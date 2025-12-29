# backend.py  # Forzar redeploy Railway 29/12/2025
# Backend Flask para bot trader Binance REAL
# Configura tus claves API aquí

# backend.py
# Backend Flask para bot trader Binance REAL
# Configuración segura usando variables de entorno (.env)

import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from binance.client import Client
import threading
import time
import pandas as pd

import requests
# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv()


API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
client = Client(API_KEY, API_SECRET)

# Variables globales necesarias para el bot
bot_status = {'running': False, 'last_action': '', 'last_price': 0}
operation_history = []
symbol = 'BTCUSDT'  # Puedes cambiarlo por el par que desees

# Estrategia mínima de ejemplo
def trading_strategy():
    # Aquí deberías poner tu lógica real
    # Por ahora, solo retorna 'hold' y el último precio
    last_price = 0
    try:
        df = get_historical_data(symbol, '1h', '2 days ago UTC')
        if not df.empty:
            last_price = df['close'].iloc[-1]
    except Exception as e:
        print(f"Error en trading_strategy: {e}")
    return 'hold', last_price



def get_historical_data(symbol, interval, lookback):
    try:
        klines = client.get_historical_klines(symbol, interval, lookback)
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
            'quote_asset_volume', 'number_of_trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['close'] = df['close'].astype(float)
        return df[['timestamp', 'close']]
    except Exception as e:
        print(f"Error obteniendo datos históricos: {e}")
        return pd.DataFrame()



push_tokens = set()

@app.route('/register_push', methods=['POST'])
def register_push():
    data = request.json
    token = data.get('token')
    if token:
        push_tokens.add(token)
        return jsonify({'status': 'Token registrado'})
    return jsonify({'error': 'Token no recibido'}), 400

def send_push_notification(title, message):
    for token in push_tokens:
        payload = {
            'to': token,
            'sound': 'default',
            'title': title,
            'body': message
        }

            print(f"Error enviando push: {e}")

def trading_loop():
    while bot_status['running']:
        try:
            action, price = trading_strategy()
            bot_status['last_price'] = price
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            if action == 'buy':
                order = client.order_market_buy(symbol=symbol, quantity=0.001)
                bot_status['last_action'] = 'Compra real'
                operation_history.append({'timestamp': timestamp, 'action': 'buy', 'price': price, 'order': order})
                send_push_notification('Bot Trader - Compra', f'Compra realizada a {price} USD')
            elif action == 'sell':
                order = client.order_market_sell(symbol=symbol, quantity=0.001)
                bot_status['last_action'] = 'Venta real'
                operation_history.append({'timestamp': timestamp, 'action': 'sell', 'price': price, 'order': order})
                send_push_notification('Bot Trader - Venta', f'Venta realizada a {price} USD')
            else:
                bot_status['last_action'] = 'Sin acción'
            time.sleep(60)  # Ejecuta cada minuto
        except Exception as e:
            bot_status['last_action'] = f'Error: {str(e)}'
            time.sleep(60)

@app.route('/start', methods=['POST'])
def start():
    if not bot_status['running']:
        bot_status['running'] = True
        threading.Thread(target=trading_loop, daemon=True).start()
        bot_status['last_action'] = 'Bot iniciado'
    return jsonify({'status': 'Bot iniciado'})

@app.route('/stop', methods=['POST'])
def stop():
    bot_status['running'] = False
    bot_status['last_action'] = 'Bot detenido'
    return jsonify({'status': 'Bot detenido'})

@app.route('/status')
def status():
    return jsonify(bot_status)

@app.route('/history')
def history():
    return jsonify(operation_history)

@app.route('/balance')
def balance():
    try:
        info = client.get_account()
        balances = {b['asset']: b['free'] for b in info['balances'] if float(b['free']) > 0}
        return jsonify(balances)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/stats')
def stats():
    return jsonify({'trades': len(operation_history), 'profit': 0})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
