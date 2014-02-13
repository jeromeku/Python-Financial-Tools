
import numpy as np
from stock import Stock

class Portfolio:
    def __init__(self,assets):
        self.assets = [Stock(stock["ticker"],stock["date_range"]) for stock in assets]
        self.n = len(self.assets)
        self.optimization = {}
        self.statistics = {}
        
    
        

portfolio = Portfolio()
print portfolio
