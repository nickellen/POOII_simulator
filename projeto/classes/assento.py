class Assento:

    def __init__(self, numeroAssento):
        self.numero = numeroAssento
        self.ocupado = False

    def ocuparAssento(self, pessoa):
        self.passageiro = pessoa
        self.ocupado = True
