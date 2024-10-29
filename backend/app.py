from flask import Flask, request, jsonify,  send_file
from lxml import etree
import os
from empresa import Empresa
from mensaje import Mensaje
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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


def generate_pdf_from_xml(xml_path, pdf_path):
    # Cargar y parsear el archivo XML
    tree = etree.parse(xml_path)
    root = tree.getroot()

    # Crear un PDF
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    # Agregar título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 40, "Resumen de Clasificación")

    # Agregar datos del XML
    c.setFont("Helvetica", 12)
    y_position = height - 60

    # Mensajes generales
    mensajes = root.find("respuesta/mensajes")
    c.drawString(100, y_position, f"Total Mensajes: {mensajes.find('total').text}")
    y_position -= 20
    c.drawString(100, y_position, f"Mensajes Positivos: {mensajes.find('positivos').text}")
    y_position -= 20
    c.drawString(100, y_position, f"Mensajes Negativos: {mensajes.find('negativos').text}")
    y_position -= 20
    c.drawString(100, y_position, f"Mensajes Neutros: {mensajes.find('neutros').text}")
    y_position -= 20

    # Detallar empresas
    for empresa in root.findall("respuesta/empresa"):
        c.drawString(100, y_position, f"Empresa: {empresa.get('nombre')}")
        y_position -= 20
        mensajes_empresa = empresa.find("mensajes")
        c.drawString(120, y_position, f"Total: {mensajes_empresa.find('total').text}")
        y_position -= 20
        c.drawString(120, y_position, f"Positivos: {mensajes_empresa.find('positivos').text}")
        y_position -= 20
        c.drawString(120, y_position, f"Negativos: {mensajes_empresa.find('negativos').text}")
        y_position -= 20
        c.drawString(120, y_position, f"Neutros: {mensajes_empresa.find('neutros').text}")
        y_position -= 20

    # Finalizar el PDF
    c.save()

if __name__ == '__main__':
    app.run(debug=True)
