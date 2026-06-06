import pandas as pd
import json
from datetime import datetime
from modelos import DireitoCreditorio, Carteira

# Lista para guardar os problemas encontrados durante a limpeza.
alertas = []

# Como o arquivo não tem cabeçalho correto no início,
# informamos manualmente o nome das colunas.
colunas = [
    "id",
    "cedente",
    "cpf_cnpj",
    "sacado",
    "valor_nominal",
    "data_aquisicao",
    "data_vencimento",
    "status",
    "numero_parcela"
]

print("Lendo o arquivo carteira.csv...")

# Leitura do arquivo.
# sep=";" porque o CSV usa ponto e vírgula.
# header=None porque o cabeçalho está fora do lugar.
# dtype=str para ler tudo como texto no início e preservar zeros no CPF/CNPJ.
df = pd.read_csv(
    "carteira.csv",
    sep=";",
    header=None,
    names=colunas,
    dtype=str
)

print(f"Total de linhas lidas: {len(df)}")

# 1. Remover cabeçalho fora do lugar
cabecalho_fora_do_lugar = df["id"] == "id"

if cabecalho_fora_do_lugar.any():
    print("Problema encontrado: cabeçalho fora do lugar.")
    alertas.append("Cabeçalho fora do lugar removido.")
    df = df[~cabecalho_fora_do_lugar]

# 2. Remover espaços extras dos textos
for coluna in df.columns:
    df[coluna] = df[coluna].str.strip()

print("Espaços extras removidos dos campos de texto.")

# 3. Remover registros duplicados pelo id
duplicados = df[df.duplicated(subset="id", keep=False)]

if not duplicados.empty:
    ids_duplicados = duplicados["id"].unique().tolist()
    print(f"Problema encontrado: ids duplicados {ids_duplicados}")
    alertas.append(f"Registros duplicados removidos: {ids_duplicados}")
    df = df.drop_duplicates(subset="id", keep="first")

# 4. Remover registros com valor_nominal vazio
valor_vazio = df["valor_nominal"].isna() | (df["valor_nominal"] == "")

if valor_vazio.any():
    ids_valor_vazio = df.loc[valor_vazio, "id"].tolist()
    print(f"Problema encontrado: valor_nominal vazio nos ids {ids_valor_vazio}")
    alertas.append(f"Registros removidos por valor_nominal vazio: {ids_valor_vazio}")
    df = df[~valor_vazio]

# 5. Converter valor_nominal para número
df["valor_nominal"] = (
    df["valor_nominal"]
    .str.replace(".", "", regex=False)
    .str.replace(",", ".", regex=False)
    .astype(float)
)

print("valor_nominal convertido para número.")

# 6. Converter datas
df["data_aquisicao"] = pd.to_datetime(
    df["data_aquisicao"],
    format="%d/%m/%Y"
)

df["data_vencimento"] = pd.to_datetime(
    df["data_vencimento"],
    format="%d/%m/%Y"
)

print("Datas convertidas.")

# 7. Converter id e numero_parcela para inteiro
df["id"] = df["id"].astype(int)
df["numero_parcela"] = df["numero_parcela"].astype(int)

print("id e numero_parcela convertidos para inteiro.")

# 8. Manter cpf_cnpj como texto
df["cpf_cnpj"] = df["cpf_cnpj"].astype(str)

print("cpf_cnpj mantido como texto.")

# 9. Resetar índice
df = df.reset_index(drop=True)

print("\nLimpeza concluída.")
print(f"Total de registros após limpeza: {len(df)}")

print("\nAlertas encontrados:")
for alerta in alertas:
    print(f"- {alerta}")

print("\nPrévia dos dados limpos:")
print(df.head())


# ============================================================
# BLOCO 2 — VALIDAÇÃO DE CPF E CNPJ
# ============================================================

def todos_digitos_iguais(documento):
    return len(set(documento)) == 1


def validar_cpf(cpf):
    cpf = str(cpf)

    if len(cpf) != 11 or todos_digitos_iguais(cpf):
        return False

    soma = 0
    peso = 10

    for i in range(9):
        soma += int(cpf[i]) * peso
        peso -= 1

    resto = soma % 11

    if resto < 2:
        primeiro_digito = 0
    else:
        primeiro_digito = 11 - resto

    soma = 0
    peso = 11

    for i in range(10):
        soma += int(cpf[i]) * peso
        peso -= 1

    resto = soma % 11

    if resto < 2:
        segundo_digito = 0
    else:
        segundo_digito = 11 - resto

    return cpf[-2:] == f"{primeiro_digito}{segundo_digito}"


def validar_cnpj(cnpj):
    cnpj = str(cnpj)

    if len(cnpj) != 14 or todos_digitos_iguais(cnpj):
        return False

    pesos_primeiro = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    soma = 0

    for i in range(12):
        soma += int(cnpj[i]) * pesos_primeiro[i]

    resto = soma % 11

    if resto < 2:
        primeiro_digito = 0
    else:
        primeiro_digito = 11 - resto

    pesos_segundo = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    soma = 0

    for i in range(13):
        soma += int(cnpj[i]) * pesos_segundo[i]

    resto = soma % 11

    if resto < 2:
        segundo_digito = 0
    else:
        segundo_digito = 11 - resto

    return cnpj[-2:] == f"{primeiro_digito}{segundo_digito}"


def validar_documento(documento):
    documento = str(documento)

    if len(documento) == 11:
        return validar_cpf(documento)

    if len(documento) == 14:
        return validar_cnpj(documento)

    return False


print("\nIniciando validação de CPF/CNPJ...")

df["documento_invalido"] = ~df["cpf_cnpj"].apply(validar_documento)

total_invalidos = df["documento_invalido"].sum()

print(f"Total de documentos inválidos encontrados: {total_invalidos}")

if total_invalidos > 0:
    ids_invalidos = df.loc[df["documento_invalido"], "id"].tolist()

    print("Problema encontrado: existem documentos inválidos na carteira.")
    print(f"IDs com documento inválido: {ids_invalidos}")

    alertas.append(f"Documentos inválidos encontrados em {total_invalidos} registro(s).")

print("\nPrévia com a coluna documento_invalido:")
print(df[["id", "cedente", "cpf_cnpj", "documento_invalido"]].head())

# ============================================================
# BLOCO 3 — ANÁLISE DA CARTEIRA
# ============================================================

print("\nIniciando análise da carteira...")

# Data-base informada no enunciado para verificar títulos vencidos.
data_base = pd.to_datetime("01/01/2026", format="%d/%m/%Y")

# ------------------------------------------------------------
# 1. Valor total da carteira
# ------------------------------------------------------------

valor_total_carteira = df["valor_nominal"].sum()

print(f"Valor total da carteira: R$ {valor_total_carteira:,.2f}")

# ------------------------------------------------------------
# 2. Títulos vencidos pela data-base
# ------------------------------------------------------------

titulos_vencidos = df[df["data_vencimento"] < data_base]

quantidade_vencidos = len(titulos_vencidos)
valor_vencidos = titulos_vencidos["valor_nominal"].sum()

print(f"Quantidade de títulos vencidos pela data-base: {quantidade_vencidos}")
print(f"Valor total dos títulos vencidos: R$ {valor_vencidos:,.2f}")

# ------------------------------------------------------------
# 3. Taxa de inadimplência
# ------------------------------------------------------------

titulos_inadimplentes = df[df["status"] == "inadimplente"]

valor_inadimplente = titulos_inadimplentes["valor_nominal"].sum()

if valor_total_carteira > 0:
    taxa_inadimplencia = (valor_inadimplente / valor_total_carteira) * 100
else:
    taxa_inadimplencia = 0

print(f"Taxa de inadimplência: {taxa_inadimplencia:.2f}%")

# ------------------------------------------------------------
# 4. Resumo por status
# ------------------------------------------------------------

resumo_por_status = df.groupby("status").agg(
    quantidade=("id", "count"),
    valor_total=("valor_nominal", "sum")
)

print("\nResumo por status:")
print(resumo_por_status)

# ------------------------------------------------------------
# 5. Resumo por cedente
# ------------------------------------------------------------

resumo_por_cedente = df.groupby("cedente").agg(
    quantidade=("id", "count"),
    valor_total=("valor_nominal", "sum")
)

print("\nResumo por cedente:")
print(resumo_por_cedente.head())

# ------------------------------------------------------------
# 6. Inconsistências lógicas
# ------------------------------------------------------------

def verificar_inconsistencias(linha):
    """
    Verifica inconsistências simples e explicáveis entre os campos.
    Retorna uma lista com os problemas encontrados no registro.
    """

    problemas = []

    # Regra 1: vencimento antes da aquisição.
    if linha["data_vencimento"] < linha["data_aquisicao"]:
        problemas.append("Data de vencimento anterior à data de aquisição")

    # Regra 2: status a_vencer, mas vencimento anterior à data-base.
    if linha["status"] == "a_vencer" and linha["data_vencimento"] < data_base:
        problemas.append("Status a_vencer com data de vencimento anterior à data-base")

    # Regra 3: status vencido, mas vencimento igual ou posterior à data-base.
    if linha["status"] == "vencido" and linha["data_vencimento"] >= data_base:
        problemas.append("Status vencido com data de vencimento igual ou posterior à data-base")

    # Regra 4: valor nominal menor ou igual a zero.
    if linha["valor_nominal"] <= 0:
        problemas.append("Valor nominal menor ou igual a zero")

    # Regra 5: número da parcela menor ou igual a zero.
    if linha["numero_parcela"] <= 0:
        problemas.append("Número da parcela menor ou igual a zero")

    return problemas


# Cria uma coluna com a lista de inconsistências de cada registro.
df["inconsistencias"] = df.apply(verificar_inconsistencias, axis=1)

# Cria uma coluna booleana indicando se existe pelo menos uma inconsistência.
df["tem_inconsistencia"] = df["inconsistencias"].apply(lambda lista: len(lista) > 0)

total_inconsistencias = df["tem_inconsistencia"].sum()

print(f"\nTotal de registros com inconsistência lógica: {total_inconsistencias}")

if total_inconsistencias > 0:
    registros_inconsistentes = df[df["tem_inconsistencia"]]

    print("\nPrévia dos registros com inconsistência:")
    print(registros_inconsistentes[["id", "status", "data_aquisicao", "data_vencimento", "inconsistencias"]].head())

    alertas.append(f"Foram encontrados {total_inconsistencias} registro(s) com inconsistência lógica.")

    # ============================================================
# BLOCO 4 — TESTE DA MODELAGEM ORIENTADA A OBJETOS
# ============================================================

print("\nIniciando teste da modelagem orientada a objetos...")

# Lista que vai guardar os objetos DireitoCreditorio.
direitos = []

# Para cada linha do DataFrame, criamos um objeto DireitoCreditorio.
for _, linha in df.iterrows():
    direito = DireitoCreditorio(
        id=linha["id"],
        cedente=linha["cedente"],
        cpf_cnpj=linha["cpf_cnpj"],
        sacado=linha["sacado"],
        valor_nominal=linha["valor_nominal"],
        data_aquisicao=linha["data_aquisicao"],
        data_vencimento=linha["data_vencimento"],
        status=linha["status"],
        numero_parcela=linha["numero_parcela"]
    )

    direitos.append(direito)

# Criamos a carteira com todos os direitos creditórios.
carteira_objeto = Carteira(
    nome="Carteira FIDC Teste",
    direitos=direitos
)

print(f"Nome da carteira: {carteira_objeto.nome}")
print(f"Quantidade de direitos na carteira: {len(carteira_objeto.direitos)}")
print(f"Valor total pela classe Carteira: R$ {carteira_objeto.valor_total():,.2f}")
print(f"Taxa de inadimplência pela classe Carteira: {carteira_objeto.taxa_inadimplencia():.2f}%")
print(f"Quantidade de títulos vencidos pela classe Carteira: {len(carteira_objeto.titulos_vencidos())}")
print(f"Quantidade de registros com inconsistência pela classe Carteira: {len(carteira_objeto.inconsistencias())}")

print("\nPrévia do relatório por cedente gerado pela classe Carteira:")

relatorio_cedente_objeto = carteira_objeto.relatorio_por_cedente()

# Mostra apenas os 5 primeiros cedentes para não poluir o terminal.
contador = 0

for cedente, dados in relatorio_cedente_objeto.items():
    print(cedente, dados)

    contador += 1

    if contador == 5:
        break

    # ============================================================
# BLOCO 5 — GERAÇÃO DO RELATÓRIO JSON
# ============================================================

print("\nGerando relatório JSON...")

# Resumo por status no formato de dicionário.
resumo_status_json = {}

for status, linha in resumo_por_status.iterrows():
    resumo_status_json[status] = {
        "quantidade": int(linha["quantidade"]),
        "valor_total": float(linha["valor_total"])
    }


# Resumo por cedente no formato de dicionário.
# Aqui também calculamos o percentual de cada cedente sobre o total da carteira.
resumo_cedente_json = {}

relatorio_cedente = carteira_objeto.relatorio_por_cedente()

for cedente, dados in relatorio_cedente.items():
    valor_cedente = dados["valor_total"]

    if valor_total_carteira > 0:
        percentual = (valor_cedente / valor_total_carteira) * 100
    else:
        percentual = 0

    resumo_cedente_json[cedente] = {
        "quantidade": int(dados["quantidade"]),
        "valor_total": float(valor_cedente),
        "percentual_sobre_carteira": round(percentual, 2)
    }


# Inclui alguns alertas adicionais importantes.
alertas.append(f"Total de documentos inválidos sinalizados: {total_invalidos}.")
alertas.append(f"Total de registros com inconsistência lógica: {total_inconsistencias}.")


# Montagem final do relatório.
relatorio = {
    "data_geracao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "nome_carteira": carteira_objeto.nome,
    "total_registros": int(len(df)),
    "valor_total": float(valor_total_carteira),
    "taxa_inadimplencia_pct": round(float(taxa_inadimplencia), 2),
    "total_titulos_vencidos": int(quantidade_vencidos),
    "valor_titulos_vencidos": float(valor_vencidos),
    "resumo_por_status": resumo_status_json,
    "resumo_por_cedente": resumo_cedente_json,
    "alertas": alertas
}


# Salva o relatório em arquivo JSON.
with open("relatorio.json", "w", encoding="utf-8") as arquivo:
    json.dump(relatorio, arquivo, ensure_ascii=False, indent=4)

print("Relatório relatorio.json gerado com sucesso.")

