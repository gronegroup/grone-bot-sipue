# Bot Trader Binance

Este proyecto es un bot de trading automático para Binance, con backend en Python (Flask) y frontend móvil en React Native (Expo).

<!-- Forzar rebuild Railway 29/12/2025 -->

## Características
- Compra barato y vende caro usando análisis de los últimos 60 días.
- Notificaciones push y por email cuando se realiza una operación.
- Backend con claves API preconfiguradas (no se ingresan desde la app).

## Instalación Backend
1. Clona el repositorio:
   ```
   git clone https://github.com/gronegroup/grone-bot-sipue.git
   cd grone-bot-sipue
   ```
2. Crea un entorno virtual e instala dependencias:
   ```
   python -m venv .venv
   .venv\Scripts\activate  # En Windows
   pip install -r requirements.txt
   ```
3. Crea un archivo `.env` basado en `.env.example` y coloca tus claves de Binance y correo.
4. Ejecuta el backend:
   ```
   python backend.py
   ```

## Instalación Frontend (app-bot-trader)
1. Entra a la carpeta `app-bot-trader`:
   ```
   cd app-bot-trader
   ```
2. Instala dependencias:
   ```
   npm install
   npx expo install
   ```
3. Configura la URL del backend en el archivo correspondiente.
4. Inicia la app:
   ```
   npx expo start
   ```

## Archivos importantes
- `backend.py`: Lógica principal del bot y API.
- `requirements.txt`: Dependencias del backend.
- `app-bot-trader/`: Carpeta del frontend móvil.

## Seguridad
- No subas tu archivo `.env` con claves reales.
- Usa `.env.example` como plantilla.

## Licencia
MIT
