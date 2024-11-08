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
    noticias_div = soup.find('div', class_='sc-1aaf288f-1 dBZArI')
    

    # Verificar si `noticias_div` existe
    if noticias_div:
        noticias = noticias_div.find_all('div', class_='sc-db8a830b-3 iuexty')
        resultado = []

        for noticia in noticias:  
            equipos = []
            time_elem = []
            equipos_divs = noticia.find_all('div', class_="events")  # Lista de divs para equipos
            
                        

            
            # Extraer el texto de cada equipo y agregarlo a la lista `equipos`
            for equipo_div in equipos_divs:
                times = equipo_div.find('div', class_="event-time")  # Lista de divs para equipos
                time_elem.append(times.text.strip())
                equipo_nombre = equipo_div.find('h3', class_="event-name")
                equipos.append(equipo_nombre.text.strip())  # Extraer el texto de cada equipo y agregarlo a la lista `equipos`
            
            canales = []
            torneo = noticia.find('h2', class_="sc-db8a830b-4 eiZrTA")
            
            canal_names = noticia.find_all('span', class_="canal-name")
            for canal_name in canal_names:
                canales.append(canal_name.text.strip())

            if torneo:
                resultado.append({
                    'equipos': equipos,  # Lista de equipos extraída correctamente
                    'torneo': torneo.text.strip() if torneo else None,
                    'time': time_elem,
                    'canales': canales if canales else None
                })

    else:
        app.logger.error("No se encontró el contenedor `noticias_div` en la página.")

    
    CACHE = resultado
    CACHE_TIMESTAMP = tiempo.time()  # Actualiza la marca de tiempo del caché
    return jsonify(resultado)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Puerto asignado por Render
    app.run(host='0.0.0.0', port=port)
