"""""Indicators maker and strategy application"""

#14.05.2021


#Modules import###
from binance.client import Client
from binance.enums import *
import datetime
from tzlocal import get_localzone 
import numpy as np
import talib as TA
from talib import MA_Type
import os

####Local import#####
import Indicators_Analyse as ind
import get_data as dt
from data_return import Data_return
from portefeuille import Wallet
from mongo import Mongo_function



class Strategy:
    def __init__(self, name, trade_symbol,
                 trade_quantity, tp_tradequantity, stop_loss,
                 take_profit):

        self.closes = []
        self.trade_symbol = trade_symbol
       
        mongo_address = os.environ.get('MONGO_ADDRESS')
        db = os.environ.get('DB')
        db_user = os.environ.get('DB_USER')
        db_secret = os.environ.get('DB_MDP')

        self.Mongo = Mongo_function(address=mongo_address, port=27017, user=db_user, passwd=db_secret, db=db,
                                    authmechanism="SCRAM-SHA-1")
        self.name = name
        self.tz = get_localzone() # local timezone
        
        self.pnl_list = []
        self.pnl_value = 0
        self.pnl_transaction = 0
        
        self.ind = ind.Signaux()
        self.dt = dt.Data()
        self.wallet = Wallet()
        self.data_return = Data_return()

        self.trade_quantity = trade_quantity
        self.tp_trade_quantity = tp_tradequantity
        self.ORDER_TYPE = ORDER_TYPE_MARKET

        self.stop_loss = stop_loss
        self.take_profit = take_profit

        self.rsi = None
        self.rsi_period = 14
        self.rsi_up = 50
        self.rsi_down = 25
        self.last_rsi = None
        self.ema_fast_period = 12
        self.ema_slow_period = 26
        self.fast_ema = None
        self.slow_ema = None
        self.last_fastema = None
        self.last_slowema = None
        self.last_upper = None
        self.last_mid = None
        self.last_low = None
        self.emac =None

        self.upper = None
        self.mid = None
        self.low = None
        self.in_position = True
        self.a = 0
        self.c = 0
        
    
    def check_position(self):
        last_order = self.data_return.reader_last_order()
        self.in_position = last_order[0]
        self.a = float(last_order[1])

    def indicateurs_and_data(self):
        np_closes = np.array(self.closes)
        self.rsi = TA.RSI(np_closes, self.rsi_period)  # RSI maker
        self.upper, self.mid, self.low = TA.BBANDS(np_closes, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)    #Bollinger maker
        self.last_upper = self.upper[-1]
        self.last_mid = self.mid[-1]
        self.last_low = self.low[-1]
        self.last_rsi = self.rsi[-1]
        self.fast_ema = TA.EMA(np_closes, self.ema_fast_period)#Local importp_closes, self.ema_fast_period)  #  EMA fast & EMA slow
        self.slow_ema = TA.EMA(np_closes, self.ema_slow_period)
        self.last_fastema = self.fast_ema[-1]
        self.last_slowema = self.slow_ema[-1]
        self.emac = (self.last_slowema - self.last_fastema)  # EMAC

    def stratosphere(self):
        if self.in_position is False:                                              #BUY Order
            if self.closes[-1] < self.last_low and self.last_rsi < self.rsi_down:  # if rsi > rsidown et bband low < a =  close[-1]
                order_succeeded = self.wallet.test_order(SIDE_BUY, self.trade_symbol, self.trade_quantity, self.ORDER_TYPE, self.name)
                if order_succeeded:
                    self.a = self.closes[-1]
                    self.data_return.save_last_order(True, self.a)
                    
                    # Enregistrement des données
                     
                    t = datetime.datetime.now(self.tz) 
                    time = t.replace(microsecond=0)
                    self.text1 = "{} --Buy-- {} {} Price: {}\n".format(self.name, self.trade_quantity, self.trade_symbol, self.a)
                    self.data_return.telegram_bot(self.text1)
                    self.Mongo.insert0ne(f"{self.name}", {'Order': "Buy", 'Datetime': f"{time}", 'Quantity': f"{self.trade_quantity}", 'Symbol': f"{self.trade_symbol}", 'Price': f"{self.a}"})
                    


        if self.in_position: # Stop Loss
            self.c = self.closes[-1]
            if self.ind.pourcentage(self.c, self.a) < self.stop_loss:  # STOP LOSS -X%
                order_succeeded = self.wallet.test_order(SIDE_SELL, self.trade_symbol, self.trade_quantity, self.ORDER_TYPE, self.name)
                if order_succeeded:
                    self.pnl_list.append(self.ind.pourcentage(self.c, self.a))  # PNL 
                    self.pnl_value = self.wallet.pnl(self.pnl_list)
                    self.pnl_transaction = self.wallet.pnl_transaction(self.c, self.a)
                    self.data_return.save_last_order(False, 0)
                
                    # Saving datas
                     
                    t = datetime.datetime.now(self.tz)
                    time = t.replace(microsecond=0)
                    self.text2 = "{} -Sell- SL {} Price:{}\nQt :{}\n Pnl moyen : {}\n Pnl de la transaction : {}".format(self.name, self.trade_symbol, self.c, self.trade_quantity, self.pnl_value, self.pnl_transaction)
                    self.data_return.telegram_bot(self.text2)
                    self.Mongo.insert0ne(f"{self.name}", {'Order': "Sell_stop", 'Datetime': f"{time}", 'Quantity': f"{self.trade_quantity}", 'Symbol': f"{self.trade_symbol}", 'Price': f"{self.c}", 'PNL': f"{self.pnl_value}", 'PNL_transaction': f"{self.pnl_transaction}"})
                    

        if self.in_position:  # TAKE PROFIT 2%
            self.c = self.closes[-1]
            if self.ind.pourcentage(self.c, self.a) > self.take_profit:
                order_succeeded = self.wallet.test_order(SIDE_SELL, self.trade_symbol, self.trade_quantity, self.ORDER_TYPE, self.name)
                if order_succeeded:
                    self.pnl_list.append(self.ind.pourcentage(self.c, self.a))
                    self.pnl_value = self.wallet.pnl(self.pnl_list)
                    self.pnl_transaction = self.wallet.pnl_transaction(self.c, self.a)
                    self.data_return.save_last_order(False, 0)
                
                    # Saving datas
                     
                    t = datetime.datetime.now(self.tz)
                    time = t.replace(microsecond=0)
                    self.text3 = "{} --Sell-- TP {} Qt: {} at: {}\n Pnl moyen: {}\n Pnl de la transaction : {}".format(self.name, self.trade_symbol, self.trade_quantity, self.c, self.pnl_value, self.pnl_transaction)
                    self.data_return.telegram_bot(self.text3)
                    self.Mongo.insert0ne(f"{self.name}", {'Order': "Sell_Take_profit", 'Datetime': f"{time}", 'Quantity': f"{self.trade_quantity}", 'Symbol': f"{self.trade_symbol}", 'Price': f"{self.c}", 'PNL': f"{self.pnl_value}", 'PNL_transaction': f"{self.pnl_transaction}"})
                    



        if self.in_position: # SELL Order condition
            self.c = self.closes[-1]
            if self.closes[-1] > self.last_upper:
                order_succeeded = self.wallet.test_order(SIDE_SELL, self.trade_symbol, self.trade_quantity, self.ORDER_TYPE, self.name)
                if order_succeeded:
                    self.pnl_list.append(self.ind.pourcentage(self.c, self.a))  # PNL
                    self.pnl_value = self.wallet.pnl(self.pnl_list)
                    self.pnl_transaction = self.wallet.pnl_transaction(self.c, self.a)
                    self.data_return.save_last_order(False, 0)
            
                    # Saving datas
                    
                    t = datetime.datetime.now(self.tz)
                    time = t.replace(microsecond=0)
                    self.text4 = "{} --Sell-- {} Qt: {}\n Price:{}\n Pnl moyen: {}\n Pnl de la transaction : {}".format(self.name, self.trade_symbol, self.trade_quantity, self.c, self.pnl_value, self.pnl_transaction)
                    self.data_return.telegram_bot(self.text4)
                    self.Mongo.insert0ne(f"{self.name}", {'Order': "Sell", 'Datetime': f"{time}", 'Quantity': f"{self.trade_quantity}", 'Symbol': f"{self.trade_symbol}", 'Price': f"{self.c}", 'PNL': f"{self.pnl_value}", 'PNL_transaction': f"{self.pnl_transaction}"})
                    
