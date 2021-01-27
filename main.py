from coinmarketcapapi import CoinMarketCapAPI, CoinMarketCapAPIError

import time
import pickle
import telebot
from colorama import Fore

TOKEN = '1628210405:AAGnKOWAWI9ZJkyEWVtglCJe2WaGBoriBTk' # Ponemos nuestro Token generado con el @BotFather
tb = telebot.TeleBot(TOKEN) # 

api_cmc = CoinMarketCapAPI('e1cf7bb2-42d4-4508-a55d-c32310c460be')


price_list_15sec = []
posiciones_abiertas = []
posiciones_cerradas = []

from datetime import datetime


class Posicion:
    def __init__(self):
        self.precio_compra = 0
        self.precio_venta = 0

def output_current_time():
    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)

def porcentaje(x, y): #NEW NUM, OLD NUM
    increase = x - y
    z = increase/y
    perc = z*100
    return perc

price_five_mins_ago = 0.00228988329991
buy_cooldown = 1
while True:
    
    try:
        with open('price_list_15sec', 'rb') as fp:
            price_list_15sec = pickle.load(fp)

        with open('posiciones_abiertas', 'rb') as fp:
            posiciones_abiertas = pickle.load(fp)

        with open('posiciones_cerradas', 'rb') as fp:
            posiciones_cerradas = pickle.load(fp)
    except:
        pass

    buy_cooldown -= 1



    try:
        price_now = api_cmc.cryptocurrency_quotes_latest(symbol='SRK').data['SRK']['quote']['USD']['price']
        price_list_15sec.append(price_now)
        current_pos = len(price_list_15sec) - 1

        price_five_mins_ago = price_list_15sec[current_pos - 20] #20 pos equivale a 5min (15*20 = 300)

        #Si el precio se ha disparado
        if porcentaje(price_now, price_five_mins_ago) > 10:
            #Normalizamos el precio (si se dispara lo baja)
            price_list_15sec[current_pos] = price_list_15sec[current_pos - 20] 

        if porcentaje(price_now, price_five_mins_ago) < -6 and buy_cooldown < 1: #CAMBIAR A 7.5
            #Compramos la pos
            posiciones_abiertas.append(Posicion())
            posiciones_abiertas[-1].precio_compra = price_now

            print("[+] Posicion comprada de valor: ", price_now)

            to_send = "[+] Posicion comprada de valor: " + str(price_now)
            tb.send_message('1131428928', to_send) #A mi
            tb.send_message('414279707', to_send)
            buy_cooldown = 5

        i = -1
        for position in posiciones_abiertas: #Vemos las que tenemos abiertas
            i += 1
            if porcentaje(position.precio_compra, price_now) > 5: #Si alguna tiene un 3% de profit se "vende" CAMBIAR A 5
                position.precio_venta = price_now 
                posiciones_cerradas.append(position) #Añadimos a lista de pos cerradas
                posiciones_abiertas.pop(i) #La quitamos de las abiertas

                print("[-] Posicion vendida con un +", porcentaje(position.precio_venta, position.precio_compra) - 100, "%")
                to_send = "[-] Posicion vendida con un +" + str(porcentaje(position.precio_venta, position.precio_compra) - 100) + "% de beneficio"
                tb.send_message('1131428928', to_send) # A mi
                tb.send_message('414279707', to_send)

    except Exception as e:
        
        pass

    with open('price_list_15sec', 'wb') as fp:
        pickle.dump(price_list_15sec, fp)

    with open('posiciones_abiertas', 'wb') as fp:
        pickle.dump(posiciones_abiertas, fp)

    with open('posiciones_cerradas', 'wb') as fp:
        pickle.dump(posiciones_cerradas, fp)

    print("Price is: ", str(price_now) + "$")
    output_current_time()


    precentagechange = porcentaje(price_now, price_five_mins_ago) #Imprimiendo bonito
    if precentagechange < 0:
        print("Percentage change from 5min ago:",  str(precentagechange) + "%")
    else:
        print("Percentage change from 5min ago:",  "+" + str(precentagechange) + "%" )

    print("")

    time.sleep(15)