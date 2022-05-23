"""Mongodb insertion for Cbot1.2 06.07.2021"""

#Import
from pymongo import MongoClient
import datetime as dt

#Mainclass
class Mongo_function:
    def __init__(self, address, port, user, passwd, db, authmechanism):
        self.address = address
        self.port = port
        self.db = db
        self.user = user
        self.passwd = passwd
        self.authmecanism = authmechanism
        self.a = self.connection()
        self.validconnection()
        self.transfert = None
        
    def connection(self):
        self.client = MongoClient(self.address,
        self.port,
        username=self.user,
        password=self.passwd,
        authSource=self.db,
        authMechanism=self.authmecanism)
        
        self.db = self.client[f"{self.db}"]
        
        return True

    def validconnection(self):
        if self.a is not True:
            print("ERROR, verify entry values for mongod connection, "
                   "or look if the mongod server running well")
   
    def insert0ne(self, collection, value):
        insertion = self.db[f"{collection}"].insert_one(value)



