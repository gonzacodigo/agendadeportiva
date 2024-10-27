from concurrent.futures import ThreadPoolExecutor, as_completed
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

# Función de scraping de una sola noticia
def scrape_noticia(noticia):
    canales = []
    torneo = noticia.find('h2', class_="sc-73748f61-4 hRQtTc")
    equipos = noticia.find('h3', class_="event-name")
    time = noticia.find('div', class_="event-time")
    canal_names = noticia.find_all('span', class_="canal-name")
    
    for canal_name in canal_names:
        canales.append(canal_name.text.strip())

    return {
        'equipos': equipos.text.strip() if equipos else None,
        'torneo': torneo.text.strip() if torneo else None,
        'time': time.text.strip() if time else None,
        'canales': canales if canales else None
    }

@app.route('/agenda', methods=['GET'])
def obtener_noticias():
    url = "https://www.ole.com.ar/agenda-deportiva"
    
    try:
        response = session.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        app.logger.error(f"Error en la solicitud: {e}")
        return jsonify({'error': 'No se pudo obtener las noticias'}), 500

    soup = BeautifulSoup(response.text, 'html.parser')
    noticias = soup.find_all('div', class_='sc-73748f61-3 eMRaBa')
    
    resultado = []
    
    # Usar ThreadPoolExecutor para realizar scraping en paralelo
    with ThreadPoolExecutor() as executor:
        future_to_noticia = {executor.submit(scrape_noticia, noticia): noticia for noticia in noticias}
        
        for future in as_completed(future_to_noticia):
            try:
                data = future.result()
                if data['equipos'] and data['torneo']:  # Verificar que hay datos válidos
                    resultado.append(data)
            except Exception as e:
                app.logger.error(f"Error al procesar una noticia: {e}")
    
    return jsonify(resultado)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Puerto asignado por Render
    app.run(host='0.0.0.0', port=port)

