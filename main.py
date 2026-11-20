####################################################################################################
####################################################################################################
# ==================================================================================================
#                                   SIMULADOR DE FILA M/M/s
# ==================================================================================================
# Arquivo de execução da simulação.
# Ele define os parâmetros, chama as funções do simulador e exporta a planilha.
####################################################################################################
####################################################################################################
from exportador_planilha import export_spreadsheet
from simulador_mms import generate_inputs_until_time, simulate_mm_s
####################################################################################################
####################################################################################################
# --------------------------------------------------------------------------------------------------
#                                    FUNÇÕES AUXILIARES
# --------------------------------------------------------------------------------------------------
# request_integer_input: solicita um número inteiro maior que um valor mínimo.
####################################################################################################
####################################################################################################
def request_integer_input(message, minimum_value):
    while True:
        try:
            value = int(input(message))
        except ValueError:
            print("Digite apenas numeros inteiros.")
            continue

        if value <= minimum_value:
            print(f"O valor deve ser maior que {minimum_value}.")
            continue

        return value
####################################################################################################
####################################################################################################
# --------------------------------------------------------------------------------------------------
#                                CONFIGURAÇÕES DA SIMULAÇÃO
# --------------------------------------------------------------------------------------------------
# Os principais parâmetros são informados pelo usuário antes da execução.
# seed_1 e seed_2 geram, separadamente, os números pseudoaleatórios de TEC e TS.
# As sementes devem ser maiores que zero.
# simulation_time define até quando novas chegadas entram na simulação.
# server_count define a quantidade de servidores em paralelo e deve ser maior que zero.
# random_list_size define o tamanho da lista de números pseudoaleatórios e deve ser maior que 1000.
#
# Rodadas de referência realizadas para testar o simulador:
# - seed_1 = 10
# - seed_2 = 11
# - server_count variando de 1 até 4 servidores
# - random_list_size = 1000
####################################################################################################
####################################################################################################
seed_1 = request_integer_input("Informe a semente 1: ", 0)
seed_2 = request_integer_input("Informe a semente 2: ", 0)
simulation_time = 300
server_count = request_integer_input("Informe a quantidade de servidores: ", 0)
random_list_size = request_integer_input("Informe o tamanho da lista aleatoria: ", 999)
####################################################################################################
####################################################################################################
# --------------------------------------------------------------------------------------------------
#                                   EXECUÇÃO DA SIMULAÇÃO
# --------------------------------------------------------------------------------------------------
# Fluxo:
# 1. Gera TEC, TS e horários de chegada até simulation_time.
# 2. Simula a fila única com server_count servidores.
# 3. Exporta os resultados para uma planilha .xlsx.
####################################################################################################
####################################################################################################

tec_list, ts_list, arrival_time_list = generate_inputs_until_time(
    seed_1,
    seed_2,
    simulation_time,
    random_list_size,
    False
)

client_size = len(tec_list)

(
    server_id_list,
    service_start_time_list,
    service_end_time_list,
    line_time_list,
    system_time_list,
    worker_idle_time_list,
    server_idle_time_matrix,
    server_idle_total_list
) = simulate_mm_s(
    arrival_time_list,
    ts_list,
    server_count,
    simulation_time,
    False
)

export_spreadsheet(
    f"simulador_MADSC_mm{server_count}.xlsx",
    client_size,
    server_count,
    server_id_list,
    tec_list,
    ts_list,
    arrival_time_list,
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
