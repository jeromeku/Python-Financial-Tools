import numpy as np
from scipy import stats
from pprint import pprint

# Autoregressive process
class AR(object):
	def __init__(self,time_series):
		self.time_series = time_series
		self.p = self.calculate_times_series_order()
		self.regression = self.time_series_regression()

	def time_series_regression(self):
		regression = {}
		m = self.p + 1
		n = len(self.time_series) - self.p
		X = np.zeros((n,m))
		targets = self.time_series[self.p:]
		for i in range(n):
			X[i,0] = 1.0
			for j in range(1,m):
				X[i,j] = self.time_series[i - self.p + j]
		coefficients = np.linalg.lstsq(X,targets)[0]
		phi = coefficients[1:]
		mu = coefficients[0] / (1 - np.sum(phi))

		regression["mu"] = mu[0]
		regression["phi"] = phi[0]
		return regress

	def calculate_times_series_order(self):
		# For the moment, naively assume that the order of the time
		# series is one. Later, it would be advantageous to implement
		# a automated method for selecting the order.
		return 1

	def autocorrelation_function(self):
		pass

	def partial_autocorrelation_function(self):
		pass

	def calculate_ljung_box_statistic(self):
		pass

if True:
	phi = .5
	n = 1000
	time_series = np.zeros((n,1))
	for i in range(1,n):
		time_series[i] = phi * time_series[i-1] + np.random.normal()

	ar = AR(time_series)
	pprint(ar.regression)
