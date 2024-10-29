class Mensaje:
    def __init__(self, texto):
        self.texto = texto
        self.palabrasPositivas = 0
        self.palabrasNegativas = 0
        self.tipo = "Neutro"  # Predeterminado como Neutro

    def defineType(self):
        if self.palabrasPositivas > self.palabrasNegativas:
            self.tipo = "Positivo"
        elif self.palabrasNegativas > self.palabrasPositivas:
            self.tipo = "Negativo"
        else:
            self.tipo = "Neutro"
