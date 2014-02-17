
import numpy as np
from scipy import stats

class Option(object):
    def __init__(self):
        self.strike_price = np.float(50)
        self.tau = .5
        self.risk_free = .03
        self.deviation = .45
        self.stock_price = np.float(55)
        

class EuropeanCall(Option):
    def evaluate_black_scholes(self):
        S = self.stock_price
        X = self.strike_price
        r = self.risk_free
        sigma = self.deviation
        tau = self.tau

        d_1 = (np.log(S / X) + (r + (sigma ** 2) / 2) * tau) / (sigma * np.sqrt(tau))
        d_2 = d_1 - sigma * np.sqrt(tau)

        value = S * stats.norm.cdf(d_1) - X * np.exp(-r * tau) * stats.norm.cdf(d_2)
        return value

european_call = EuropeanCall()
print european_call.evaluate_black_scholes()
