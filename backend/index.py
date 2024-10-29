from flask import Flask, request, jsonify
from lxml import etree
import os
from app import *

app = Flask(__name__)

@app.route('/clasificar', methods=['POST'])
def clasificar():
    if 'file' not in request.files:
        return jsonify({"message": "No se encontró el archivo"}), 400
    
    file = request.files['file']
    output_path = os.path.join("output", "salida.xml")
    
    # Procesa el archivo, analízalo y guarda el resultado en output_path
    diccionario, empresas, mensajes = parse_xml(file)  # Asumiendo que parse_xml es tu función de procesamiento
    resultados = classify_message(diccionario, mensajes, empresas)  # procesar_mensajes realiza la clasificación
    
    generate_output_xml(resultados, output_path)
    
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
