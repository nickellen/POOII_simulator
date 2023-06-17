class Pessoa:

    temBagagem = None
    tempoBagagem = None

    def __init__(self,nome, assento=None):
        self.nome = nome
        self.assento = assento
        self.numFila = int(assento[1:])
        self.entrada = None ###
        self.ordemEntrada = 0
        self.colocandoBagagem = False
        self.chegouNaFila = False
        self.marcado = None

class Crianca(Pessoa):
        temBagagem = False
        tempoBagagem = 0

class Adulto(Pessoa):
        temBagagem = True
        tempoBagagem = 3
