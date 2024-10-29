from flask import Flask, request, jsonify
from lxml import etree
import os
from app import *

from flask import send_from_directory

app = Flask(__name__)

@app.route('/clasificar', methods=['POST'])
def clasificar():
    if 'file' not in request.files:
        return jsonify({"message": "No se encontró el archivo"}), 400

    file = request.files['file']
    output_path = os.path.join("output", "salida.xml")
    pdf_path = os.path.join("output", "reporte.pdf")  # Define la ruta del PDF

    diccionario, empresas, mensajes = parse_xml(file)
    resultados = classify_message(diccionario, mensajes, empresas)
    generate_output_xml(resultados, output_path)

    # Generar PDF
    generate_pdf_from_xml(output_path, pdf_path)

    with open(output_path, 'r') as output_file:
        contenido_salida = output_file.read()

    return jsonify({
        "message": "Archivo procesado y salida generada",
        "content": contenido_salida,
        "pdf_path": pdf_path  # O puedes devolver la ruta o link del PDF si lo deseas
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
    output_path = os.path.join("output", "salida.xml")
    if not os.path.exists(output_path):
        return jsonify({"message": "No se encontraron datos procesados"}), 404
    
    # Leer el contenido del archivo XML
    with open(output_path, 'r') as output_file:
        contenido_salida = output_file.read()

    return jsonify({
        "content": contenido_salida
    }), 200

@app.route('/descargar_pdf') 
def descargar_pdf():
    pdf_path = os.path.join("output", "reporte.pdf")
    if os.path.exists(pdf_path):
        return send_from_directory("output", "reporte.pdf", as_attachment=True)
    else:
        return jsonify({"message": "PDF no encontrado"}), 404

if __name__ == '__main__':
    app.run(debug=True)

