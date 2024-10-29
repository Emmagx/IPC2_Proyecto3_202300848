class Empresa:
    def __init__(self, nombre, servicios):
        self.nombre = nombre
        self.servicios = servicios
        self.mensajes_positivos = 0
        self.mensajes_negativos = 0
        self.mensajes_neutros = 0

    def contar_mensaje(self, tipo):
        if tipo == "Positivo":
            self.mensajes_positivos += 1
        elif tipo == "Negativo":
            self.mensajes_negativos += 1
        else:
            self.mensajes_neutros += 1
            
    def agregar_servicio(self, servicio):
        self.servicios.append(servicio)