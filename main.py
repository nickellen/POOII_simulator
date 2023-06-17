from classes.simulador import *

def setBool(variavel):
    if variavel =="True":
        variavel = True
    else:
        variavel = False
    return variavel

def main():

    while True:

        op = int(input("\n1 - Testar métodos de embarque\n2 - Encontrar melhor sequencia de embarque\n"))
        os.system('cls')

        if (op==1):
            quantidadeSim = int(input("Quantidade de simulações: "))
            Simulador().testarMetodos(quantidadeSim, 72, 6)

        elif (op==2):

            quantidadeSim = int(input("Quantidade de simulações: "))
            metodo = int(input("Informe o método:\n1 - Random\n2 - Steffen\n3 - Wilma\n4 - Blocos\n5 - De trás para frente\n"))
            bd = input("Deseja salvar as simulações (True ou False): ")
            visual = input("Deseja ver a representação visual (True ou False): ")
    
            bd = setBool(bd)
            visual = setBool(visual)
        
            Simulador().rodarSimulacoes(
                quantidadeSimulacoes = quantidadeSim,
                qtdAssento = 72,
                qtdColuna = 6,
                metodo = metodo,
                useDB = bd,
                visual = visual
            )

main()
