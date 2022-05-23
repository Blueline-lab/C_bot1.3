"""Return infos from Cbot"""
##14.05.2021


#Modules import###

import requests
import csv
import os

####Local imports#####





########################



class Data_return:
    def __init__(self):
        self.hist = ""

    def telegram_bot(self, bot_message):
        bot_token = os.environ.get('BOT_ID')
        bot_chatID = os.environ.get('CHAT_ID')
        send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + str(bot_message)

        response = requests.get(send_text)



    def save_last_order(self, value, a):
        with open('buy_out_connection.csv', 'w', newline='') as s:
            fieldnames = ['in_position', 'a']
            write = csv.DictWriter(s, fieldnames=fieldnames)
            write.writeheader()
            write.writerow({'in_position':value, 'a':a})

    def reader_last_order(self):
        with open('buy_out_connection.csv', 'r') as r:
            read = csv.DictReader(r)
            for i in read:
                if i['in_position'] == "True":
                    true_position = []
                    true_position.append(bool(True))
                    true_position.append(float(i['a']))
                    return true_position
                else:
                    false_position = []
                    false_position.append(bool(False))
                    false_position.append(float(0))
                    return false_position
                    
    def saveData(self, data):
        with open('saved.txt', 'a') as s:
            s.write(str(data))


    
