## Forzar rebuild Railway 29/12/2025 - No copiar .env.example
# Utiliza una imagen oficial de Python como base
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos necesarios
COPY requirements.txt ./
COPY backend.py ./

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto de Flask
EXPOSE 5000

# Comando para ejecutar la app
CMD ["python", "backend.py"]
