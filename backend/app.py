from flask import Flask, request, jsonify
from lxml import etree
import os
from empresa import Empresa
from mensaje import Mensaje

app = Flask(__name__)

# Parsear XML de Entrada
def parse_xml(file):
    tree = etree.parse(file)
    root = tree.getroot()

    # Extraer el diccionario de sentimientos y empresas
    diccionario = {
        "positivos": [palabra.text.strip().lower() for palabra in root.xpath('//sentimientos_positivos/palabra')],
        "negativos": [palabra.text.strip().lower() for palabra in root.xpath('//sentimientos_negativos/palabra')]
    }

    # Crear instancias de Empresa con sus servicios
    empresas = []
    for empresa_elem in root.xpath('//empresas_analizar/empresa'):
        nombre = empresa_elem.find('nombre').text.strip().lower()
        servicios = [servicio.get('nombre').lower() for servicio in empresa_elem.findall('servicios/servicio')]
        empresas.append(Empresa(nombre, servicios))

    # Crear instancias de Mensaje
    mensajes = [Mensaje(mensaje.text.strip()) for mensaje in root.xpath('//lista_mensajes/mensaje')]

    return diccionario, empresas, mensajes

# Clasificar Mensaje
def classify_message(diccionario, mensajes, empresas):
    resultados = {
        "total": len(mensajes),
        "positivos": 0,
        "negativos": 0,
        "neutros": 0,
        "empresas": {}
    }

    for mensaje in mensajes:
        # Contar palabras positivas y negativas en el mensaje
        positive_count = sum(mensaje.texto.lower().count(palabra) for palabra in diccionario["positivos"])
        negative_count = sum(mensaje.texto.lower().count(palabra) for palabra in diccionario["negativos"])

        # Asignar valores en el mensaje y definir su tipo
        mensaje.palabrasPositivas = positive_count
        mensaje.palabrasNegativas = negative_count
        mensaje.defineType()

        # Contar el mensaje en la clasificación general
        if mensaje.tipo == "Positivo":
            resultados["positivos"] += 1
        elif mensaje.tipo == "Negativo":
            resultados["negativos"] += 1
        else:
            resultados["neutros"] += 1

    # Procesar empresas mencionadas en mensajes
    for empresa in empresas:
        empresa_data = {
            "total": 0,
            "positivos": 0,
            "negativos": 0,
            "neutros": 0,
            "servicios": {}
        }
        
        for mensaje in mensajes:
            if empresa.nombre in mensaje.texto.lower():
                empresa_data["total"] += 1
                if mensaje.tipo == "Positivo":
                    empresa_data["positivos"] += 1
                elif mensaje.tipo == "Negativo":
                    empresa_data["negativos"] += 1
                else:
                    empresa_data["neutros"] += 1

        resultados["empresas"][empresa.nombre] = empresa_data

    return resultados

# Generar XML de Salida
def generate_output_xml(resultados, output_path="salida.xml"):
    root = etree.Element("lista_respuestas")
    respuesta = etree.SubElement(root, "respuesta")

    # Mensajes Generales
    mensajes = etree.SubElement(respuesta, "mensajes")
    etree.SubElement(mensajes, "total").text = str(resultados["total"])
    etree.SubElement(mensajes, "positivos").text = str(resultados["positivos"])
    etree.SubElement(mensajes, "negativos").text = str(resultados["negativos"])
    etree.SubElement(mensajes, "neutros").text = str(resultados["neutros"])

    # Agregar análisis de cada empresa y sus servicios
    for nombre_empresa, data in resultados["empresas"].items():
        empresa_elem = etree.SubElement(respuesta, "empresa", nombre=nombre_empresa)
        mensajes_empresa = etree.SubElement(empresa_elem, "mensajes")
        etree.SubElement(mensajes_empresa, "total").text = str(data["total"])
        etree.SubElement(mensajes_empresa, "positivos").text = str(data["positivos"])
        etree.SubElement(mensajes_empresa, "negativos").text = str(data["negativos"])
        etree.SubElement(mensajes_empresa, "neutros").text = str(data["neutros"])

    tree = etree.ElementTree(root)
    tree.write(output_path, pretty_print=True, xml_declaration=True, encoding="UTF-8")

@app.route('/clasificar', methods=['POST'])
def clasificar():
    if 'file' not in request.files:
        return jsonify({"message": "No se encontró el archivo"}), 400

    file = request.files['file']
    output_path = os.path.join("output", "salida.xml")
    
    diccionario, empresas, mensajes = parse_xml(file)
    resultados = classify_message(diccionario, mensajes, empresas)
    generate_output_xml(resultados, output_path)
    
    with open(output_path, 'r') as output_file:
        contenido_salida = output_file.read()

    return jsonify({
        "message": "Archivo procesado y salida generada",
        "content": contenido_salida
    }), 200

if __name__ == '__main__':
    app.run(debug=True)
