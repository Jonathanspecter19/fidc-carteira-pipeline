import pandas as pd


class DireitoCreditorio:
    """
    Classe que representa um único direito creditório da carteira.
    """

    def __init__(
        self,
        id,
        cedente,
        cpf_cnpj,
        sacado,
        valor_nominal,
        data_aquisicao,
        data_vencimento,
        status,
        numero_parcela
    ):
        self.id = id
        self.cedente = cedente
        self.cpf_cnpj = cpf_cnpj
        self.sacado = sacado
        self.valor_nominal = valor_nominal
        self.data_aquisicao = data_aquisicao
        self.data_vencimento = data_vencimento
        self.status = status
        self.numero_parcela = numero_parcela

        # Data-base definida no enunciado do teste.
        self.data_base = pd.to_datetime("01/01/2026", format="%d/%m/%Y")


    def esta_vencido(self):
        """
        Retorna True se o título estiver vencido pela data-base.
        """
        return self.data_vencimento < self.data_base


    def dias_em_atraso(self):
        """
        Retorna a quantidade de dias em atraso.
        Se não estiver vencido, retorna 0.
        """
        if self.esta_vencido():
            diferenca = self.data_base - self.data_vencimento
            return diferenca.days

        return 0


    def inconsistencias(self):
        """
        Retorna uma lista com as inconsistências encontradas no título.
        """
        problemas = []

        if self.data_vencimento < self.data_aquisicao:
            problemas.append("Data de vencimento anterior à data de aquisição")

        if self.status == "a_vencer" and self.data_vencimento < self.data_base:
            problemas.append("Status a_vencer com data de vencimento anterior à data-base")

        if self.status == "vencido" and self.data_vencimento >= self.data_base:
            problemas.append("Status vencido com data de vencimento igual ou posterior à data-base")

        if self.valor_nominal <= 0:
            problemas.append("Valor nominal menor ou igual a zero")

        if self.numero_parcela <= 0:
            problemas.append("Número da parcela menor ou igual a zero")

        return problemas


    def tem_inconsistencia(self):
        """
        Retorna True se existir pelo menos uma inconsistência.
        """
        return len(self.inconsistencias()) > 0



class Carteira:
    """
    Classe que representa uma carteira com vários direitos creditórios.
    """

    def __init__(self, nome, direitos):
        self.nome = nome
        self.direitos = direitos


    def valor_total(self):
        """
        Soma o valor nominal de todos os direitos creditórios.
        """
        total = 0

        for direito in self.direitos:
            total += direito.valor_nominal

        return total


    def taxa_inadimplencia(self):
        """
        Calcula o percentual do valor inadimplente sobre o valor total da carteira.
        """
        total = self.valor_total()

        if total == 0:
            return 0

        valor_inadimplente = 0

        for direito in self.direitos:
            if direito.status == "inadimplente":
                valor_inadimplente += direito.valor_nominal

        return (valor_inadimplente / total) * 100


    def titulos_vencidos(self):
        """
        Retorna uma lista com os títulos vencidos pela data-base.
        """
        vencidos = []

        for direito in self.direitos:
            if direito.esta_vencido():
                vencidos.append(direito)

        return vencidos


    def relatorio_por_cedente(self):
        """
        Agrupa os títulos por cedente, calculando quantidade e valor total.
        """
        relatorio = {}

        for direito in self.direitos:
            cedente = direito.cedente

            if cedente not in relatorio:
                relatorio[cedente] = {
                    "quantidade": 0,
                    "valor_total": 0
                }

            relatorio[cedente]["quantidade"] += 1
            relatorio[cedente]["valor_total"] += direito.valor_nominal

        return relatorio


    def inconsistencias(self):
        """
        Retorna os direitos creditórios que possuem alguma inconsistência.
        """
        lista_inconsistentes = []

        for direito in self.direitos:
            if direito.tem_inconsistencia():
                lista_inconsistentes.append(direito)

        return lista_inconsistentes