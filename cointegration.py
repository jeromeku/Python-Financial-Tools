import numpy as np
from stock import Stock

class CointegratedAssets(object):
	# The "CointegratedAssets" class implements the Engle-Granger approach
	# to cointegrated time series.

	def __init__(self,assets):
		self.price_series = np.atleast_2d([asset.asset_closing_prices() for asset in assets]).T
		self.dependent = self.price_series[:,0].T
		self.independent = self.price_series[:,1:]

		self.engle_granger = {}
		self.engle_granger["step_one"] = self.engle_granger_step_one()
		
		if self.engle_granger_cointegration_test():
			print "The Engle-Granger test reports that cointegration exists between the time-series."
		else:
			print "The Engle-Granger test reports that cointegration does not exist between the time-series."

	def __str__(self):
		return "Cointegration assets"

	def engle_granger_step_one(self):
		
		constant = np.ones((self.independent.shape[0],1))
		covariates = np.concatenate((constant,self.independent),axis = 1)

		theta = np.linalg.lstsq(covariates,self.dependent)[0]
		residuals = self.independent - np.dot(covariates,theta)

		return {"theta" : theta,"residuals" : residuals}


	def engle_granger_step_two(self):
		pass

	def engle_granger_cointegration_test(self):
		pass


assets = [Stock("MSFT"),Stock("GOOG")]
ca = CointegratedAssets(assets)

