"""""MATH methods  """



#Modules import###
from binance.client import Client
from binance.enums import *
import talib as TA
import datetime

####Local import#####
import readme

class Signaux:
    def __init__(self):
        self.x = 0

    def pourcentage(self, prix_comparaison, prix_achat):
        calc = (prix_comparaison * 100 / prix_achat)
        return calc

    def risky(self, portfolio, trade_quantity):                 # Trade quantity definition 
        risk = (portfolio / 100) * trade_quantity
        return round(risk, 3)
