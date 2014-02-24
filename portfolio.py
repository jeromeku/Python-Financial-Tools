# portfolio.py  This class represents a portfolio of stocks. It supports optimization
#      of assets via a quadratic program.
#
# The following is an example of how the portfolio class may be used to represent a
# portfolio of assets representing major technology companies:
#       portfolio = Portfolio(["MSFT","GOOG","IBM"])
#       print "The value at risk: %.2f" % portfolio.calculate_parametric_risk(.05,1000)
#       print "The expected shortfall: %.2f" % portfolio.calculate_parametric_risk(.05,1000,True)

import numpy as np
from stock import Stock
from cvxopt import matrix
from cvxopt.blas import dot
from cvxopt import solvers
from scipy import stats

from pprint import pprint

solvers.options["show_progress"] = False


class Portfolio(object):
    def __init__(self,assets,risk_free = None,position = None):
        # The position refers to the dollar amount invested into this particular
        # portfolio. The position can be allocated so that it corresponds to the
        # portfolio with the maximum sharpe's ratio, or to the portfolio with the
        # minimum risk.
        self.position = position if position is not None else None

        self.assets = [Stock(stock["ticker"],stock["date_range"]) if type(stock) is dict else Stock(stock) for stock in assets]

        if risk_free is not None:
            self.risk_free = Stock(risk_free["ticker"],risk_free["date_range"]) if type(risk_free) is dict else Stock(risk_free)
        else:
            self.risk_free = Stock("^IRX")

        self.n = len(self.assets)
        self.statistics = self.calculate_statistics()
        self.optimization = self.optimize_portfolio()
        self.returns = self.calculate_portfolio_returns()

    def __str__(self):
        print_string = "Assets in portfolio: [" + " ".join([asset.ticker for asset in self.assets]) + "]\n\n"
        for asset in self.assets:
            print_string += asset.__str__() + "\n\n"
        print_string += "The weights for each asset in the portfolio:\n"
        for i in range(self.n):
            print_string += "\t" + self.assets[i].ticker + "\t: " + str(self.optimization["max_sharpe_weights"][i][0]) + "\n"
        print_string += "\nExpected return: %.4f" % self.returns

        return print_string

    def calculate_portfolio_returns(self):
        returns = 0.0
        for i in range(self.n):
            returns += self.assets[i].statistics["expected_return"] * self.optimization["max_sharpe_weights"][i][0]
        return returns


    def calculate_statistics(self):
        statistics = {}
        returns = np.zeros((len(self.assets[0].statistics["returns"]),self.n))

        for i in range(self.n):
            returns[:,i] = self.assets[i].statistics["returns"]

        statistics["expected_asset_returns"] = np.array([asset.statistics["expected_return"] for asset in self.assets])
        statistics["covariance"] = np.cov(returns,rowvar = 0)

        # Due to the behavior of the numpy "diag" function, scalar inputs will fail and 
        # produce an error. This instance occurs when there is only a single asset in the
        # portfolio. In this case, simply exclude the call to "diag" and calculate the 
        # standard deviation and the square root of a scalar covariance "matrix".
        if statistics["covariance"].shape == ():
            statistics["standard_deviation"] = np.sqrt(statistics["covariance"])
        else:
            statistics["standard_deviation"] = np.sqrt(np.diag(statistics["covariance"]))
        return statistics

    def calculate_parametric_risk(self,alpha,expected_shortfall = False,position = None):

        if position is None and self.position is not None:
            position = self.position
        elif position is None and self.position is None:
            print "Either specify a position for the portfolio object or provide one as an input parameter."
            return np.nan

        mu = self.statistics["expected_asset_returns"]
        S = self.statistics["covariance"]
        w = self.optimization["max_sharpe_weights"]
        portfolio_mu = np.dot(mu,w)
        portfolio_sigma = np.sqrt(np.dot(np.dot(w.T,S),w))[0]

        quantile = stats.norm.ppf(alpha)

        if expected_shortfall:
            risk = position * (-portfolio_mu + portfolio_sigma * (stats.norm.pdf(quantile) / alpha))
        else:
            risk = -position * (portfolio_mu + quantile * portfolio_sigma)

        return risk


    def optimize_kelly_criterion(self):
        # This code attempts to reproduce the optimization routine proposed by 
        # Vasily Nekrasov using the Kelly criterion. In particular, this code 
        # uses as reference the following work:
        #
        # Nekrasov, Vasily. 2013. "Kelly Criterion for Multivariate Portfolios: 
        # A Model-Free Approach".

        kelly_optimization = {}

        n = self.n
        r = self.risk_free.statistics["expected_daily_return"]
        S = matrix(1.0 / ((1 + r) ** 2) * self.statistics["covariance"])
        r_assets = matrix([asset.statistics["expected_daily_return"] for asset in self.assets])

        q = matrix(1.0 / (1 + r) * (r_assets - r))
        G, h, A, b = self.optimization_constraint_matrices()

        # Notice that the "linear" term in the quadratic optimization formulation is made 
        # negative. This is because Nekrasov maximizes the function, whereas CXVOPT is forced
        # to minimize. By making the linear term negative, we arrive at an equivalent 
        # formulation.
        portfolio_weights = solvers.qp(S,-q,G,h,A,b)["x"]
        kelly_optimization["weights"] = np.array([portfolio_weights[i] for i in range(n)])
        return kelly_optimization


    def optimize_portfolio(self):
        optimization = {}

        n = self.n
        S = matrix(2 * self.statistics["covariance"])
        expected_returns = matrix(self.statistics["expected_asset_returns"])
        G, h, A, b = self.optimization_constraint_matrices()

        mu_array = [10**(5.0*t/100-1.0) for t in range(100)]

        portfolio_weights = [solvers.qp(mu*S,-expected_returns,G,h,A,b)["x"] for mu in mu_array]
        returns = [dot(expected_returns,w) for w in portfolio_weights]
        risk = [np.sqrt(dot(w,S*w)) for w in portfolio_weights]

        mu_free = self.risk_free.statistics["returns"][-1]
        sharpe_ratio = (returns - mu_free) / risk
        max_sharpe_index = sharpe_ratio == max(sharpe_ratio)
        min_variance_index = risk == min(risk)

        optimization["returns"] = returns
        optimization["risk"] = risk

        # If possible, try to decrease the number of for loops used to extract the
        # optimal weights of the portfolio. At the time of writing this, it seems
        # that the matrix data structure is somewhat bizarre. Therefore, in order to
        # generate the desired numpy array object, so many for loops turned out to
        # be necessary.
        max_sharpe_weights = [portfolio_weights[i] for i in range(len(portfolio_weights)) if max_sharpe_index[i]]
        min_variance_weights = [portfolio_weights[i] for i in range(len(portfolio_weights)) if min_variance_index[i]]
        optimization["max_sharpe_weights"] = np.zeros((n,1))
        optimization["min_variance_weights"] = np.zeros((n,1))

        for i in range(len(max_sharpe_weights[0])):
            optimization["max_sharpe_weights"][i] = max_sharpe_weights[0][i]
        for i in range(len(min_variance_weights[0])):
            optimization["min_variance_weights"][i] = min_variance_weights[0][i]

        return optimization

    def optimization_constraint_matrices(self):
        n = self.n
        G = matrix(0.0, (n,n))
        G[::n+1] = -1.0
        h = matrix(0.0, (n,1))
        A = matrix(1.0, (1,n))
        b = matrix(1.0)

        return G, h, A, b

portfolio = Portfolio(["MSFT","GOOG","IBM"])
print portfolio

pprint(portfolio.optimize_kelly_criterion())

