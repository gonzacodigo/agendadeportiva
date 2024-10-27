from concurrent.futures import ThreadPoolExecutor
import random
from flask import Flask, render_template, send_from_directory, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas
session = requests.Session()  # Reutilizar la sesión HTTP




@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/agenda', methods=['GET'])
def obtener_noticias_tn():
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
        time = noticia.find('div', class_="event-time")
        # Encontrar todos los elementos de canal-name y agregar su texto al array
        canal_names = noticia.find_all('span', class_="canal-name")
        for canal_name in canal_names:
            canales.append(canal_name.text.strip())  # Agregar texto directamente

        # Sección de agregados
        if torneo:
            resultado.append({
                'equipos': equipos.text.strip() if equipos else None,
                'torneo': torneo.text.strip() if torneo else None,
                'time': time.text.strip() if time else None,
                'canales': canales if canales else None  # Agregar la lista de canales
            })

    return jsonify(resultado)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Puerto asignado por Render
    app.run(host='0.0.0.0', port=port)
