import random
import time
import os
import sqlite3
import matplotlib.pyplot as plt

class Simulador:

    def pegarSimulacoesTestadas(self):
        
        if 'simulacoes.db' not in os.listdir():
            con = sqlite3.connect("simulacoes.db")
            cursor = con.cursor()
            cursor.execute('''
                CREATE TABLE simulacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulacao TEXT,
                    tempo INTEGER
                )
            ''')
            con.commit()
            con.close()

        print('-----------TABELA---------------')
        con = sqlite3.connect("simulacoes.db")
        cursor = con.cursor()
        cursor.execute('SELECT * FROM simulacoes')
        resultados = cursor.fetchall()
        simulacoes = []
        melhorSequencia = None
        melhorTempo = None
        for resultado in resultados:
            if melhorTempo == None:
                melhorTempo = resultado[2]
                melhorSequencia = resultado[1]
            
            elif resultado[2] < melhorTempo:
                melhorTempo = resultado[2]
                melhorSequencia = resultado[1]

            simulacoes.append(resultado[1])
        con.close()

        matrixSimulacoes = []
        for i in simulacoes:
            sim = []
            for cada in i.split('_'):
                if cada != '':
                    sim.append(cada)
            matrixSimulacoes.append(sim)

        return {'matrix':matrixSimulacoes,'melhorTempo':melhorTempo,'melhorSequencia':melhorSequencia}


    def gerarGraficoTaxaDeVariacao(self):

        x = []  
        y = []

        con = sqlite3.connect("simulacoes.db")
        cursor = con.cursor()
        cursor.execute('SELECT * FROM simulacoes ORDER BY tempo DESC')
        resultados = cursor.fetchall()
        melhorTempo = None

        ultima = None

        for i,resultado in enumerate(resultados):

            if i % 100 == 0: 
                # melhor tempo atual deve ser diferente do ultimo tempo registrado nas quantidades de simulações e ser diferente de none
                if melhorTempo != ultima or ultima==None:
                    x.append(i)
                    y.append(melhorTempo)
                    ultima = melhorTempo

            if melhorTempo == None:
                melhorTempo = resultado[2]
            
            elif resultado[2] < melhorTempo:
                melhorTempo = resultado[2]
            
        con.close()

        plt.plot(x, y, color='black', linestyle='solid', linewidth=1)
        plt.title('Gráfico de Tempo de Embarque')
        plt.xlabel('Quantidade de Simulações')
        plt.ylabel('Tempo')
        plt.savefig('graficoTaxaDeVariacao.png')
        plt.show()

    def gerarGrafico(self):

        x = []
        y = []

        con = sqlite3.connect("simulacoes.db")
        cursor = con.cursor()
        cursor.execute('SELECT * FROM simulacoes')
        resultados = cursor.fetchall()
        melhorTempo = None

        ultima = None

        for i,resultado in enumerate(resultados):

            if i % 100 == 0: 
                # melhor tempo atual deve ser diferente do ultimo tempo registrado nas quantidades de simulações e ser diferente de none
                if melhorTempo != ultima or ultima==None:
                    x.append(i)
                    y.append(melhorTempo)
                    ultima = melhorTempo

            if melhorTempo == None:
                melhorTempo = resultado[2]
            
            elif resultado[2] < melhorTempo:
                melhorTempo = resultado[2]
            
        con.close()

        plt.plot(x, y, color='black', linestyle='solid', linewidth=1)
        plt.title('Gráfico de Tempo de Embarque')
        plt.xlabel('Quantidade de Simulações')
        plt.ylabel('Tempo')
        plt.savefig('grafico.png')
        plt.show()


    def rodarSimulacoes(self,quantidadeSimulacoes):
        sequencias = self.pegarSimulacoesTestadas()
        sequenciasTestadas = sequencias['matrix']
        #print('sequencia testadas:',sequenciasTestadas)
        #print('quantidadeDeTestadas:',len(sequenciasTestadas))
        melhorSequencia = sequencias['melhorSequencia']
        melhorTempo = sequencias['melhorTempo']
        
        con = sqlite3.connect("simulacoes.db")
        cursor = con.cursor()
        
        sequenciasTestes = []

        for index,i in enumerate(range(quantidadeSimulacoes)):

            aviao = Aviao()
            tempo = 0
            contadorEntrada = 0

            filaDeEmbarque2 = []
            sequencia = []
            
            while True:
                
                filaDeEmbarque2 = []
                sequencia = []
                posicoes = []
                for i in ['A','B','C','D','E','F','G','H']:
                    for numero in range(1,10):
                        posicoes.append(f'{i}{numero}')
                
                while posicoes != []:

                    posicao = random.choice(posicoes)
                    filaDeEmbarque2.append(random.choice([Adulto('nome',posicao), Crianca('nome',posicao)]))
                    sequencia.append(posicao)
                    posicoes.remove(posicao)
                    
                if filaDeEmbarque2 not in sequenciasTestadas:
                    sequenciasTestadas.append(filaDeEmbarque2)
                    break

            for _ in aviao.classes:

                while filaDeEmbarque2 != [] or not aviao.corredorVazio():

                    aviao.andarFila()
                    
                    ordem = ''
                    if(contadorEntrada < 10):
                        ordem = '0' + str(contadorEntrada)
                    else:
                        ordem = str(contadorEntrada)
                    
                    if filaDeEmbarque2 != []:
                        passageiro = filaDeEmbarque2[0]
                        passageiro.ordemEntrada = ordem

                        if aviao.colocarfila(passageiro):
                            filaDeEmbarque2.pop(0)    
                            contadorEntrada += 1    
                    
                    tempo += 1
                    
                    continue
                    time.sleep(0.1)
                    os.system('clear')
                    print(f'simulação: {index + 1} de {quantidadeSimulacoes}')
                    print('melhor tempo:',melhorTempo)
                    print('faltando embarcar:',len(filaDeEmbarque2))
                    print('tempo:',tempo)
                    print(aviao)

            if melhorTempo == None or tempo < melhorTempo:
                melhorTempo = tempo
                melhorSequencia = sequencia

            sequenciasTestadas.append(sequencia)
            
            stringSequencia = ''
            for cada in sequencia:
                stringSequencia += cada + '_'
            
            cursor.execute('INSERT INTO simulacoes (simulacao, tempo) VALUES (?, ?)', (stringSequencia,tempo))
                
        print('melhor sequencia:',melhorSequencia)
        print('melhorTempo:',melhorTempo)

        con.commit()
        con.close()

        self.gerarGrafico()
        self.gerarGraficoTaxaDeVariacao()

class Assento:

    def __init__(self, numeroAssento):
        self.numero = numeroAssento
        self.ocupado = False

    def ocuparAssento(self, pessoa):
        self.passageiro = pessoa
        self.ocupado = True
   
class Classe:

    quantidadeAssentos = 72
    assentosPorFila = 8 

    def __init__(self,nome):
        self.nomeClasse = nome
        self.assentos = []
        self.assentosDisponiveis = []
        self.lotada = False

    def ocuparAssento(self,passageiro,numero = None):

        if self.assentosDisponiveis == []:
            self.lotada = True
            return

        if numero == None:
            numero = random.choice(self.assentosDisponiveis)

        for assento in self.assentos:
            if assento.numero == numero:
                assento.ocuparAssento(passageiro)

        self.assentosDisponiveis.remove(numero)

class Aviao:

    classesDisponiveis = ['Classe Economica']
    filas = ['A','B','C','D','E','F','G','H']

    def __init__(self):
        
        self.classes = []

        self.corredor = []
        for i in range( int(Classe.quantidadeAssentos / Classe.assentosPorFila) ):
            self.corredor.append(None)

        for classe in self.classesDisponiveis:
            
            x = 0
            y = 1
            classObj = Classe(classe)
            
            for assento in range(classObj.quantidadeAssentos):
                
                numeroAssento = f'{self.filas[x]}{y}' 
                x += 1
                if(x == len(self.filas)):
                    x = 0
                    y += 1

                classObj.assentosDisponiveis.append(numeroAssento)
                classObj.assentos.append(Assento(numeroAssento))
            
            self.classes.append(classObj)

    def corredorVazio(self):
        for i in self.corredor:
            if i !=None:
                return False
        return True
            
        
    def colocarfila(self, passageiro):
        if self.corredor[0]==None:
            self.corredor[0] = passageiro
            return True
        else:
            return False
    
    def andarFila(self):
        
        for index, passageiro in enumerate(reversed(self.corredor)):

            if passageiro==None:
                continue

            posicao = len(self.corredor)-1 - index

            if posicao+1 == passageiro.numFila:
                if not passageiro.tempoBagagem or not passageiro.temBagagem:
                    self.classes[0].ocuparAssento( passageiro = passageiro , numero = passageiro.assento)
                    self.corredor[posicao] = None
                    passageiro.colocandoBagagem = False
                    continue
                else:
                    passageiro.tempoBagagem-=1
                    passageiro.colocandoBagagem = True
                    continue
   
            if posicao >= len(self.corredor)-1:
                continue

            if self.corredor[posicao+1] == None:
                self.corredor[posicao+1], self.corredor[posicao] = self.corredor[posicao], self.corredor[posicao+1]
    

    def __str__(self):
        string = ''
        for classe in self.classes:
            string += f'\n[---AVIÃO---]'
            string += f'\n\n   [A.][B.][C.][D.] |      | [E.][F.][G.][H.]'
            contador = 0
            x = 1
            y = 1
            for assento in classe.assentos:
                if x == 1:
                    string += f'\n {y} '
                if assento.ocupado:
                    string += f'<{assento.passageiro.ordemEntrada}>'
                else:
                    string += f'[{assento.numero}]'
                contador += 1
                if contador == int( classe.assentosPorFila / 2 ):
                    if self.corredor[y-1]!=None:
                        if self.corredor[y-1].temBagagem:
                            if self.corredor[y-1].colocandoBagagem:
                                string += f' |  {self.corredor[y-1].ordemEntrada}- | '
                            else:
                                string += f' |  {self.corredor[y-1].ordemEntrada}+ | '
                        else:
                            string += f' |  {self.corredor[y-1].ordemEntrada}  | '
                    else:
                        string += f' | {self.corredor[y-1]} | '
                x += 1
                if contador == classe.assentosPorFila:
                    contador = 0
                    y += 1
                    x = 1
        return string

class Pessoa:

    temBagagem = None
    tempoBagagem = None

    def __init__(self,nome,assento=None):
        self.nome = nome
        self.assento = assento
        self.numFila = int(assento[1:])
        self.entrada = None
        self.ordemEntrada = 0
        self.colocandoBagagem = False

class Crianca(Pessoa):
        temBagagem = False
        tempoBagagem = 0

class Adulto(Pessoa):
        temBagagem = True
        tempoBagagem = 3