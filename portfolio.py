
import numpy as np
from stock import Stock
from pprint import pprint
from cvxopt import matrix, solvers

class Portfolio:
    def __init__(self,assets):
        self.assets = [Stock(stock["ticker"],stock["date_range"]) if type(stock) is dict else Stock(stock) for stock in assets]
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

    def optimize_portfolio(self):
        P = 2 * self.statistics["covariance"]
        n = self.n

        n_expected_returns = 300
        expected_returns = np.linspace(.05,.14,n_expected_returns)
        standard_deviations = np.nan((n_expected_returns,1))
        weights = np.nan((n_expected_returns,n))
        
        
        

        


portfolio = Portfolio(["MSFT","GOOG","IBM"])
# for asset in portfolio.assets:
#     print asset


