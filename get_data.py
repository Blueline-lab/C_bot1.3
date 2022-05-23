"""Get_data from api"""
##14.05.2021


#Modules import###

import websocket


class Data:

    def __init__(self):
        self.socket = ""
        self.data = {}
        self.close = ""
        self.candle_is_closed = bool



    def clean_datas(self, array, valeur_inutile):
        if len(array) > valeur_inutile:
            del array[0]  # Nettoie les array supprime les valeurs inutiles

    def get_message(self, SOCKET, on_message, on_open, on_close):
        ws = websocket.WebSocketApp(SOCKET,
                                    on_message=on_message,  # Message generator
                                    on_open=on_open,
                                    on_close=on_close,)
        self.ws = ws
        self.ws.run_forever()
