from flask import Flask, request, jsonify
from lxml import etree

import re

app = Flask(__name__)

def parse_xml(file_path):
    tree = etree.parse(file_path)
    root = tree.getroot()

    # Extraer el diccionario
    diccionario = {
        "positivos": [palabra.text for palabra in root.xpath('//sentimientos_positivos/palabra')],
        "negativos": [palabra.text for palabra in root.xpath('//sentimientos_negativos/palabra')],
        "empresas": {}
    }

    # Extraer empresas y servicios
    for empresa in root.xpath('//empresas_analizar/empresa'):
        nombre = empresa.find('nombre').text
        servicios = {servicio.get('nombre'): [alias.text for alias in servicio.findall('alias')] for servicio in empresa.findall('servicios/servicio')}
        diccionario["empresas"][nombre] = servicios

    # Extraer mensajes
    mensajes = [mensaje.text for mensaje in root.xpath('//lista_mensajes/mensaje')]

    return diccionario, mensajes

def classify_message(diccionario, mensaje):
    # Normalizar el mensaje (sin mayúsculas, sin tildes)
    mensaje = mensaje.lower()
    mensaje = re.sub(r'[áéíóú]', lambda x: x.group(0).translate(str.maketrans("áéíóú", "aeiou")), mensaje)
    
    # Contar palabras positivas y negativas
    positive_count = sum(mensaje.count(palabra) for palabra in diccionario["positivos"])
    negative_count = sum(mensaje.count(palabra) for palabra in diccionario["negativos"])

    # Determinar sentimiento
    if positive_count > negative_count:
        return "positivo"
    elif negative_count > positive_count:
        return "negativo"
    else:
        return "neutro"

def generate_output_xml(resultados, output_path="salida.xml"):
    root = etree.Element("lista_respuestas")

    # Verifica que `resultados` tenga la estructura correcta
    respuesta = etree.SubElement(root, "respuesta")
    
    # Información general de mensajes
    mensajes = etree.SubElement(respuesta, "mensajes")
    etree.SubElement(mensajes, "total").text = str(resultados["total"])
    etree.SubElement(mensajes, "positivos").text = str(resultados["positivos"])
    etree.SubElement(mensajes, "negativos").text = str(resultados["negativos"])
    etree.SubElement(mensajes, "neutros").text = str(resultados["neutros"])

    # Análisis por empresa y servicio (si está presente en `resultados`)
    if "empresas" in resultados:
        analisis = etree.SubElement(respuesta, "analisis")
        for empresa, empresa_data in resultados["empresas"].items():
            empresa_elem = etree.SubElement(analisis, "empresa", nombre=empresa)
            
            # Datos de la empresa
            empresa_mensajes = etree.SubElement(empresa_elem, "mensajes")
            etree.SubElement(empresa_mensajes, "total").text = str(empresa_data.get("total", 0))
            etree.SubElement(empresa_mensajes, "positivos").text = str(empresa_data.get("positivos", 0))
            etree.SubElement(empresa_mensajes, "negativos").text = str(empresa_data.get("negativos", 0))
            etree.SubElement(empresa_mensajes, "neutros").text = str(empresa_data.get("neutros", 0))

            # Análisis por servicio
            servicios = etree.SubElement(empresa_elem, "servicios")
            for servicio, servicio_data in empresa_data.get("servicios", {}).items():
                servicio_elem = etree.SubElement(servicios, "servicio", nombre=servicio)
                servicio_mensajes = etree.SubElement(servicio_elem, "mensajes")
                etree.SubElement(servicio_mensajes, "total").text = str(servicio_data.get("total", 0))
                etree.SubElement(servicio_mensajes, "positivos").text = str(servicio_data.get("positivos", 0))
                etree.SubElement(servicio_mensajes, "negativos").text = str(servicio_data.get("negativos", 0))
                etree.SubElement(servicio_mensajes, "neutros").text = str(servicio_data.get("neutros", 0))

    # Guardar el archivo de salida XML
    tree = etree.ElementTree(root)
    tree.write(output_path, pretty_print=True, xml_declaration=True, encoding="UTF-8")
