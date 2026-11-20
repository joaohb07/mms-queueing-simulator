####################################################################################################
####################################################################################################
# ==================================================================================================
#                                   SIMULADOR DE FILA M/M/s
# ==================================================================================================
# Funções principais da simulação M/M/s:
# - M: chegadas com tempos entre chegadas exponenciais.
# - M: tempos de serviço exponenciais.
# - s: quantidade configurável de servidores em paralelo.
#
# A geração de clientes para quando a próxima chegada ultrapassa
# simulation_time. A fila é única e cada cliente vai para o servidor que
# estiver disponível primeiro.
####################################################################################################
####################################################################################################
import math
####################################################################################################
####################################################################################################
# --------------------------------------------------------------------------------------------------
#                             GERADOR DE NÚMEROS PSEUDOALEATÓRIOS
# --------------------------------------------------------------------------------------------------
# Gerador congruencial linear:
#   U_i = x_i / M
#   x_(i+1) = (a * x_i + c) mod M
####################################################################################################
####################################################################################################
def generate_random_numbers(x, n, pt):
    """
    Gera n números pseudoaleatórios uniformes no intervalo [0, 1).

    Usa o gerador multiplicativo de Park-Miller:
    a = 16807, c = 0 e M = 2^31 - 1.
    """

    a = 16807
    M = (2**31) - 1
    c = 0

    random_numbers = []

    for i in range(n):

        # Converte a semente atual em um valor uniforme.
        random_numbers.append(x / M)

        # Avança para a próxima semente.
        x = ((a * x) + c) % M
    
    if pt:
        print(f"Random numbers: {random_numbers}")
    
    return random_numbers
####################################################################################################
####################################################################################################
# --------------------------------------------------------------------------------------------------
#                           GERAÇÃO DOS DADOS ATÉ O TEMPO DE SIMULAÇÃO
# --------------------------------------------------------------------------------------------------
# Converte números uniformes em variáveis exponenciais:
#   TEC = -ln(U) / 0.5
#   TS  = -ln(U) / 0.125
####################################################################################################
####################################################################################################
def generate_inputs_until_time(seed_1, seed_2, simulation_time, random_list_size, pt):
    """
    Gera TEC, TS e horários de chegada até o limite simulation_time.

    A quantidade de clientes não é fixa. Cada chegada é acumulada no relógio;
    se a próxima chegada passar de simulation_time, ela é descartada.

    A leitura começa na posição 2 para manter compatibilidade com os cálculos
    manuais da atividade.
    """

    random_list_1 = generate_random_numbers(seed_1, random_list_size, False)
    random_list_2 = generate_random_numbers(seed_2, random_list_size, False)

    tec_list = []
    ts_list = []
    arrival_time_list = []

    list_position = 2
    current_arrival_time = 0

    while list_position < random_list_size:

        # Converte o próximo número pseudoaleatório em tempo entre chegadas.
        tec = -math.log(random_list_1[list_position]) / 0.5
        next_arrival_time = current_arrival_time + tec

        # Clientes que chegariam depois do horizonte não entram na simulação.
        if next_arrival_time > simulation_time:
            break
        
        # Converte o próximo número pseudoaleatório em tempo de serviço.
        ts = -math.log(random_list_2[list_position]) / 0.125

        tec_list.append(tec)
        ts_list.append(ts)
        arrival_time_list.append(next_arrival_time)

        current_arrival_time = next_arrival_time
        list_position += 1

    # Se a lista de números pseudoaleatórios acabar antes de atingir o tempo de simulação, 
    # o usuário deve aumentar random_list_size.
    if list_position >= random_list_size and current_arrival_time <= simulation_time:
        raise ValueError(
            "A lista de números aleatórios acabou antes de atingir o tempo de simulação. "
            "Aumente random_list_size."
        )
    
    # Se não houver clientes, a simulação não faz sentido.
    if len(tec_list) == 0:
        raise ValueError("Nenhum cliente chegou dentro do tempo de simulação.")

    if pt:
        print(f"Clientes simulados: {len(tec_list)}")
        print(f"Última chegada: {arrival_time_list[-1]:.5f}")

    return tec_list, ts_list, arrival_time_list
####################################################################################################
####################################################################################################
# --------------------------------------------------------------------------------------------------
#                                   SIMULAÇÃO DA FILA M/M/s
# --------------------------------------------------------------------------------------------------
# Recebe chegadas e serviços já gerados, escolhe o servidor de cada cliente e
# calcula início, fim, fila, tempo no sistema e ociosidade.
####################################################################################################
####################################################################################################
def simulate_mm_s(arrival_time_list, ts_list, server_count, simulation_time, pt):
    """
    Simula uma fila única com vários servidores em paralelo.

    Cada cliente vai para o servidor que ficará livre primeiro. Em caso de
    empate, fica com o servidor de menor número.

    Retorna as listas usadas na planilha: servidor escolhido, início/fim de
    serviço, fila, sistema e ociosidade.
    """

    client_size = len(arrival_time_list)

    # Cada posição guarda quando o servidor correspondente ficará livre.
    server_available_time = [0 for _ in range(server_count)]

    # Listas de saída, cada uma com tamanho igual ao número de clientes.
    server_id_list = []
    # Início e fim do atendimento de cada cliente.
    service_start_time_list = []
    service_end_time_list = []
    # Tempo de espera na fila e tempo total no sistema.
    line_time_list = []
    system_time_list = []

    # Ociosidade do servidor que atendeu cada cliente.
    worker_idle_time_list = []

    # Matriz cliente x servidor. Só o servidor escolhido recebe valor na linha.
    server_idle_time_matrix = []

    # Totais por servidor, incluindo a ociosidade final até simulation_time.
    server_idle_total_list = [0 for _ in range(server_count)]
    server_final_idle_list = [0 for _ in range(server_count)]

    # Simulação de cada cliente, na ordem de chegada.
    for i in range(client_size):
        arrival = arrival_time_list[i]
        service = ts_list[i]

        # min() mantém o menor índice em caso de empate.
        server_index = min(
            range(server_count),
            key=lambda index: server_available_time[index]
        )

        # Se o servidor estiver ocupado, o cliente espera.
        start_time = max(arrival, server_available_time[server_index])
        end_time = start_time + service

        waiting_time = start_time - arrival
        system_time = end_time - arrival

        # Ociosidade antes deste atendimento.
        idle_time = max(0, arrival - server_available_time[server_index])

        # Ociosidade do servidor escolhido, com zeros para os demais.
        idle_by_server = [0 for _ in range(server_count)]
        idle_by_server[server_index] = idle_time

        server_idle_total_list[server_index] += idle_time

        # Adiciona os resultados do cliente às listas de saída.
        server_id_list.append(server_index + 1)
        service_start_time_list.append(start_time)
        service_end_time_list.append(end_time)
        line_time_list.append(waiting_time)
        system_time_list.append(system_time)
        worker_idle_time_list.append(idle_time)
        server_idle_time_matrix.append(idle_by_server)

        # Atualiza o tempo em que o servidor escolhido ficará livre.
        server_available_time[server_index] = end_time

    # Ociosidade após o último atendimento de cada servidor, limitada ao
    # horizonte da simulação.
    for server_index in range(server_count):
        final_idle = max(0, simulation_time - server_available_time[server_index])
        server_final_idle_list[server_index] = final_idle
        server_idle_total_list[server_index] += final_idle

    if pt:
        print(f"Servidor usado por cliente: {server_id_list}")
        print(f"Ociosidade final por servidor: {[f'{x:.5f}' for x in server_final_idle_list]}")
        print(f"Total ocioso por servidor: {[f'{x:.5f}' for x in server_idle_total_list]}")

    return (
        server_id_list,
        service_start_time_list,
        service_end_time_list,
        line_time_list,
        system_time_list,
        worker_idle_time_list,
        server_idle_time_matrix,
        server_idle_total_list
    )
####################################################################################################
####################################################################################################
