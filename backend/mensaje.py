from empresa import Empresa
class Mensaje:
    def __init__(self, empresa):
        self.empresa = Empresa
        self.tipo = ''
        self.palabrasPositivas = 0
        self.palabrasNegativas = 0

    def incrementarPos(self):
        self.palabrasPositivas+=1
        
    def incrementarNeg(self):
        self.palabrasNegativas+=1
        
    def defineType(self):
        if self.palabrasPositivas > self.palabrasNegativas:
            self.tipo = 'Positivo'
        elif self.palabrasPositivas < self.palabrasNegativas:
            self.tipo = 'Negativo'
        else:
            self.tipo = 'Neutral'