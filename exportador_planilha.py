####################################################################################################
####################################################################################################
# ==================================================================================================
#                                    EXPORTADOR DE PLANILHA .XLSX
# ==================================================================================================
# Cria a planilha final sem bibliotecas externas.
# Um arquivo .xlsx é um ZIP com arquivos XML no padrão Office Open XML.
####################################################################################################
####################################################################################################
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape
####################################################################################################
####################################################################################################
# --------------------------------------------------------------------------------------------------
#                                    REFERÊNCIA DE CÉLULA DO EXCEL
# --------------------------------------------------------------------------------------------------
# Exemplo: linha 2, coluna 3 -> C2.
####################################################################################################
####################################################################################################
def cell_reference(row, column):
    """
    Converte linha e coluna numéricas para referência de célula do Excel.
    """

    column_name = ""

    while column > 0:
        column, remainder = divmod(column - 1, 26)
        column_name = chr(65 + remainder) + column_name

    return f"{column_name}{row}"
####################################################################################################
####################################################################################################
# --------------------------------------------------------------------------------------------------
#                                   CÉLULAS NO XML DA PLANILHA
# --------------------------------------------------------------------------------------------------
# Funções pequenas para montar células de texto, decimal e inteiro.
####################################################################################################
####################################################################################################
def text_cell(row, column, value, style):
    """
    Cria uma célula de texto. escape() protege caracteres especiais do XML.
    """

    reference = cell_reference(row, column)
    safe_value = escape(str(value))

    return (
        f'<c r="{reference}" t="inlineStr" s="{style}">'
        f"<is><t>{safe_value}</t></is>"
        f"</c>"
    )


def number_cell(row, column, value, style):
    """
    Cria uma célula numérica decimal com 5 casas.
    """

    reference = cell_reference(row, column)

    return f'<c r="{reference}" s="{style}"><v>{value:.5f}</v></c>'


def integer_cell(row, column, value, style):
    """
    Cria uma célula numérica inteira.
    """

    reference = cell_reference(row, column)

    return f'<c r="{reference}" s="{style}"><v>{value}</v></c>'
####################################################################################################
####################################################################################################
# --------------------------------------------------------------------------------------------------
#                                     FUNÇÃO AUXILIAR DE MÉDIA
# --------------------------------------------------------------------------------------------------
####################################################################################################
####################################################################################################
def average_list(values):
    """
    Calcula a média de uma lista. Retorna 0 para lista vazia.
    """

    if len(values) == 0:
        return 0
    return sum(values) / len(values)
####################################################################################################
####################################################################################################
# --------------------------------------------------------------------------------------------------
#                                     EXPORTAÇÃO DA PLANILHA
# --------------------------------------------------------------------------------------------------
# Organização:
#   linha 1: cabeçalho.
#   linhas 2 até client_size + 1: dados dos clientes.
#   linha client_size + 3: médias.
####################################################################################################
####################################################################################################
def export_spreadsheet(
    filename,
    client_size,
    server_count,
    server_id_list,
    tec_list,
    ts_list,
    arrival_time_list,
    service_start_time_list,
    service_end_time_list,
    line_time_list,
    sistem_time_list,
    worker_idle_time_list,
    server_idle_time_matrix,
    server_idle_total_list
):
    """
    Exporta os resultados da simulação para uma planilha .xlsx.

    Se filename vier sem pasta, o arquivo é salvo em planilhas/.
    A planilha contém cabeçalho, uma linha por cliente e uma linha de médias.
    """

    # Cria o caminho do arquivo de saída.
    output_path = Path(filename)

    # Se o usuário não especificou pasta, cria planilhas/ e salva lá.
    if output_path.parent == Path("."):
        output_path = Path("planilhas") / output_path
    
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Cabeçalho da planilha, com uma coluna de ociosidade para cada servidor.
    headers = [
        "Clientes",
        "Servidor",
        "TEC",
        "TS",
        "Tempo de\nchegada no\nrelógio",
        "Tempo início\nserviço",
        "Tempo final\nserviço",
        "Tempo na fila",
        "Tempo no\nsistema",
        "Tempo ocioso\nservidor que\natendeu"
    ]

    # Uma coluna de ociosidade para cada servidor.
    for server_number in range(1, server_count + 1):
        headers.append(f"Tempo ocioso\nServidor {server_number}")

    # A última coluna é a de ociosidade do último servidor.
    last_column = len(headers)

    # Deixa uma linha em branco antes da linha de médias.
    average_row = client_size + 3
    last_cell = cell_reference(average_row, last_column)

    rows = []

    # Cabeçalho com quebra de linha em alguns títulos.
    rows.append(
        '<row r="1" ht="58" customHeight="1">'
        + "".join(text_cell(1, column + 1, header, 1) for column, header in enumerate(headers))
        + "</row>"
    )

    # Linhas dos clientes simulados.
    # A linha 1 é o cabeçalho; por isso o cliente i começa na linha i + 2.
    for i in range(client_size):
        row_number = i + 2

        # Valores que sempre existem, independentemente da quantidade de
        # servidores. Eles começam na coluna C, pois A é o cliente e B é o
        # servidor escolhido.
        fixed_values = [
            tec_list[i],
            ts_list[i],
            arrival_time_list[i],
            service_start_time_list[i],
            service_end_time_list[i],
            line_time_list[i],
            sistem_time_list[i],
            worker_idle_time_list[i]
        ]

        # A partir da coluna K, cada servidor tem uma coluna de ociosidade. O
        # servidor escolhido para o cliente i é server_id_list[i], que vai de 1
        # a server_count. A lista server_idle_time_matrix[i] tem ociosidade para
        # todos os servidores, mas só o escolhido recebe valor; os outros são 0.
        rows.append(
            f'<row r="{row_number}">'
            + integer_cell(row_number, 1, i + 1, 2)
            + integer_cell(row_number, 2, server_id_list[i], 4)
            # Colunas C até J: tempos principais do cliente.
            + "".join(
                number_cell(row_number, column + 3, value, 3)
                for column, value in enumerate(fixed_values)
            )
            # A partir da coluna K: uma coluna de ociosidade para cada servidor.
            + "".join(
                number_cell(row_number, 11 + server_index, server_idle_time_matrix[i][server_index], 3)
                for server_index in range(server_count)
            )
            + "</row>"
        )

    # Médias das colunas fixas C até J. A ordem precisa ser a mesma de
    # fixed_values para que cada média caia na coluna correta.
    average_values = [
        average_list(tec_list),
        average_list(ts_list),
        average_list(arrival_time_list),
        average_list(service_start_time_list),
        average_list(service_end_time_list),
        average_list(line_time_list),
        average_list(sistem_time_list),
        average_list(worker_idle_time_list)
    ]

    # Média de ociosidade por servidor. O total já inclui a ociosidade final
    # até simulation_time, mas a planilha mostra apenas a média.
    server_idle_average_list = [
        server_idle_total_list[server_index] / client_size
        for server_index in range(server_count)
    ]

    # Linha final de médias:
    # - Coluna A recebe o rótulo "Média".
    # - Coluna B recebe "-" porque servidor é uma identificação, não uma média.
    # - Colunas C em diante recebem as médias numéricas.
    rows.append(
        f'<row r="{average_row}">'
        + text_cell(average_row, 1, "Média", 1)
        + text_cell(average_row, 2, "-", 4)
        + "".join(
            number_cell(average_row, column + 3, value, 3)
            for column, value in enumerate(average_values)
        )
        + "".join(
            number_cell(average_row, 11 + server_index, server_idle_average_list[server_index], 3)
            for server_index in range(server_count)
        )
        + "</row>"
    )

    # XML da aba principal da planilha.
    # Aqui ficam o intervalo usado, as larguras das colunas e todas as linhas
    # montadas anteriormente em rows.
    sheet_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <dimension ref="A1:{last_cell}"/>
  <sheetViews>
    <sheetView workbookViewId="0"/>
  </sheetViews>
  <sheetFormatPr defaultRowHeight="18"/>
  <cols>
    <col min="1" max="1" width="11" customWidth="1"/>
    <col min="2" max="2" width="11" customWidth="1"/>
    <col min="3" max="4" width="15" customWidth="1"/>
    <col min="5" max="10" width="20" customWidth="1"/>
    <col min="11" max="{last_column}" width="18" customWidth="1"/>
  </cols>
  <sheetData>
    {''.join(rows)}
  </sheetData>
</worksheet>
'''

    # XML de estilos.
    # Define formatos reutilizáveis pelas células:
    # - numFmtId 164: números com 5 casas decimais.
    # - fonts: fonte normal, fonte branca em negrito e fonte branca normal.
    # - fills: preenchimentos usados no cabeçalho e em células destacadas.
    # - borders: borda fina cinza nas células da tabela.
    # - cellXfs: estilos finais referenciados pelo parâmetro s="..." das células.
    styles_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <numFmts count="1">
    <numFmt numFmtId="164" formatCode="0.00000"/>
  </numFmts>
  <fonts count="3">
    <font><sz val="11"/><name val="Calibri"/></font>
    <font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font>
    <font><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font>
  </fonts>
  <fills count="4">
    <fill><patternFill patternType="none"/></fill>
    <fill><patternFill patternType="gray125"/></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FF999999"/><bgColor indexed="64"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FF3F3F3F"/><bgColor indexed="64"/></patternFill></fill>
  </fills>
  <borders count="2">
    <border><left/><right/><top/><bottom/><diagonal/></border>
    <border>
      <left style="thin"><color rgb="FF808080"/></left>
      <right style="thin"><color rgb="FF808080"/></right>
      <top style="thin"><color rgb="FF808080"/></top>
      <bottom style="thin"><color rgb="FF808080"/></bottom>
      <diagonal/>
    </border>
  </borders>
  <cellStyleXfs count="1">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0"/>
  </cellStyleXfs>
  <cellXfs count="5">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
    <xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">
      <alignment horizontal="center" vertical="center" wrapText="1"/>
    </xf>
    <xf numFmtId="0" fontId="2" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">
      <alignment horizontal="center" vertical="center"/>
    </xf>
    <xf numFmtId="164" fontId="0" fillId="0" borderId="1" xfId="0" applyNumberFormat="1" applyBorder="1" applyAlignment="1">
      <alignment horizontal="right" vertical="center"/>
    </xf>
    <xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1" applyAlignment="1">
      <alignment horizontal="center" vertical="center"/>
    </xf>
  </cellXfs>
  <cellStyles count="1">
    <cellStyle name="Normal" xfId="0" builtinId="0"/>
  </cellStyles>
</styleSheet>
'''

    # XML da pasta de trabalho.
    # Indica que o arquivo terá uma aba chamada "Simulador".
    workbook_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
    <sheet name="Simulador" sheetId="1" r:id="rId1"/>
  </sheets>
</workbook>
'''

    # Relações internas da pasta de trabalho.
    # Conecta a aba "Simulador" ao arquivo sheet1.xml e conecta os estilos ao
    # arquivo styles.xml.
    workbook_rels_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>
'''

    # Relação principal do pacote .xlsx.
    # Diz ao Excel que o arquivo principal da pasta de trabalho está em
    # xl/workbook.xml.
    rels_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>
'''

    # Tipos de conteúdo do pacote.
    # Informa ao Excel quais arquivos XML existem dentro do ZIP e qual é o
    # papel de cada um deles.
    content_types_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
</Types>
'''

    # Cria o .xlsx como um arquivo ZIP e grava cada XML no caminho esperado
    # pelo padrão Office Open XML.
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as spreadsheet:
        spreadsheet.writestr("[Content_Types].xml", content_types_xml)
        spreadsheet.writestr("_rels/.rels", rels_xml)
        spreadsheet.writestr("xl/workbook.xml", workbook_xml)
        spreadsheet.writestr("xl/_rels/workbook.xml.rels", workbook_rels_xml)
        spreadsheet.writestr("xl/worksheets/sheet1.xml", sheet_xml)
        spreadsheet.writestr("xl/styles.xml", styles_xml)

    print(f"Exported spreadsheet: {output_path}")
####################################################################################################
####################################################################################################
