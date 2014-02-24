
import numpy as np
from stock import Stock
from scipy.special import gamma

class JumpStatistics(object):
	def __init__(self,stock):
		self.stock = stock

class BarndorffNielsen(JumpStatistics):
	# An implementation of the Barnforff-Nielsen test statistic used for detecting "jumps"
	# (or "suprises") in stock price data. The mathematics for this test statistic can be
	# found at the following two resources:
	#
	# Michael William Schwert. 2008. "Problems in the Application of Jump Detection Tests 
	# to Stock Price Data". Duke University.
	#
	# "Some Like it Smooth, and Some Like it Rough: Untangling Continuous and Jump 
	# Components in Measuring, Modeling, and Forecasting Asset Return Volatility".
	# Torben G. Andersen, Tim Bollerslev and Francis X. Diebold. September 2003.

	def __init__(self,stock):
		super(BarndorffNielsen,self).__init__(stock)
		self.n = len(self.stock.statistics["log_returns"])
		self.realized_variance = self.calculate_realized_variance()
		self.bipower_variance = self.calculate_bipower_variance()

		self.relative_jump = np.float(self.realized_variance - self.bipower_variance) / self.realized_variance
		self.tripower_quarticity = self.calculate_tripower_quarticity()

		self.statistic = self.barndorff_nielsen_statistic()

	def calculate_realized_variance(self):
		log_returns = self.stock.statistics["log_returns"]
		variance = np.sum(np.power(log_returns,2))
		return variance

	def calculate_bipower_variance(self):
		n = self.n
		log_returns = np.absolute(self.stock.statistics["log_returns"])
		
		variance = (np.pi / 2.0) * (np.float(n) / (n - 1.0)) * np.sum(log_returns[1:] * log_returns[:-1])
		return variance

	def calculate_tripower_quarticity(self):
		n = self.n

		# Notice that the absolute value of the log returns is calculated in this step. This is to 
		# prevent numerical nan's from being produced. This also seems to be consistent with the 
		# notation specified by Michael Schwert and Torben G. Andersen et al.
		log_returns = np.absolute(self.stock.statistics["log_returns"])
		mu = np.power(np.power(2.0,2.0 / 3) * gamma(7.0 / 6.0) * np.power(gamma(1.0 / 2.0),-1),-3)

		tripower = np.sum(np.power(log_returns[2:],4.0 / 3) * np.power(log_returns[1:-1],4.0 / 3) * np.power(log_returns[:-2],4.0 / 3))
		quarticity = n * mu * (np.float(n) / (n - 2.0)) * tripower
		return quarticity

	def barndorff_nielsen_statistic(self):
		n = self.n
		pi = np.pi
		relative_jump = self.relative_jump
		tripower = self.tripower_quarticity
		bipower = self.bipower_variance

		statistic = relative_jump / np.sqrt(((pi / 2) ** 2 + pi - 5) * (1.0 / n) * max(1,tripower / (bipower ** 2)))

		return statistic

stock = Stock("MSFT")
stock.display_price()

bn = BarndorffNielsen(stock)
print "The Barndorff-Nielsen statistic: %.2f\n" % bn.statistic
