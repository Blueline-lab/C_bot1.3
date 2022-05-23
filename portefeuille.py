"""""BOT WALLET"""
##Version 1
#Date de création 14.05.2021


#Modules import###
from binance.client import Client
from binance.enums import *
import datetime
import os

####Local import#####
from data_return import Data_return


class Wallet:
    def __init__(self):
        api_key = os.environ.get('API_KEY')
        api_secret = os.environ.get('SECRET_KEY')
        self.client = Client(api_key, api_secret)
        self.data_return = Data_return()

    def order(self, side, symbol, quantity, order_type, name):                            #Classic order

        try:
            self.client.create_order(side=side, symbol=symbol, quantity=quantity, type=order_type)
            
        except Exception as e:
            self.data_return.telegram_bot(f"ERROR on bot: {name}  \n{e}")
            return False

        return True



    def test_order(self, side, symbol, quantity, order_type, name):                       #Test order
            try:
                self.client.create_test_order(side=side, symbol=symbol, quantity=quantity, type=order_type)
                
            except Exception as e:
                self.data_return.telegram_bot(f"ERROR on bot: {name}  \n{e}")
                return False
 
            return True




    def pnl(self, a):
        compt = len(a)
        total = sum(a)
        a = total / compt
        b = 100
        result = a - b
        return round(result, 2)

    def pnl_transaction(self, exit, entry):
        pnl = exit / entry 
        multiply = pnl * 100 - 100
        return round(multiply, 2)
        
    def limitbuy(self, client, trade_symbol):
        avg_price = client.get_avg_price(symbol=trade_symbol)
        price = avg_price['price']
        pr = float(price)
        limit_buy = 15 / pr
        return limit_buy


    def fiat_convertion(self, TRADE_SYMBOL, WALLET, client):
        avg_price = self.client.get_avg_price(symbol=TRADE_SYMBOL)
        price = avg_price['price']
        pr = float(price)
        return WALLET / pr
