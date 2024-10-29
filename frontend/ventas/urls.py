# En urls.py
from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('cargar_archivo/', views.cargar_archivo, name='cargar_archivo'),
    path('consultar_datos/', views.consultar_datos, name='consultar_datos'),
    path('resumen_clasificacion_fecha/', views.resumen_clasificacion_fecha, name='resumen_clasificacion_fecha'),
    path('resumen_rango_fechas/', views.resumen_rango_fechas, name='resumen_rango_fechas'),
    path('reporte_pdf/', views.reporte_pdf, name='reporte_pdf'),
    path('prueba_mensaje/', views.prueba_mensaje, name='prueba_mensaje'),
    path('ayuda/', views.ayuda, name='ayuda'),
    path('peticiones/', views.peticiones, name='peticiones')
]