# Stock.py: A Python class representing a stock as downloaded from Yahoo
#       Finance! A stock object is instantiated by specifying a ticker
#       and, optionally, a start and end date in the format "YYYY/MM/DD".
#
# The stock object is completely specified by its ticker and a pair of
# dates across which is aggregates financial data. The stock class then
# computes the returns, the expected return, and the gross return based on
# daily price information. 
#
# The stock class supports operations to calculate the value-at-risk, and
# utility functions to graph the daily prices.
#
# The following is an example usage of the stock class to download
# historical stock information from Google over a specified period:
#       date_range = {"start" : "2012-01-03", "end" : "2013-01-08"}
#       ticker = "GOOG"
#       stock = Stock(ticker,date_range)
#       stock.display_price()
#       print stock

import numpy as np
from urllib2 import Request, urlopen
from urllib import urlencode
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
from scipy import stats

class Stock(object):
    def __init__(self,ticker,date_range = None,position = None):
        self.ticker = ticker
        self.position = position if position is not None else None

        if date_range is not None:
            self.date_range = date_range
        else:
            # If there was no specified time interval, presume that the
            # user intends to download historical price data from the 
            # past year. Notice that the end of the time interval is 
            # today, while the start is one year in the past.
            end = datetime.datetime.now().strftime("%Y-%m-%d")
            start = (datetime.datetime.now() - datetime.timedelta(days = 365)).strftime("%Y-%m-%d")
            self.date_range = {"start" : start, "end" : end}

        try:
            self.profile = self.yahoo_download_daily()
            self.statistics = self.calculate_statistics()
        except:
            print "Invalid ticker symbol specified or else there was not an internet connection available."
        
        
    def __str__(self):
        print_string = "Ticker: " + self.ticker + "\n"
        print_string += "Time series: From " + self.date_range["start"] + " to " + self.date_range["end"] + "\n\n"
        print_string += "Current performance:\n"
        print_string += "Date\t\tOpen\tHigh\tLow\tClose\tVolume\t\tAdjusted Close\n"

        current_date = sorted(self.profile.keys())[-1]
        current_performance = self.profile[current_date]
     
        print_string += "%s\t%.2f\t%.2f\t%.2f\t%.2f\t%7e\t%.2f\n\n" % (current_date, 
                                                                       float(current_performance["Open"]), 
                                                                       float(current_performance["High"]), 
                                                                       float(current_performance["Low"]), 
                                                                       float(current_performance["Close"]), 
                                                                       int(current_performance["Volume"]), 
                                                                       float(current_performance["Adj Close"])
                                                                       )
        print_string += "Expected return: %.4f" % self.statistics["expected_return"]
        return print_string

    def calculate_statistics(self):
        statistics = {}
        closing_prices = np.array(
            [np.float(self.profile[day]["Close"]) for day in self.profile.keys()]
            )

        # Occasionally, values of zero are obtained as an asset price. In all likelihood, this
        # value is rubbish and cannot be trusted, as it implies that the asset has no value. 
        # In these cases, we replace the reported asset price by the mean of all asset prices.
        closing_prices[closing_prices == 0] = np.mean(closing_prices)

        # Calculate the daily returns on the stock option. These calculation is
        # defined by the formula:
        #     R_t = (P_t / P_{t - 1}) - 1
        # Refer to page five of Statistics and Data Analysis for Financial 
        # Engineering. For the expected return, we simply take the mean value of
        # the calculated daily returns.
        statistics["returns"] = closing_prices[1:] / closing_prices[:-1] - 1
        statistics["log_returns"] = np.log(statistics["returns"] + 1)

        # Multiply the average daily return by the length of the time series in order to
        # obtain the expected return over the entire period.
        statistics["expected_daily_return"] = np.mean(statistics["returns"])
        statistics["expected_return"] = statistics["expected_daily_return"] * len(statistics["returns"])
        
        return statistics

    def calculate_parametric_risk(self,alpha,position = None):

        if position is None and self.position is not None:
            position = self.position
        elif position is None and self.position is None:
            print "Either specify a position for the stock object or provide one as an input parameter."
            return np.nan

        returns = self.statistics["returns"]
        
        # Fit a t-distribution to the daily returns data using the 
        # method of maximum likelihood estimation.
        tdof, tloc, tscale = stats.t.fit(returns)
        quantile = stats.t.ppf(alpha, tdof, tloc, tscale)

        # Assuming that returns are i.i.d. with a t-distribution, it
        # can be shown that value-at-risk is calculated as:
        #      VaR_t(alpha) = -S * {mu + q_{alpha}(nu) * lambda}
        # Is this formula, S refers to the size of the position. The 
        # parameters mu, lambda, and scale are the estimated mean, 
        # scale, and degrees of freedom of the sample returns. The
        # parameter q_{alpha}(nu) is the alpha-quantile of a 
        # t-distribution with nu degrees of freedom. Refer to page 
        # 510 in Statistics and Data Analysis for Financial 
        # Engineering.
        value_at_risk = -position * (tloc + quantile * tscale)
        return value_at_risk

    def asset_closing_prices(self,array = False):
        sorted_dates = sorted(self.profile.keys())
        closing_prices = [np.float(self.profile[day]["Close"]) for day in sorted_dates]
        return np.array(closing_prices) if array else closing_prices

    def display_price(self):
        sorted_dates = sorted(self.profile.keys())
        plt.plot_date([mdates.strpdate2num('%Y-%m-%d')(day) for day in sorted_dates],
                      self.asset_closing_prices(),
                      fmt="k-o")
        plt.title(self.ticker + " Closing Prices")
        plt.ylabel("Daily Prices")
        plt.xlabel("Historical Dates")
        plt.grid(True)
        plt.show()

    def yahoo_download_daily(self):
        # Stocks are defined over a range of time, with a beginning and an end 
        # date. We use these dates to query yahoo Finance! for the relevant 
        # historical price data.
        start_date = self.date_range["start"]
        end_date = self.date_range["end"]


        # Encode the query parameters to be used in the GET request to yahoo 
        # Finance!
        yahoo = {}
        yahoo["parameters"] = urlencode({
                "s": self.ticker,
                "a": int(start_date[5:7]) - 1,
                "b": int(start_date[8:10]),
                "c": int(start_date[0:4]),
                "d": int(end_date[5:7]) - 1,
                "e": int(end_date[8:10]),
                "f": int(end_date[0:4]),
                "g": "d",
                "ignore": ".csv",
                })
        yahoo["url"] = "http://ichart.yahoo.com/table.csv?%s" % yahoo["parameters"]
        yahoo["query"] = Request(yahoo["url"])
        yahoo["response"] = urlopen(yahoo["query"])
        yahoo["content"] = str(yahoo["response"].read().decode("utf-8").strip())

        daily_data = yahoo["content"].splitlines()
        historical_data = {}
        keys = daily_data[0].split(",")

        # For every day, create an entry in a dictionary of dates with the trading
        # volume, the closing price, the opening price, the high and the low price, 
        # and the adjusted closing price. The data structure representing the 
        # historical price data is as follows:
        #     'YYYY-MM-DD': {'Adj Close': 'float',
        #                    'Close': 'float',
        #                    'High': 'float',
        #                    'Low': 'float',
        #                    'Open': 'float',
        #                    'Volume': 'int'
        #                   }
        for day in daily_data[1:]:
            day_data = day.split(",")
            date = day_data[0]
            historical_data[date] = {
                keys[1]: day_data[1],
                keys[2]: day_data[2],
                keys[3]: day_data[3],
                keys[4]: day_data[4],
                keys[5]: day_data[5],
                keys[6]: day_data[6]
                }
        return historical_data

