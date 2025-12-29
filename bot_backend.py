# Bot de trading automático para Binance
# Descarga datos históricos de 60 días y ejecuta compras/ventas según una estrategia simple

import time
import threading
from binance.client import Client
from binance.enums import *
import pandas as pd
import os
from flask import Flask, jsonify, request
from flask_cors import CORS


user_clients = {}  # Diccionario para almacenar clientes por usuario

app = Flask(__name__)
CORS(app)

symbol = 'BTCUSDT'
interval = Client.KLINE_INTERVAL_1HOUR
lookback = 60 * 24  # 60 días en horas

bot_status = {'running': False, 'last_action': 'Ninguna', 'last_price': 0}
operation_history = []  # Historial de operaciones

def get_client(user_id):
    if user_id not in user_clients:
        raise Exception('API keys not set for this user')
    return user_clients[user_id]

def get_historical_data(user_id):
    client = get_client(user_id)
    klines = client.get_historical_klines(symbol, interval, f"{lookback} hours ago UTC")
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
        'quote_asset_volume', 'number_of_trades', 'taker_buy_base',
        'taker_buy_quote', 'ignore'])
    df['close'] = df['close'].astype(float)
    return df

def trading_strategy(user_id):
    df = get_historical_data(user_id)
    avg_price = df['close'].mean()
    last_price = df['close'].iloc[-1]
    if last_price < avg_price:
        return 'buy', last_price
    elif last_price > avg_price:
        return 'sell', last_price
    else:
        return 'hold', last_price


def trading_loop(user_id):
    while bot_status['running']:
        action, price = trading_strategy(user_id)
        bot_status['last_price'] = price
        client = get_client(user_id)
        timestamp = pd.Timestamp.now().isoformat()
        if action == 'buy':
            bot_status['last_action'] = 'Compra automática'
            try:
                order = client.order_market_buy(symbol=symbol, quantity=0.001)
                operation_history.append({'timestamp': timestamp, 'action': 'buy', 'price': price, 'order': order})
            except Exception as e:
                bot_status['last_action'] = f'Error compra: {e}'
        elif action == 'sell':
            bot_status['last_action'] = 'Venta automática'
            try:
                order = client.order_market_sell(symbol=symbol, quantity=0.001)
                operation_history.append({'timestamp': timestamp, 'action': 'sell', 'price': price, 'order': order})
            except Exception as e:
                bot_status['last_action'] = f'Error venta: {e}'
        else:
            bot_status['last_action'] = 'Sin acción'
        time.sleep(3600)

def start_bot(user_id):
    if not bot_status['running']:
        bot_status['running'] = True
        threading.Thread(target=trading_loop, args=(user_id,), daemon=True).start()

def stop_bot():
    bot_status['running'] = False


@app.route('/set_keys', methods=['POST'])
def set_keys():
    data = request.json
    user_id = data.get('user_id')
    api_key = data.get('api_key')
    api_secret = data.get('api_secret')
    if not user_id or not api_key or not api_secret:
        return jsonify({'error': 'Faltan datos'}), 400
    user_clients[user_id] = Client(api_key, api_secret)
    return jsonify({'status': 'Claves guardadas'})

@app.route('/start', methods=['POST'])
def start():
    data = request.json
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'error': 'Falta user_id'}), 400
    start_bot(user_id)
    return jsonify({'status': 'Bot iniciado'})


@app.route('/stop', methods=['POST'])
def stop():
    stop_bot()
    return jsonify({'status': 'Bot detenido'})


@app.route('/status')
def status():
    return jsonify(bot_status)


# Endpoint para consultar historial de operaciones
@app.route('/history')
def history():
    return jsonify(operation_history)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
