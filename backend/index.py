from flask import Flask, request, jsonify
from lxml import etree
import os
from app import *

app = Flask(__name__)

@app.route('/clasificar', methods=['POST'])
def clasificar():
    file = request.files['file']
    
    # Parsear el archivo XML
    diccionario, mensajes = parse_xml(file)
    
    # Inicializar el diccionario de resultados
    resultados = {
        "total": 0,
        "positivos": 0,
        "negativos": 0,
        "neutros": 0,
        "empresas": {}
    }
    
    # Procesar cada mensaje y clasificar su sentimiento
    for mensaje in mensajes:
        sentimiento = classify_message(diccionario, mensaje)
        
        # Incrementar el contador correspondiente
        if sentimiento in resultados:
            resultados[sentimiento] += 1
        else:
            resultados[sentimiento] = 1
            
        resultados["total"] += 1

    # Generar el archivo de salida XML
    output_path = "output/salida.xml"
    generate_output_xml(resultados, output_path)
    
    # Leer el contenido del archivo procesado
    with open(output_path, 'r') as output_file:
        contenido_salida = output_file.read()

    return jsonify({
        "message": "Archivo procesado y salida generada",
        "content": contenido_salida
    }), 200

@app.route('/analizar_mensaje', methods=['POST'])
def analizar_mensaje():
    data = request.get_json()
    mensaje = data['mensaje']
    
    # Ejecutar la función de análisis del mensaje
    resultado = classify_message(diccionario={}, mensaje=mensaje)  # Modifica según tu implementación

    # Enviar la respuesta en JSON
    return jsonify(resultado), 200

@app.route('/datos_procesados', methods=['POST'])
def datos_procesados():
    data = request.get_json()
    mensaje = data['mensaje']
    
    # Ejecutar la función de análisis del mensaje
    resultado = classify_message(diccionario={}, mensaje=mensaje)  # Modifica según tu implementación

    # Enviar la respuesta en JSON
    return jsonify(resultado), 200

if __name__ == '__main__':
    app.run(debug=True)
