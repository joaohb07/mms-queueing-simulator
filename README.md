# Simulador de Fila M/M/s

Este projeto implementa um simulador estocástico de sistemas de filas do tipo **M/M/s**, desenvolvido em Python para a disciplina de **Modelagem e Avaliação de Sistemas Computacionais**.

O simulador permite analisar uma fila única com múltiplos servidores em paralelo, considerando tempos entre chegadas e tempos de serviço gerados a partir de distribuições exponenciais negativas.

---

## 1. Objetivo

O objetivo do simulador é avaliar o comportamento de sistemas de filas com diferentes quantidades de servidores, permitindo comparar configurações como:

- M/M/1
- M/M/2
- M/M/3
- M/M/4

A partir da simulação, são calculadas medidas como:

- Tempo médio de espera na fila;
- Tempo médio de serviço;
- Tempo médio no sistema;
- Tempo médio ocioso dos servidores;
- Quantidade de clientes atendidos;
- Dados detalhados de cada cliente simulado.

---

## 2. Estrutura dos arquivos

O projeto está organizado nos seguintes arquivos principais:

```text
.
├── main.py
├── simulador_mms.py
├── exportador_planilha.py
└── README.md
```

### `main.py`

Arquivo principal de execução do simulador.

Ele solicita ao usuário os parâmetros necessários, chama as funções de simulação e gera a planilha final com os resultados.

### `simulador_mms.py`

Contém as funções principais da simulação M/M/s, incluindo:

- geração de números pseudoaleatórios;
- geração dos tempos entre chegadas;
- geração dos tempos de serviço;
- cálculo dos horários de chegada;
- escolha do servidor disponível;
- cálculo dos tempos de fila, serviço, sistema e ociosidade.

### `exportador_planilha.py`

Responsável por exportar os resultados da simulação para uma planilha `.xlsx`.

A planilha contém os dados detalhados de cada cliente, como:

- servidor que realizou o atendimento;
- tempo entre chegadas;
- tempo de serviço;
- instante de chegada;
- início do serviço;
- fim do serviço;
- tempo na fila;
- tempo no sistema;
- tempo ocioso dos servidores;
- médias finais.

---

## 3. Requisitos

Para executar o simulador, é necessário ter o **Python 3** instalado.

Não é necessário instalar bibliotecas externas para a execução principal do simulador.

O exportador de planilha utiliza apenas bibliotecas padrão do Python, como:

- `zipfile`;
- `pathlib`;
- `xml.sax.saxutils`;
- `math`.

---

## 4. Como executar o simulador

No terminal, dentro da pasta do projeto, execute o comando:

```bash
python3 main.py
```

Em alguns sistemas, o comando também pode ser:

```bash
python main.py
```

---

## 5. Parâmetros solicitados

Ao executar o programa, o simulador solicita os seguintes valores:

```text
Informe a semente 1:
Informe a semente 2:
Informe a quantidade de servidores:
Informe o tamanho da lista aleatoria:
```

### Semente 1

A primeira semente é usada para gerar a sequência de números pseudoaleatórios associada aos **tempos entre chegadas** dos clientes.

### Semente 2

A segunda semente é usada para gerar a sequência de números pseudoaleatórios associada aos **tempos de serviço**.

### Quantidade de servidores

Define a quantidade de servidores em paralelo no sistema.

Exemplos:

```text
1 → M/M/1
2 → M/M/2
3 → M/M/3
4 → M/M/4
```

### Tamanho da lista aleatória

Define quantos números pseudoaleatórios serão gerados inicialmente.

Esse valor deve ser maior que 1000, conforme validação feita no programa.

---

## 6. Exemplo de execução

Exemplo para simular um sistema M/M/2:

```bash
python3 main.py
```

Entradas:

```text
Informe a semente 1: 10
Informe a semente 2: 12
Informe a quantidade de servidores: 2
Informe o tamanho da lista aleatoria: 1000
```

Ao final da execução, será gerada uma planilha na pasta `planilhas/`.

Exemplo de arquivo gerado:

```text
planilhas/simulador_MADSC_mm2.xlsx
```

---

## 7. Funcionamento da simulação

O simulador considera uma fila única com múltiplos servidores em paralelo.

Cada cliente chega ao sistema em determinado instante. Caso exista algum servidor disponível, o atendimento começa imediatamente. Caso todos os servidores estejam ocupados, o cliente aguarda na fila.

Para cada cliente, o programa calcula:

- tempo entre chegadas;
- tempo de serviço;
- instante de chegada;
- início do atendimento;
- fim do atendimento;
- tempo de espera na fila;
- tempo total no sistema;
- servidor responsável pelo atendimento;
- tempo ocioso associado ao servidor.

O servidor escolhido para cada cliente é aquele que estiver disponível primeiro. Em caso de empate, é escolhido o servidor de menor número.

---

## 8. Geração dos números pseudoaleatórios

O simulador utiliza um gerador congruencial linear de Park-Miller, definido por:

```text
x(i+1) = (a * x(i) + c) mod M
```

Com os seguintes parâmetros:

```text
a = 16807
c = 0
M = 2^31 - 1
```

A partir dos valores gerados, são obtidos números uniformes no intervalo entre 0 e 1.

Esses números são usados para gerar as variáveis exponenciais negativas utilizadas no modelo.

---

## 9. Distribuições utilizadas

O tempo entre chegadas dos clientes é gerado por:

```text
TEC = -ln(U) / 0,5
```

O tempo de serviço é gerado por:

```text
TS = -ln(U) / 0,125
```

Onde:

```text
U = número pseudoaleatório uniforme entre 0 e 1
```

Assim:

- o tempo médio entre chegadas é igual a 2 unidades de tempo;
- o tempo médio de serviço é igual a 8 unidades de tempo.

---

## 10. Tempo de simulação

O simulador utiliza um horizonte fixo de simulação de:

```text
300 unidades de tempo
```

As chegadas são geradas sucessivamente até que a próxima chegada ultrapasse esse tempo máximo. Quando isso ocorre, a chegada é descartada e a simulação termina.

---

## 11. Saída gerada

Após a execução, o programa gera automaticamente uma planilha `.xlsx` contendo os resultados da simulação.

A planilha é salva na pasta:

```text
planilhas/
```

O nome do arquivo depende da quantidade de servidores informada.

Exemplos:

```text
simulador_MADSC_mm1.xlsx
simulador_MADSC_mm2.xlsx
simulador_MADSC_mm3.xlsx
simulador_MADSC_mm4.xlsx
```

---
