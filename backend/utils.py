# utils.py

import json
import xml.etree.ElementTree as ET
from departamento import Departamento
from venta import Venta
import xml.dom.minidom
import unicodedata

def cargar_departamentos():
    with open('departamentos.json', 'r') as f:
        data = json.load(f)
    # Normalizar los nombres de los departamentos al cargarlos
    return {normalizar_texto(nombre): Departamento(nombre) for nombre in data['departamentos']}

def procesar_ventas(xml_data, departamentos):
    try:
        tree = ET.ElementTree(ET.fromstring(xml_data))
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error al parsear XML: {str(e)}")
        raise

    listado_ventas = root.find('ListadoVentas')
    if listado_ventas is None:
        raise ValueError("No se encontró el nodo 'ListadoVentas' en el XML.")
    
    for venta in listado_ventas.findall('Venta'):
        departamento_nombre = venta.get('departamento')
        # Normalizamos el nombre del departamento al cargarlo
        departamento_normalizado = normalizar_texto(departamento_nombre)

        # Buscar el departamento en el diccionario normalizado
        if departamento_normalizado in departamentos:
            departamento = departamentos[departamento_normalizado]
            departamento.incrementar_ventas()
            print(f"Ventas incrementadas para: {departamento.nombre}. Total: {departamento.numero_ventas}")
        else:
            print(f"Departamento no encontrado: {departamento_nombre}")

def generar_xml_resumen(departamentos):
    root = ET.Element("resultados")
    departamentos_elem = ET.SubElement(root, "departamentos")
    
    for departamento in departamentos.values():
        if departamento.numero_ventas > 0:
            dep_elem = ET.SubElement(departamentos_elem, departamento.nombre.replace(" ", ""))
            cantidad_elem = ET.SubElement(dep_elem, "cantidadVentas")
            cantidad_elem.text = str(departamento.numero_ventas)
    
    xml_string = ET.tostring(root, encoding='utf-8', method='xml').decode('utf-8')

    parsed_string = xml.dom.minidom.parseString(xml_string)
    pretty_xml_as_string = parsed_string.toprettyxml(indent="    ")  

    return pretty_xml_as_string

def normalizar_texto(texto):
    # Normaliza el texto eliminando acentos y tildes
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
