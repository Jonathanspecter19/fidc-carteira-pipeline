# RESPOSTAS.md — Teste FIDC

## 1. No Bloco 1, quais problemas você encontrou nos dados? Como tratou e por quê?

No Bloco 1, li o arquivo `carteira.csv` com `pandas`, usando `;` como separador e informando manualmente os nomes das colunas, porque o cabeçalho não estava no início do arquivo.

Durante a limpeza, encontrei estes problemas:

- **Cabeçalho fora do lugar:** havia uma linha de cabeçalho no final do arquivo. Removi essa linha porque ela não era um registro da carteira e atrapalharia as conversões de tipo.
- **Registro duplicado:** encontrei o `id = 6` duplicado. Mantive a primeira ocorrência e removi a repetida, para não contar o mesmo título duas vezes.
- **Valor nominal vazio:** o registro `id = 18` estava sem `valor_nominal`. Removi esse registro porque esse campo é necessário para calcular valor total, inadimplência e agrupamentos.
- **Valores em formato brasileiro:** converti `valor_nominal` de texto para número, trocando vírgula por ponto.
- **Datas em formato brasileiro:** converti `data_aquisicao` e `data_vencimento` para formato de data, pois precisava comparar vencimentos com a data-base.
- **CPF/CNPJ como texto:** mantive `cpf_cnpj` como texto para não perder zeros à esquerda.

Depois da limpeza, a carteira ficou com **199 registros válidos para processamento**.

---

## 2. Explique o algoritmo que você implementou para validar CPF e CNPJ.

Implementei a validação de CPF e CNPJ manualmente, sem usar biblioteca externa.

Primeiro, o código verifica o tamanho do documento:

- 11 dígitos: valida como CPF;
- 14 dígitos: valida como CNPJ;
- qualquer outro tamanho: considera inválido.

Também tratei documentos com todos os dígitos iguais, como `00000000000` ou `11111111111`, como inválidos.

No CPF, calculei os dois dígitos verificadores usando os pesos de 10 até 2 para o primeiro dígito e de 11 até 2 para o segundo. Depois comparei os dígitos calculados com os dois últimos dígitos do CPF informado.

No CNPJ, usei a mesma ideia, mas com os pesos próprios do CNPJ. Para o primeiro dígito usei os pesos `5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2`. Para o segundo, usei `6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2`.

Os documentos inválidos não foram removidos. Eles ficaram na carteira com a coluna `documento_invalido = True`, como o teste pediu.

---

## 3. Quais inconsistências lógicas você implementou e por que escolheu essas?

Implementei regras simples, ligadas diretamente aos campos disponíveis na base. Usei as mesmas regras no Bloco 3 e na classe `DireitoCreditorio`.

As inconsistências foram:

- **Data de vencimento anterior à data de aquisição:** escolhi essa regra porque não faz sentido um título vencer antes de ser adquirido.
- **Status `a_vencer` com vencimento antes de 01/01/2026:** nesse caso, o status entra em conflito com a data-base usada no teste.
- **Status `vencido` com vencimento em 01/01/2026 ou depois:** considerando a data-base, esse título ainda não deveria estar vencido.
- **Valor nominal menor ou igual a zero:** um direito creditório precisa ter valor positivo.
- **Número de parcela menor ou igual a zero:** a parcela deve ser um número inteiro positivo.

Escolhi essas regras porque são objetivas, fáceis de justificar e não dependem de informações que não estavam no arquivo.

---

## 4. No método `taxa_inadimplencia()`, o que acontece se a carteira estiver vazia?

No método `taxa_inadimplencia()`, primeiro calculo o valor total da carteira.

Se o valor total for zero, o método retorna `0`. Fiz isso para evitar erro de divisão por zero.

Se houver valor na carteira, o método soma os títulos com status `inadimplente`, divide pelo valor total e multiplica por 100 para chegar ao percentual.

---

## 5. Se o pipeline rodasse diariamente, o que você mudaria?

Se esse pipeline fosse rodar todos os dias, eu organizaria melhor o código em funções separadas para leitura, limpeza, validação, análise e geração do relatório.

Também adicionaria logs para registrar o que aconteceu em cada execução, como quantidade de registros lidos, problemas encontrados e horário de início e fim.

Outra melhoria seria deixar o caminho do arquivo de entrada e do relatório de saída parametrizados, para não precisar alterar o código todos os dias.

Também criaria uma validação inicial para verificar se o arquivo existe e se tem as colunas esperadas. Para automatizar, poderia usar o Agendador de Tarefas do Windows, cron ou uma ferramenta da empresa.

---

## 6. Se a carteira tivesse 10 milhões de linhas, o que mudaria?

Com 10 milhões de linhas, eu evitaria carregar tudo de uma vez na memória.

Uma alternativa seria ler o arquivo em partes usando `chunksize` no `pandas`, processando pequenos blocos e consolidando os resultados no final.

Também tentaria validar documentos únicos apenas uma vez, porque muitos cedentes podem se repetir. Isso reduziria o tempo de processamento.

Para os agrupamentos por status e cedente, eu acumularia os resultados por lote e juntaria tudo no final.

O relatório JSON também teria apenas dados consolidados, e não detalhes linha a linha. Se o volume fosse frequente, avaliaria usar banco de dados ou outra ferramenta mais adequada para grandes volumes.

