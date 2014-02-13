import numpy as np
from scipy.stats import norm
from stock import Stock

class CAPM:
    def __init__(self,risk_free,market):
        # 
        self.risk_free = Stock(risk_free["ticker"],risk_free["date_range"])
        self.market = Stock(market["ticker"],market["date_range"])

        # 
        self.alpha = {}
        self.beta = {}
        self.critical_value = norm.ppf(.975)

    def asset_regression(self,asset_dictionary):
        asset = Stock(asset_dictionary["ticker"],asset_dictionary["date_range"])
        market_premium = np.atleast_2d(self.market.statistics["returns"] - self.risk_free.statistics["returns"]).T
        asset_premium = np.atleast_2d(asset.statistics["returns"] - self.risk_free.statistics["returns"]).T
        
        constant = np.ones((market_premium.shape[0],1))
        covariates = np.concatenate((constant,market_premium),axis = 1)
      
        # Solve the capital asset pricing model in the least-squares sense. In
        # particular, wel solve the following linear model for parameters theta_0
        # and theta_1:
        #     R_{j,t} - mu_{f,t} = theta_0 + theta_1 * (R_{M,t} - mu_{f,t}) + e_{j,t}
        # Where R_{j,t} is the asset premium of the jth asset, mu_{f,t} is the 
        # risk-free rate, R_{M,t} is the market premium, and e_{j,t} represents an
        # error term. Refer to page 435 in the Statistics and Data Analysis for 
        # Financial Engineering.
        theta = np.linalg.lstsq(covariates,asset_premium)[0]
        residuals = asset_premium - np.dot(covariates,theta)

        # The rank of the covariates matrix is presumably two, and it is for that 
        # reason that we subtract two in the denominator.
        s_squared = np.sum(residuals * residuals) / (market_premium.shape[0] - 2)
        
        standard_errors = np.sqrt(s_squared * np.linalg.inv(np.dot(covariates.T,covariates)))
        self.alpha["value"] = theta[0]
        self.alpha["confidence_interval"] = theta[0] + standard_errors[0,0] * self.critical_value * np.array([-1,1])

        self.beta["value"] = theta[1]
        self.beta["confidence_interval"] = theta[1] + standard_errors[1,1] * self.critical_value * np.array([-1,1])
        

    
date_range = {"start" : "2012-01-03", "end" : "2013-01-08"}
tickers = ("^IRX","^GSPC","GOOG")
capm = CAPM({"ticker" : tickers[0],"date_range" : date_range},{"ticker" : tickers[1],"date_range" : date_range})
capm.asset_regression({"ticker" : tickers[2],"date_range" : date_range})


