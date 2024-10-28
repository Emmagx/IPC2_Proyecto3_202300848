import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.core.files.storage import FileSystemStorage
import os
#from utils import generar_pdf, analizar_mensaje
API_BASE_URL = 'http://127.0.0.1:5000'  # Cambia a la URL de tu servidor si es necesario

def cargar_archivo(request):
    salida = ""
    contenido_salida = ""
    
    if request.method == 'POST' and 'archivo' in request.FILES:
        archivo = request.FILES['archivo']
        
        # Guardar archivo en el servidor temporalmente
        fs = FileSystemStorage()
        filename = fs.save(archivo.name, archivo)
        file_path = fs.path(filename)
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{API_BASE_URL}/clasificar", files=files)
        
        if response.status_code == 200:
            data = response.text  # Recibir el contenido XML como texto
            salida = "Archivo procesado correctamente"
            contenido_salida = data
        else:
            salida = "Error al procesar el archivo"
        
        # Eliminar el archivo temporal
        os.remove(file_path)
        
        return render(request, 'ventas/cargar_archivo.html', {
            'salida': salida,
            'contenido_salida': contenido_salida
        })

    return render(request, 'ventas/cargar_archivo.html', {'salida': salida})

def consultar_datos(request):
    # Suponiendo que hay un endpoint en Flask para obtener los datos procesados
    response = requests.get(f"{API_BASE_URL}/datos_procesados")
    if response.status_code == 200:
        datos_consultados = response.json()
    else:
        datos_consultados = "No se pudo obtener los datos procesados"
    
    return render(request, 'ventas/consultar_datos.html', {'datos_consultados': datos_consultados})

def resumen_clasificacion_fecha(request):
    if request.method == 'POST':
        fecha = request.POST['fecha']
        empresa = request.POST.get('empresa', None)
        
        # Realizar solicitud a la API para obtener el resumen por fecha
        params = {'fecha': fecha}
        if empresa:
            params['empresa'] = empresa
        response = requests.get(f"{API_BASE_URL}/resumen_fecha", params=params)
        
        if response.status_code == 200:
            datos_grafico = response.json()
        else:
            datos_grafico = "No se pudo obtener el resumen por fecha"
        
        return render(request, 'ventas/resumen_clasificacion_fecha.html', {'datos_grafico': datos_grafico})
    
    return render(request, 'ventas/resumen_clasificacion_fecha.html')

def resumen_rango_fechas(request):
    if request.method == 'POST':
        fecha_inicio = request.POST['fecha_inicio']
        fecha_fin = request.POST['fecha_fin']
        empresa = request.POST.get('empresa', None)
        
        params = {'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin}
        if empresa:
            params['empresa'] = empresa
        response = requests.get(f"{API_BASE_URL}/resumen_rango", params=params)
        
        if response.status_code == 200:
            datos_rango = response.json()
        else:
            datos_rango = "No se pudo obtener el resumen por rango de fechas"
        
        return render(request, 'resumen_rango_fechas.html', {'datos_rango': datos_rango})
    
    return render(request, 'ventas/resumen_rango_fechas.html')

def prueba_mensaje(request):
    resultado = None
    if request.method == 'POST':
        mensaje = request.POST['mensaje']
        
        # Enviar el mensaje a la API para su análisis
        response = requests.post(f"{API_BASE_URL}/analizar_mensaje", json={'mensaje': mensaje})
        
        if response.status_code == 200:
            resultado = response.json()
        else:
            resultado = "No se pudo analizar el mensaje"
    
    return render(request, 'ventas/prueba_mensaje.html', {'resultado': resultado})

def home(request):
    return render(request, 'ventas/home.html')

def ayuda(request):
    return render(request, 'ventas/ayuda.html')

def reporte_pdf(request):
    return render(request, 'ventas/reporte_pdf.html')
