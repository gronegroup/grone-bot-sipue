# backend.py
# Backend Flask para bot trader Binance REAL
# Configura tus claves API aquí

from flask import Flask, jsonify, request
from flask_cors import CORS
from binance.client import Client
import threading
import time
import pandas as pd
import smtplib
from email.mime.text import MIMEText
import requests

API_KEY = "1UM5DD5TR9R0hyeN8t3JCPKrA5fadviPPIxx0RA1LuavUcaZHR2fXiWi22kzkbAm"
API_SECRET = "TwI6LZnDWbGwgZ8VchrLNB3iU4kw4TlQgHfjF1AEALvtENzGkmI8koZ8IgrpWM09"

client = Client(API_KEY, API_SECRET)

app = Flask(__name__)
CORS(app)

bot_status = {'running': False, 'last_action': 'Ninguna', 'last_price': 0}
operation_history = []

symbol = 'BTCUSDT'
interval = Client.KLINE_INTERVAL_1HOUR
lookback = 60 * 24  # 60 días en horas

# Estrategia avanzada: usa datos de los últimos 60 días

def get_historical_data():
    klines = client.get_historical_klines(symbol, interval, f"{lookback} hours ago UTC")
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
        'quote_asset_volume', 'number_of_trades', 'taker_buy_base',
        'taker_buy_quote', 'ignore'])
    df['close'] = df['close'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    return df

def trading_strategy():
    df = get_historical_data()
    avg_price = df['close'].mean()
    last_price = df['close'].iloc[-1]
    max_price = df['high'].max()
    min_price = df['low'].min()
    # Estrategia: compra si el precio está cerca del mínimo de 60 días, vende si está cerca del máximo
    if last_price <= min_price * 1.05:
        return 'buy', last_price
    elif last_price >= max_price * 0.95:
        return 'sell', last_price
    elif last_price < avg_price:
        return 'buy', last_price
    elif last_price > avg_price:
        return 'sell', last_price
    else:
        return 'hold', last_price

# Configura tu email para notificaciones
NOTIFY_EMAIL = "fabroxf@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "fabroxf@gmail.com"
SMTP_PASS = "AQUÍ_TU_CONTRASEÑA_DE_GMAIL"

def send_notification(subject, message):
    try:
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = SMTP_USER
        msg['To'] = NOTIFY_EMAIL
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, [NOTIFY_EMAIL], msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Error enviando notificación: {e}")

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
        try:
            requests.post('https://exp.host/--/api/v2/push/send', json=payload)
        except Exception as e:
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
