from portfolio import Portfolio
from stock import Stock
from pprint import pprint
from dateutil import rrule, parser

class Backtesting(object):
	def __init__(self,portfolio,strategies,time_interval = None,transaction_cost = 0.0):
		self.portfolio = portfolio

		# Create an array of strategies to test. For the moment it is assumed that
		# there is a single strategy for each asset in the portfolio, or else there
		# is only a single strategy. 
		self.strategies = [strategies] if type(strategies) is not list else strategies
		dates = time_interval if time_interval is not None else self.portfolio.assets[0].date_range

		self.time_interval = [date.strftime("%Y-%m-%d") for date in list(rrule.rrule(rrule.DAILY,
			dtstart = parser.parse(dates["start"]),
			until = parser.parse(dates["end"])))]

		self.results = self.test_strategies_in_time_interval()

	def __str__(self):
		print_string = ""
		return print_string

	def test_strategies_in_time_interval(self):
		results = {}
		n_assets = self.portfolio.n

		# 
		position = ["Buy"] * n_assets

		if n_assets > 1 and n_assets != len(self.strategies):
			print "The number of strategies must equal the number of assets in the portfolio."
			return None

		for date in self.time_interval:
			for i in range(n_assets):
				asset = self.portfolio.assets[i]
				strategy = self.strategies[0] if n_assets == 1 else self.strategies[i]

				if date in asset.profile.keys():
					position[i] = strategy(date,asset,position[i])
					print position[i]




def strategy(date,asset,position):
	# For this simple trading strategy, we will choose to buy stock
	# of WNC when the price is below $9.50, and we will choose to
	# sell when the price rises above $10.50. Because we have the 
	# benefit of looking backwards, this strategy should to be very
	# profitable over the specified time interval.

	
	if float(asset.profile[date]["Close"]) < 9.5:
		decision = "Buy"
	elif float(asset.profile[date]["Close"]) > 10.5:
		decision = "Sell"
	else:
		decision = "Hold"

	return decision if decision != position else "Hold"



portfolio = Portfolio([{"ticker" : "WNC","date_range" : {"start" : "2013-02-13","end" : "2013-08-13"}}])
if False:
	portfolio.assets[0].display_price()

backtest = Backtesting(portfolio,strategy)

# print portfolio
# print backtest
