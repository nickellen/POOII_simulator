import time
import os
import sqlite3
import matplotlib.pyplot as plt
from classes.pessoa import *
from classes.aviao import *
import numpy as np

class Simulador:

    def criarBD(self):
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

    def pegarSimulacoesTestadas(self):
        '''
            Retorna um dicionário contendo uma lista com assimulações, o melhor tempo e a melhor sequência da tabela 
        '''
        
        if 'simulacoes.db' not in os.listdir():
            self.criarBD()

        con = sqlite3.connect("simulacoes.db")  
        cursor = con.cursor()
        cursor.execute('SELECT * FROM simulacoes')
        resultados = cursor.fetchall()

        simulacoes = []
        melhorSequencia = None
        melhorTempo = None

        for resultado in resultados:                                  # passa todas as sequencias da tabela para simulações

            if melhorTempo == None or resultado[2] < melhorTempo:     # obter melhor sequencia e melhor tempo de todas as simulações
                melhorTempo = resultado[2]
                melhorSequencia = resultado[1]

            simulacoes.append(resultado[1])

        con.close()

        matrixSimulacoes = []                                         
        for i in simulacoes:                                          # transforma a lista de strings em uma lista de listas
            sim = []
            for cada in i.split('_'):
                if cada != '':
                    sim.append(cada)
            matrixSimulacoes.append(sim)

        return {'matrix':matrixSimulacoes,'melhorTempo':melhorTempo,'melhorSequencia':melhorSequencia}

    def gerarGraficos(self):
        '''
            Gera os gráficos da taxa de variação do tempo pela quantidade de simulações, e o gráfico do resultado da simulação.
        '''
        self.gerarGrafico(1)
        self.gerarGrafico(2)
    
    def obterTempoEQtdSimulacoes(self, opcao):
        '''
            Retorna uma lista com as quantidades de simulações realizadas e outra com os tempos de durações das simulações
            que estão armazenadas no banco de dados.
        '''

        tempo = []              # lista dos tempos
        qtdsimulacoes = []      # lista de quantidade de simulações

        con = sqlite3.connect("simulacoes.db")
        cursor = con.cursor()

        if opcao == 1:                                        # tabela é ordenada pelas simulações de maior tempo ao menor
            cursor.execute('SELECT * FROM simulacoes ORDER BY tempo DESC')
        elif opcao == 2:                                      # tabela não é ordenada
            cursor.execute('SELECT * FROM simulacoes')

        resultados = cursor.fetchall()

        melhorTempo = None
        ultima = None
        
        for i, resultado in enumerate(resultados):    
            # gera a listas que serão usadas para criar o grafico, 
            # adicionando o tempo e quantidade de simulações nas listas a cada 100 simulaçoes, se o tempo for diferente do ultimo

            if i % 100 == 0:        
                if melhorTempo != ultima or ultima==None:
                    tempo.append(i)
                    qtdsimulacoes.append(melhorTempo)
                    ultima = melhorTempo

            if melhorTempo == None:
                melhorTempo = resultado[2]
            
            elif resultado[2] < melhorTempo:
                melhorTempo = resultado[2]
            
        con.close()

        return tempo, qtdsimulacoes
    
    def gerarGrafico(self, opcao):
        '''
            opcao 1 = gera uma gráfico da taxa de variação do tempo pela quantidade de simulações
            opcao 2 = gera um gráfico do resultado da simulação
        '''

        tempo, qtdSimulacoes = self.obterTempoEQtdSimulacoes(opcao)

        plt.plot(tempo, qtdSimulacoes, color='black', linestyle='solid', linewidth=1)
        plt.title('Gráfico de Tempo de Embarque')
        plt.xlabel('Quantidade de Simulações')
        plt.ylabel('Tempo')

        if opcao==1:
             plt.savefig('imagens/graficoTaxaDeVariacao.png')
        elif opcao==2:
             plt.savefig('imagens/grafico.png')

        plt.show()

    def criarOrdemDeEntrada(self, contadorEntrada):
    
        if(contadorEntrada < 10):                            # definir a ordem de entrada de cada passageiro que entra no corredor
            ordem = '0' + str(contadorEntrada)
        else:
            ordem = str(contadorEntrada)
        
        return ordem

    def embarcarPessoa(self, aviao, filaDeEmbarque, contadorEntrada):
        """
            Embarca o passageiro da fila de embarque no avião se houver espaço no corredor.
        """

        aviao.andarFila()
                            
        if filaDeEmbarque != []:                             # o passageiro entra no corredor se ainda tem alguem na fila de embarque
            
            passageiro = filaDeEmbarque[0]
            
            if aviao.colocarNoCorredor(passageiro):                # se possível, coloca o passageiro no corredor e o tira da fila de embarque
                
                ordem = self.criarOrdemDeEntrada(contadorEntrada)
                passageiro.ordemEntrada = ordem

                filaDeEmbarque.pop(0)
                contadorEntrada += 1
        
        return contadorEntrada
    
    def rodarSimulacoes(self, quantidadeSimulacoes, qtdAssento, qtdColuna, metodo, useDB=True, visual = False):
        '''
            Simula embarques de passageiros em um avião por meio de uma determinada ordem de entrada (metodo).\n
            visual: exibir representacao visual do embarque\n
            useBD : salvar as simulações em um banco de dados\n
            metodo:
            1 - Aleatorio, 
            2 - Steffen, 
            3 - Wilma, 
            4 - Blocos, 
            5 - De trás para frente
        '''

        if (qtdAssento % qtdColuna) != 0:   
            print("Argumentos incorretos. Todas as colunas devem ter a mesma quantidade de assentos.")
            return
        
        if useDB:

            sequencias = self.pegarSimulacoesTestadas()
            sequenciasTestadas = sequencias['matrix']
            melhorSequencia = sequencias['melhorSequencia']
            melhorTempo = sequencias['melhorTempo']

            con = sqlite3.connect("simulacoes.db")
            cursor = con.cursor()

        else:
            sequenciasTestadas = []
            melhorSequencia = []
            melhorTempo = 300

        tempoTotal = 0
        
        # Cria um avião, a fila de passageiros e simula o seu embarque a quantidade de vezes solicitada
        for index,i in enumerate(range(quantidadeSimulacoes)):

            aviao = Aviao(qtdAssento, qtdColuna) 
            
            while True:                                   # Gera fila de embarque com uma sequencia que não existe no banco de dados
                
                posicoes = []

                for i in aviao.coluna:                                      # Gera as posições possiveis dos assentos
                    for numero in range(1, aviao.classe.numFileiras+1):
                        posicoes.append(f'{i}{numero}')
                
                metodos = {3:self.metodoWilma, 4:self.metodoBlockBoarding, 5: self.metodoBackToFront}

                match metodo:                                             
                    case 1:
                        filaDeEmbarque, sequencia = self.metodoAleatorio(posicoes)
                    case 2:
                        filaDeEmbarque, sequencia = self.metodoSteffan(posicoes, aviao.classe.numFileiras)
                    case other:
                        filaDeEmbarque, sequencia = metodos[metodo](posicoes, aviao.classe.numFileiras, aviao.classe.numeroDeColunas)
            
                if sequencia not in sequenciasTestadas:           
                    sequenciasTestadas.append(sequencia)
                    break
                
                if (metodo==5 or metodo==2):    # em caso de metodo com resultado de tempo fixo já estiver no banco de dados
                    
                    print('melhor sequencia:', melhorSequencia)
                    print('melhorTempo:', melhorTempo)

                    if useDB:
                        
                        con.commit()
                        con.close()

                        self.gerarGraficos()
                    return
            
            tempo = 0                   # controle do tempo da simulação
            contadorEntrada = 0         # controle da qtd de pessoas dentro do avião
            
            while filaDeEmbarque != [] or not aviao.corredorVazio():  # Coloca as pessoas da fila de embarque em seus respectivos assentos

                contadorEntrada = self.embarcarPessoa(aviao, filaDeEmbarque, contadorEntrada) 
                tempo += 1      
                
                if visual:             
                    time.sleep(1)
                    os.system('cls')
                    print(f'simulação: {index + 1} de {quantidadeSimulacoes}')
                    print('melhor tempo:', melhorTempo)
                    print('faltando embarcar:', len(filaDeEmbarque))
                    print('tempo:', tempo)
                    print(aviao)

            if melhorTempo == None or tempo < melhorTempo:       # Define o melhor tempo já testado
                melhorTempo = tempo
                melhorSequencia = sequencia

            tempoTotal += tempo
    
            if useDB:                       # Gera sequencia em formato string para incluí-la no banco de dados
                stringSequencia = ''
                for cada in sequencia:              
                    stringSequencia += cada + '_'

                cursor.execute('INSERT INTO simulacoes (simulacao, tempo) VALUES (?, ?)', (stringSequencia, tempo))
        
        print('melhor sequencia:',melhorSequencia)
        print('melhorTempo:',melhorTempo)   

        if useDB:    

            con.commit()
            con.close()

            self.gerarGraficos()
        
        return (tempoTotal//quantidadeSimulacoes)
    
    def testarMetodos(self, quantidadeSimulacoes, qtdAssento, qtdColuna):
        """
        Testa os métodos de embarque implementados a fim de obter uma média do tempo de embarque dos passageiros em cada método.
        Gera uma tabela com os resultados.
        """
        
        metodos = {1: 'Random', 3: 'Wilma', 4:'Block',2: 'Steffen', 5:'De trás para frente'}
        mediaDeTempo = []

        for metodo in metodos:
            print(f"\nMétodo {metodos[metodo]}")

            if metodo == 2:                 # metodo Steffen e Back to Front serão simulados umas vez
                quantidadeSimulacoes = 1;
            
            tempoMedio = self.rodarSimulacoes(quantidadeSimulacoes, qtdAssento, qtdColuna, metodo, False)
            
            print("Tempo médio: ", tempoMedio)
            mediaDeTempo.append(tempoMedio)
    
        colunas = ['Algoritmo', 'Tempo Médio']

        dados = [
            ['Random', mediaDeTempo[0]],
            ['Wilma', mediaDeTempo[1]],
            ['Block', mediaDeTempo[2]],
            ['Steffen', mediaDeTempo[3]],
            ['BackToFront', mediaDeTempo[4]]
        ]

        self.criarTabela(colunas, dados)
        
    def criarTabela(self, colunas, dados):
        
        dados_array = np.array(dados)   # Converter lista de dados em um array do NumPy

        fig, ax = plt.subplots()        # Criar a figura e o eixo da tabela
        ax.axis('off')  # Ocultar eixos

        tabela = ax.table(cellText=dados_array, colLabels=colunas, loc='center') # Criar a tabela
        tabela.auto_set_column_width(col=list(range(len(colunas))))      # Ajustar o tamanho das células

        plt.savefig('imagens/tabela.png')
        plt.show()          # Exibir a tabela

    
    def posicaoNaFila(self, filaDeEmbarque, sequencia, posicao):
        '''
        Cria um passageiros na fila de Embarque e adiciona armazena a sequencia. 
        '''
        filaDeEmbarque.append(Adulto('nome',posicao))
        sequencia.append(posicao)

    def metodoAleatorio(self, posicoes):
        '''
        Gera uma lista de embarque com passageiros de ordem de entrada aleatoria.
        Retorna a fila de embarque e a sequencia de entrada.
        '''
        filaDeEmbarque = []
        sequencia = []

        while posicoes != []:    

                    posicao = random.choice(posicoes)
                    self.posicaoNaFila(filaDeEmbarque, sequencia, posicao)
                    posicoes.remove(posicao)
        
        return filaDeEmbarque, sequencia

    def embaralhaWilma(self, sequencia, fileiras, coluna, filaDeEmbarque):
        """
            Embaralha uma sequencia de entrada organizada dentro do metodo Wilma 
            para considerar uma ordem de chegada aleatória dos passageiros dentro do método.
        """
        
        ini = 0

        for bloco in range(0, coluna//2):           # a entrada no avião será organizadas em blocos (duas colunas por vez)

            fim =  2 * fileiras + ini              

            for i in range(ini, fim):
                r = random.randrange(i, fim)
                sequencia[r] , sequencia[i] = sequencia[i], sequencia[r]
                filaDeEmbarque.append(Adulto('nome',sequencia[i]))

            ini+= 2 * fileiras                      

        if (coluna % 2 != 0):                       # caso o avião tenha uma quantidade impar de colunas, uma delas entra sozinha

            fim = len(sequencia)                    

            for i in range(ini, fim):
                r = random.randrange(i, fim)
                sequencia[r] , sequencia[i] = sequencia[i], sequencia[r]
                filaDeEmbarque.append(Adulto('nome',sequencia[i]))
            

    def metodoWilma(self, posicoes, fileiras, coluna):
        '''
        Gera uma lista de embarque com passageiros de ordem de entrada:\n
        1º passageiros das cantos, 2º passageiros ao lado do canto, ...., nº passageiros dos corredores\n
        Retorna a fila de embarque e a sequencia de entrada.
        '''

        filaDeEmbarque = []
        sequencia = []
        
        while posicoes!=[]:
                                                
            for n in range(0,fileiras):              # adiciona na sequencia todos os assentos da primeira coluna, de tras para frente
                posicao =  posicoes[fileiras-1-n]    
                sequencia.append(posicao)
                posicoes.remove(posicao)           
                
            
            if (len(posicoes)!=0):
                for n in range(0,fileiras):                # adiciona todas os assentos da ultima coluna, de tras para frente
                    posicao = posicoes[len(posicoes)-1]   
                    sequencia.append(posicao)
                    posicoes.remove(posicao)             

        self.embaralhaWilma(sequencia, fileiras, coluna, filaDeEmbarque)

        return filaDeEmbarque, sequencia
    
    def embaralhaBlock(self, sequencia, fileiras, colunas, filaDeEmbarque):
        """
            Embaralha uma sequencia de entrada organizada dentro do metodo de Blocos 
            para considerar uma ordem de chegada aleatória dos passageiros dentro do método.
        """

        tam  = len(sequencia)
        canto = fileiras//3 *colunas    # quantidade de assentos nos blocos do inicio e fundo
        meio = tam - (2 * canto)        # quantidade de assentos no bloco do meio

        fim = 0
        
        for bloco in range(0,3):
            
            ini = fim

            if (bloco %2 == 0):     
                fim+=canto
            else:
                fim+= meio
            
            for p in range(ini, fim):       # embaralhando as posicos do bloco
                a = random.randrange(p, fim)      
                sequencia[a] , sequencia[p] = sequencia[p], sequencia[a]
                filaDeEmbarque.append(Adulto('nome',sequencia[p]))

    def metodoBlockBoarding(self, posicoes, fileiras, coluna):
        '''
        O avião é dividido em fundo, meio e inicio e é gerada uma lista de embarque com passageiros de ordem de entrada:\n
        1º entram os do fundo, 2º os do inicio e em 3º os do meio.\n
        Retorna a fila de embarque e a sequencia de entrada.
        '''

        filaDeEmbarque = []
        sequencia = []

        canto = fileiras//3             
        meio = (fileiras - 2*canto)     


        #Cria os blocos do método Block.
        #Fim: fileira que termina o bloco, Ini: fileira que se inicia o bloco
        ini = 1
        fim = canto + ini                
        for col in range(1, coluna+1):                            # primeira coluna até a ultima
            for fil in range (ini, fim):                          # numero de fileira pertencentes ao bloco
                posicao =  posicoes[col * fileiras - fil]         # Gera os assentos de uma col de trás para frente até o num de assentos permitido no bloco
                sequencia.append(posicao)                         

        ini += 2 * canto 
        fim = meio+ini               
        for col in range(1, coluna+1):                      
            for fil in range (ini, fim):                   
                posicao =  posicoes[col * fileiras - fil]   
                sequencia.append(posicao)

        ini -= canto 
        fim = canto+ini
        for col in range(1, coluna+1):                    
            for fil in range (ini, fim):                    
                posicao =  posicoes[col * fileiras - fil]   
                sequencia.append(posicao)                  

        self.embaralhaBlock(sequencia, fileiras, coluna, filaDeEmbarque)

        return filaDeEmbarque, sequencia

    def metodoBackToFront(self, posicoes, fileiras, coluna):
        '''
        Gera uma lista de embarque com passageiros de ordem de entrada que se inicia no fim do avião:\n
        [D11, A11, C11, B11, D10, A10, C10, B10, ..., D1, A1, C1, B1].\n
        Retorna a fila de embarque e a sequencia de entrada.
        '''

        filaDeEmbarque = []        
        sequencia = []

        tam = len(posicoes)

        for fil in range(1, fileiras+1):                                # o embarque acontece por fileiras

            col = 1                     
            for i in range(1, (coluna//2) + 1):                        

                posicao = posicoes[tam - col - fil + 1]                 # pega a ultima posição não adic. da col da direita
                self.posicaoNaFila(filaDeEmbarque, sequencia, posicao)

                posicao =  posicoes[i * fileiras - fil]                 # pega a ultima posicão não adic. da col da esquerda
                self.posicaoNaFila(filaDeEmbarque, sequencia, posicao)

                col += fileiras                                        
            
            if (coluna%2 !=0):                                           # caso a classe tenha mais colunas de um lado que do outro
                i+=1
                posicao = posicoes[tam - col - fil + 1] 
                self.posicaoNaFila(filaDeEmbarque, sequencia, posicao)
        
        return filaDeEmbarque, sequencia

    def metodoSteffan(self, posicoes, fileiras):
        '''
        Gera uma lista de embarque com passageiros de ordem de entrada:\n
        [D5, D3, D1, A5, A3, A1, D4, D2, A4, A2, ..., C4, C2, B4, B2].\n
        Retorna a fila de embarque e a sequencia de entrada.
        '''

        filaDeEmbarque = []
        sequencia = []

        lim = fileiras//2                                      # qtd de assentos de uma coluna que serão adicionados em segunda ordem

        while posicoes!=[]:

            fimLista = len(posicoes) -1                        # obtem as posicoes da ultima coluna (de tras para frente), pulando de uma em uma
            for n in range(fimLista, fimLista- fileiras, -2):     
                posicao = posicoes[n]
                self.posicaoNaFila(filaDeEmbarque, sequencia, posicao)
                posicoes.remove(posicao)

            if len(posicoes)!= fileiras:                      
                for n in range(fileiras-1, 0, -2):            # obtem as posicoes da prim coluna (de tras para frente), pulando de uma em uma
                    posicao = posicoes[n]
                    self.posicaoNaFila(filaDeEmbarque, sequencia, posicao) 
                    posicoes.remove(posicao)
        # obtem as posicoes que não foram adic das colun.
            for n in range(0, lim):                           
                posicao = posicoes[len(posicoes) - 1]
                self.posicaoNaFila(filaDeEmbarque, sequencia, posicao)
                posicoes.remove(posicao)

            if len(posicoes)!=fileiras:
                for n in range(lim -1, -1, -1):             
                    posicao = posicoes[n]
                    self.posicaoNaFila(filaDeEmbarque, sequencia, posicao)
                    posicoes.remove(posicao)

        return filaDeEmbarque, sequencia
