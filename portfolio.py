# portfolio.py  This class represents a portfolio of stocks. It supports optimization
#      of assets via a quadratic program.

import numpy as np
from stock import Stock
from cvxopt import matrix
from cvxopt.blas import dot
from cvxopt import solvers
from scipy import stats

class Portfolio:
    def __init__(self,assets,risk_free = None):
        self.assets = [Stock(stock["ticker"],stock["date_range"]) if type(stock) is dict else Stock(stock) for stock in assets]

        if risk_free is not None:
            self.risk_free = Stock(risk_free["ticker"],risk_free["date_range"]) if type(risk_free) is dict else Stock(risk_free)
        else:
            self.risk_free = Stock("^IRX")

        self.n = len(self.assets)
        self.statistics = self.calculate_statistics()
        self.optimization = self.optimize_portfolio()

    def calculate_statistics(self):
        statistics = {}
        returns = np.zeros((len(self.assets[0].statistics["returns"]),self.n))

        for i in range(self.n):
            returns[:,i] = self.assets[i].statistics["returns"]
        statistics["mean"] = np.mean(returns,axis = 0)
        statistics["covariance"] = np.cov(returns,rowvar = 0)
        statistics["standard_deviation"] = np.sqrt(np.diag(statistics["covariance"]))
        return statistics

    def calculate_parametric_risk(self,alpha,position,expected_shortfall = False):
        mu = self.statistics["mean"]
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


    def optimize_portfolio(self):
        optimization = {}

        n = self.n
        S = matrix(2 * self.statistics["covariance"])
        pbar = matrix(self.statistics["mean"])
        G = matrix(0.0, (n,n))
        G[::n+1] = -1.0
        h = matrix(0.0, (n,1))
        A = matrix(1.0, (1,n))
        b = matrix(1.0)

        mu_array = [10**(5.0*t/100-1.0) for t in range(100)]

        solvers.options['show_progress'] = False

        portfolio_weights = [solvers.qp(mu*S,-pbar,G,h,A,b)['x'] for mu in mu_array]
        returns = [dot(pbar,w) for w in portfolio_weights]
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

portfolio = Portfolio(["MSFT","GOOG","IBM"])
print "The value at risk: %.2f" % portfolio.calculate_parametric_risk(.05,1000)
print "The expected shortfall: %.2f" % portfolio.calculate_parametric_risk(.05,1000,True)
