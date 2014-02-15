<<<<<<< HEAD
# portfolio.py  This class represents a portfolio of stocks. It supports optimization
#      of assets via a quadratic program.
=======
# portfolio.py  This class represents a portfolio of stocks
>>>>>>> 159c9a232c60d0c2bfbc333a73752717557e19df


import numpy as np
from stock import Stock
from pprint import pprint
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

    def calculate_parametric_value_at_risk(self,alpha,position):
        mu = self.statistics["mean"]
        S = self.statistics["covariance"]
        w = self.optimization["weights"]
        portfolio_mu = np.dot(mu,w)
        portfolio_sigma = np.sqrt(np.dot(np.dot(w.T,S),w))[0]

        quantile = stats.norm.ppf(1 - alpha)
        value_at_risk = -position * (portfolio_mu + quantile * portfolio_sigma)

        return value_at_risk

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
        sharpe_index = sharpe_ratio == max(sharpe_ratio)

        optimization["returns"] = returns
        optimization["risk"] = risk
<<<<<<< HEAD

        # If possible, try to decrease the number of for loops used to extract the
        # optimal weights of the portfolio. At the time of writing this, it seems
        # that the matrix data structure is somewhat bizarre. Therefore, in order to 
        # generate the desired numpy array object, so many for loops turned out to 
        # be necessary.
        optimization_weights = [portfolio_weights[i] for i in range(len(portfolio_weights)) if sharpe_index[i]]
        optimization["weights"] = np.zeros((n,1))
        
        for i in range(len(optimization_weights[0])):
            optimization["weights"][i] = optimization_weights[0][i]
        
        return optimization
                

portfolio = Portfolio(["MSFT","GOOG","IBM"])
=======
>>>>>>> db0fb24ec760dc652b66cc861393d013c1e430cc

        # If possible, try to decrease the number of for loops used to extract the
        # optimal weights of the portfolio. At the time of writing this, it seems
        # that the matrix data structure is somewhat bizarre. Therefore, in order to
        # generate the desired numpy array object, so many for loops turned out to
        # be necessary.
        optimization_weights = [portfolio_weights[i] for i in range(len(portfolio_weights)) if sharpe_index[i]]
        optimization["weights"] = np.zeros((n,1))

        for i in range(len(optimization_weights[0])):
            optimization["weights"][i] = optimization_weights[0][i]

        return optimization


portfolio = Portfolio(["MSFT","GOOG","IBM"])
portfolio.calculate_parametric_value_at_risk(.05,1000)
