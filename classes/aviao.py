from classes.classe import *
from classes.assento import *

class Aviao:

    def gerarColuna(self, qtdColunas):
        """
        Gera uma lista representando as colunas do avião por letras do alfebeto.
        """

        coluna = []
        ini = 65

        while ini-65 != qtdColunas:          
            coluna.append(chr(ini))
            ini+=1
        
        return coluna
    
    def __init__(self, qtdAssentos, qtdColunas):
        """
        Cria o avião com o corredor, as colunas e todos os assentos disponíveis dentro do seu interior (Classe).
        """

        self.coluna = self.gerarColuna(qtdColunas)

        # Criar a classe com todos os assentos disponpivels
        self.classe = Classe("Classe Econômica", qtdAssentos, qtdColunas)

        col = 0   
        fil = 1  
        for assento in range(self.classe.quantidadeAssentos):  # Atribui um valor a cada assento
            
            numeroAssento = f'{self.coluna[col]}{fil}'          
            col += 1

            if (col == len(self.coluna)):                      # Caso a fileira esteja completa, contagem das colunas inic. novam.
                col = 0
                fil += 1

            self.classe.assentosDisponiveis.append(numeroAssento)
            self.classe.assentos.append(Assento(numeroAssento))
        
        self.corredor = []                                      # inicia um corredor vazio
        for i in range( self.classe.numFileiras ):
            self.corredor.append(None)

    def corredorVazio(self):

        for i in self.corredor:
            if i !=None:
                return False
        return True
        
    def colocarNoCorredor(self, passageiro):
        """
            Se possível, coloca o passageiro no inicio do corredor.
        """
        if self.corredor[0]== None:
            self.corredor[0] = passageiro
            return True
        else:
            return False
    
    def andarFila(self):
        """
        Movimenta os passageiros que estão no corredor do avião, indo do final até o inicio.
        Cada andar fila marca 1 tempo de embarque. É levado em consideração ao tempo total:
        - o tempo que o passageiro leva para alcançar seu lugar (relativo ao assento)\n
        - o tempo de se colocar a bagagem (3 tempo)\n
        - tempo para se sentar no banco caso haja outros já sentados no(s) banco(s) anteriores (1 tempo cada banco)
        """
        
        for index, passageiro in enumerate(reversed(self.corredor)):

            if passageiro==None:                     # se não houver um passageiro na atual posicao do corredor, passa para a prox posicao              
                continue

            posicao = len(self.corredor)-1 - index   # pega a posicao atual do passageiro           

            if posicao+1 == passageiro.numFila:      # se a proxima posicao é na fila do assento do passageiro

                # Calcular o tempo extra que o passageiro leva para passar pelos bancos ao lado se eles estiverem ocupados
                if not passageiro.chegouNaFila:
                    passageiro.chegouNaFila = True      

                    coluna = passageiro.assento[:1]        
                    fila = passageiro.assento[1:]
                    
                    numeroDeColunas = self.classe.numeroDeColunas
                    colunas = self.coluna
                    esquerda = colunas[:int(numeroDeColunas/2)]     # divide o avião em duas partes para delimitar o corredor
                    esquerda.reverse()
                    direita = colunas[int(numeroDeColunas/2):]
                    
                    tempoCalculado = 0                           

                    #analisa o bloco da direita
                    if coluna in direita:                          
                        for assento in direita:
                            assentoTeste = assento + fila          
                            if assentoTeste == passageiro.assento:
                                break
                            elif self.classe.isAssentoOcupado(assentoTeste):    #  o valor aumenta se o assento está ocupado
                                tempoCalculado += 1                            
                    
                    #analisa o bloco da esquerda
                    elif coluna in esquerda:
                        for assento in esquerda:
                            assentoTeste = assento + fila
                            if assentoTeste == passageiro.assento:
                                break
                            elif self.classe.isAssentoOcupado(assentoTeste):
                                tempoCalculado += 1 

                    passageiro.tempoBagagem += tempoCalculado
                    passageiro.marcado = tempoCalculado
                    
                if not passageiro.tempoBagagem or not passageiro.temBagagem:            
                    self.classe.ocuparAssento( passageiro = passageiro , numero = passageiro.assento)
                    self.corredor[posicao] = None
                    passageiro.colocandoBagagem = False
                    continue
                else:
                    passageiro.tempoBagagem-=1              # tempo diminui a cada andar fila
                    passageiro.colocandoBagagem = True
                    continue

            if self.corredor[posicao+1] == None:           #  se não houver ninguém na frente, o passageiro anda
                self.corredor[posicao+1], self.corredor[posicao] = self.corredor[posicao], self.corredor[posicao+1]

    def __str__(self):
        
        string = ''

        string += f'\n[---AVIÃO---]'

        contador = 1
        string+= f"\n\n    "
        for i in self.coluna:                                         # Gera o formato:  [A. ][B. ][C. ] |      | [D. ][E. ][F. ]'
            string+= f'[{i}. ]'
            if contador == int( self.classe.numeroDeColunas / 2 ):        # identifica o corredor
                string+= f" |      | "
            contador+=1


        contador = 0
        x = 1   # numero da coluna
        y = 1   # numero da fila
        for assento in self.classe.assentos:

            # imprime os números do canto esq que repres. as fileiras
            if x == 1:                        
                if y<10:                      
                    string += f'\n 0{y} '
                else:
                    string += f'\n {y} '

            # imprime os assentos
            if assento.ocupado:                              
                string += f'<0{assento.passageiro.ordemEntrada}>'  
            else:                                            # se o assento está vazio imprime o numero do assento
                if int(assento.numero[1:])<10:                                 
                    string += f'[{assento.numero[:1]}0{assento.numero[1:]}]'
                else:
                    string += f'[{assento.numero}]'

            # imprime o corredor
            contador += 1                           
            if contador == int( self.classe.numeroDeColunas / 2 ):  

                if self.corredor[y-1]!= None:

                    if self.corredor[y-1].temBagagem:

                        if self.corredor[y-1].marcado != None:                      # se há alguem sentado nas poltronas ao lado
                            string += f' |  {self.corredor[y-1].ordemEntrada}.{self.corredor[y-1].marcado}| '
                        elif self.corredor[y-1].colocandoBagagem:                   # se há bagagem a ser colocada
                            string += f' |  {self.corredor[y-1].ordemEntrada}- | '
                        else:                                      
                            string += f' |  {self.corredor[y-1].ordemEntrada}+ | '  

                    else:
                        string += f' |  {self.corredor[y-1].ordemEntrada}  | '

                else:
                    string += f' | {self.corredor[y-1]} | '
            x += 1                                                                  # prox coluna

            if contador == self.classe.numeroDeColunas:                             # se chegou ao fim coluna x
                contador = 0
                y += 1                                                              # prox fileira
                x = 1                                                               # prim coluna nov.

        return string