class Empresa:
    def __init__(self, nombre, servicios):
        self.nombre = nombre
        self.servicios = servicios[0]

    def agregar_servicio(self, servicio):
        self.servicios.append(servicio)