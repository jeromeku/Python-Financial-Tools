# capm.py: A Python class representing the CAPM model given
#       the risk free rate and market returns.  The object
#       can be instantiated given Stock objects representing
#		the risk free and market data or their respective
#       ticker symbols.
#
# Calling asset_regression with a stock object or asset
# dictionary as a parameter will calculate and store the CAPM
# model's alpha, beta, and associated confidence intervals.
#
# The folowing is an example usage of the CAPM class to
# calculate the alpha and beta of the stock given an asset
# dictionary.
#       date_range = {"start" : "2012-01-03", "end" : "2013-01-08"}
#       tickers = ("^IRX","^GSPC","GOOG")
#       capm = CAPM({"ticker" : tickers[0],"date_range" : date_range},
#                   {"ticker" : tickers[1],"date_range" : date_range})
#       capm.asset_regression({"ticker" : tickers[2],"date_range" : date_range})

import numpy as np
from scipy.stats import norm
from stock import Stock

class CAPM(object):
    def __init__(self,risk_free,market,alpha = .05):

        self.risk_free = Stock(risk_free["ticker"],risk_free["date_range"]) if type(risk_free) is dict else Stock(risk_free)
        self.market = Stock(market["ticker"],market["date_range"]) if type(market) is dict else Stock(market)

        self.alpha, self.beta = {}, {}
        self.critical_value = norm.ppf(1 - alpha / 2.0)

    def __str__(self):
        if len(self.alpha.keys()) and len(self.beta.keys()):
            alpha = self.alpha
            beta = self.beta
        else:
            return "The alpha and beta coefficients were not initialized. Please call the asset regression method before continuing."


        print_string = "Capital Asset Pricing Model:\n\tCritical value: %.2f\n" % self.critical_value
        print_string += "\t\t\tValue\t\tLower Bound\tUpper Bound\n"
        print_string += "\talpha:\t\t%.4f\t\t%.4f\t\t%.4f\n" % (alpha["value"],alpha["confidence_interval"][0],
                                                                    alpha["confidence_interval"][1])
        print_string += "\tbeta:\t\t%.4f\t\t%.4f\t\t%.4f\n\n" % (beta["value"],beta["confidence_interval"][0],
                                                                    beta["confidence_interval"][1])
        
        if alpha["confidence_interval"][0] > 0:
            print_string += "\tThe CAPM reports that the security is overpriced. Asset returns are too large on average."
        elif alpha["confidence_interval"][1] < 0:
            print_string += "\tThe CAPM reports that the security is underpriced. Asset returns are too small on average."
        else:
            print_string += "\tThere CAPM reports that the security is appropriately priced."

        return print_string

    def asset_regression(self,asset_data):

        alpha, beta = {}, {}

        asset = Stock(asset_data["ticker"],asset_data["date_range"]) if type(asset_data) is dict else Stock(asset_data)
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
        alpha["value"] = theta[0]
        alpha["confidence_interval"] = theta[0] + standard_errors[0,0] * self.critical_value * np.array([-1,1])

        beta["value"] = theta[1]
        beta["confidence_interval"] = theta[1] + standard_errors[1,1] * self.critical_value * np.array([-1,1])

        self.alpha = alpha
        self.beta = beta

date_range = {"start" : "2012-01-03", "end" : "2013-01-08"}
tickers = ("^IRX","^GSPC","GOOG")
capm = CAPM({"ticker" : tickers[0],"date_range" : date_range},
    {"ticker" : tickers[1],"date_range" : date_range})
capm.asset_regression({"ticker" : tickers[2],"date_range" : date_range})

print capm
