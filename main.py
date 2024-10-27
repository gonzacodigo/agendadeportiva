from concurrent.futures import ThreadPoolExecutor
import random
from flask import Flask, render_template, send_from_directory, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import time as tiempo  # Renombrar el módulo time

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas
session = requests.Session()  # Reutilizar la sesión HTTP

CACHE = None
CACHE_TIMESTAMP = 0
CACHE_DURATION = 60  # Duración del caché en segundos

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/agenda', methods=['GET'])
def obtener_noticias_tn():
    global CACHE, CACHE_TIMESTAMP
    
    # Verifica si los datos están en caché y aún son válidos
    if CACHE and (tiempo.time() - CACHE_TIMESTAMP) < CACHE_DURATION:
        return jsonify(CACHE)
    
    url = "https://www.ole.com.ar/agenda-deportiva"

    # Realizar la solicitud usando requests directamente
    try:
        response = session.get(url)
        response.raise_for_status()  # Lanza excepción si falla
    except requests.RequestException as e:
        app.logger.error(f"Error en la solicitud: {e}")
        return jsonify({'error': 'No se pudo obtener las noticias'}), 500

    soup = BeautifulSoup(response.text, 'html.parser')
    noticias = soup.find_all('div', class_='sc-73748f61-3 eMRaBa')

    resultado = []

    for noticia in noticias:
        canales = []
        torneo = noticia.find('h2', class_="sc-73748f61-4 hRQtTc")
        equipos = noticia.find('h3', class_="event-name")
        time_elem = noticia.find('div', class_="event-time")
        
        canal_names = noticia.find_all('span', class_="canal-name")
        for canal_name in canal_names:
            canales.append(canal_name.text.strip())

        if torneo:
            resultado.append({
                'equipos': equipos.text.strip() if equipos else None,
                'torneo': torneo.text.strip() if torneo else None,
                'time': time_elem.text.strip() if time_elem else None,
                'canales': canales if canales else None
            })
    
    CACHE = resultado
    CACHE_TIMESTAMP = tiempo.time()  # Actualiza la marca de tiempo del caché
    return jsonify(resultado)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Puerto asignado por Render
    app.run(host='0.0.0.0', port=port)
