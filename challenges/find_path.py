import heapq  # Biblioteca que cria a fila de prioridade (heap)
import math   # Biblioteca para calcular distâncias

from data_structures.city_map import CityMap


def find_path(
    city_map: CityMap,  # O mapa da cidade com ruas e interseções
    start: int,         # Número da interseção de partida
    goal: int,          # Número da interseção de destino
) -> list[int]:         # Retorna uma lista de interseções do caminho


    # CASO ESPECIFICO: Quando já estamos no destino, não precisamos mais buscar
    
    if start == goal:
        return [start]

    intersecoes = city_map.intersections  # Dicionário: ID -> posição (x, y)
    estradas = city_map.roads             # Dicionário: ID -> lista de vizinhos

    # NORMALIZAÇÃO DA HEURÍSTICA
    # O mapa tem coordenadas grandes (até 1000x1000).
    # Sem normalizar, a estimativa de distância ficaria enorme
    # e atrapalharia o algoritmo. Dividimos pela diagonal do mapa
    # para garantir que h(n) fique sempre entre 0 e 1.
   
    xs = [x for x, y in intersecoes.values()]  # Pega todas as coordenadas X
    ys = [y for x, y in intersecoes.values()]  # Pega todas as coordenadas Y
    diagonal = math.hypot(
        max(xs) - min(xs),  # Largura total do mapa
        max(ys) - min(ys),  # Altura total do mapa
    ) or 1  # Garante que não dividiremos por zero

    def heuristica(no):
        # Calcula a distância em linha reta do nó atual até o destino
        # (seria basicamente como um pássaro voaria, sem seguir ruas)
        # Dividido pela diagonal para ficar entre 0 e 1 — nunca superestima
        x1, y1 = intersecoes[no]
        x2, y2 = intersecoes[goal]
        return math.hypot(x2 - x1, y2 - y1) / diagonal

    # INICIALIZAÇÃO DA HEAP
    # A heap é a fila de prioridade do A*.
    # Cada elemento é uma tupla: (f, g, no)
    #   f = custo total estimado (g + h) — define a prioridade
    #   g = custo real percorrido até aqui (número de ruas)
    #   no = ID da interseção
    # Começa com o nó de partida, custo real 0

    heap_aberta = []
    heapq.heappush(heap_aberta, (heuristica(start), 0, start))

    # Guarda o menor custo real conhecido para chegar em cada nó
    # Começa sabendo que chegar ao start custa 0
    custo_g = {start: 0}

    # Guarda de qual nó viemos ao chegar em cada interseção
    # Usado no final para reconstruir o caminho percorrido
    veio_de = {}


    # LOOP PRINCIPAL DO A*
    # Enquanto houver nós a explorar na heap...
    while heap_aberta:

        # Retira o nó com MENOR f da heap (o mais promissor)
        # O _ descarta o f, pois não precisamos mais dele aqui
        _, g, atual = heapq.heappop(heap_aberta)

        # CONSEGUIMOS CHEGAR AO DESTINO!
        # Agora reconstruímos o caminho andando de trás pra frente
        # usando o dicionário veio_de, do goal até o start
        if atual == goal:
            caminho = []
            while atual in veio_de:
                caminho.append(atual)       # Adiciona o nó atual
                atual = veio_de[atual]      # Volta para o nó anterior
            caminho.append(start)           # Adiciona o ponto de partida
            caminho.reverse()               # Inverte: agora vai do start ao goal
            return caminho

        # LAZY DELETION (remoção preguiçosa):
        # Problema: quando achamos um caminho melhor para um nó,
        # não conseguimos apagar a entrada antiga da heap.
        # Então a heap pode ter DUAS entradas para o mesmo nó:
        #
        #   (f=4, g=3, nó=7)  ← entrada nova, caminho melhor  
        #   (f=6, g=5, nó=7)  ← entrada antiga, caminho pior  
        #
        # Quando a entrada velha (g=5) for retirada da heap,
        # verificamos de esse custo é pior que o melhor que já registramos,
        # Se sim, é lixo nós descartamos e passamos para o próximo.
        # Isso evita reprocessar o mesmo nó com um caminho pior.
        
        if g > custo_g.get(atual, float("inf")):
            continue

        # Analisa cada rua saindo da interseção atual
        for vizinho in estradas[atual]:

            # Custo para chegar neste vizinho = custo atual + 1 rua
            custo_tentativo = g + 1

            # Só atualiza se encontrou um caminho MELHOR para este vizinho
            # (menor número de ruas do que qualquer caminho anterior)
            if custo_tentativo < custo_g.get(vizinho, float("inf")):

                # Registra o novo melhor custo para este vizinho
                custo_g[vizinho] = custo_tentativo

                # Marca que chegamos a este vizinho vindo do nó atual
                veio_de[vizinho] = atual

                # Calcula f = g + h e insere o vizinho na heap
                # h estima quantas ruas ainda faltam até o destino
                f = custo_tentativo + heuristica(vizinho)
                heapq.heappush(
                    heap_aberta, (f, custo_tentativo, vizinho)
                )

    # A heap esvaziou sem encontrar o destino:
    # Não existe caminho possível entre start e goal

    return []