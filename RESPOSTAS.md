# RESPOSTAS.md — Teste FIDC

## 1. No Bloco 1, quais problemas você encontrou nos dados? Liste cada um e descreva exatamente como tratou e por que tomou essa decisão.

No Bloco 1, eu fiz a leitura do arquivo `carteira.csv` usando a biblioteca `pandas`, considerando que o arquivo estava separado por ponto e vírgula (`;`) e que o cabeçalho não estava posicionado corretamente na primeira linha.

Os problemas encontrados foram:

### Cabeçalho fora do lugar

O arquivo possuía uma linha de cabeçalho no final, contendo os nomes das colunas, como `id`, `cedente`, `cpf_cnpj`, `sacado`, `valor_nominal`, entre outros campos. Essa linha não representava um direito creditório real, por isso foi identificada quando a coluna `id` era igual a `"id"` e removida da base.

Tomei essa decisão porque manter essa linha causaria erro nas conversões de tipo, como conversão de `id` para inteiro, `valor_nominal` para número e datas para formato de data.

### Espaços extras nos campos de texto

Também padronizei os campos de texto removendo espaços antes e depois dos valores. Essa limpeza foi feita em todas as colunas lidas como texto.

A decisão foi tomada para evitar problemas em comparações, agrupamentos e validações. Por exemplo, um status `"a_vencer"` e outro `" a_vencer "` poderiam ser interpretados como valores diferentes se os espaços não fossem removidos.

### Registro duplicado

Foi encontrado um registro duplicado com o `id = 6`. Como o campo `id` deve identificar um direito creditório de forma única, removi a duplicidade mantendo a primeira ocorrência.

Tomei essa decisão para evitar que o mesmo título fosse considerado duas vezes nos cálculos de valor total da carteira, taxa de inadimplência e agrupamentos por status ou cedente.

### Valor nominal vazio

Foi encontrado um registro com `valor_nominal` vazio, no `id = 18`. Como o valor nominal é essencial para os cálculos financeiros da carteira, esse registro foi removido.

A decisão foi remover o registro porque preencher com zero ou com média poderia distorcer os resultados. Como não havia informação suficiente para estimar o valor correto, considerei mais seguro remover o registro e registrar essa decisão nos alertas.

### Conversão do valor nominal

O campo `valor_nominal` estava no padrão brasileiro, usando vírgula como separador decimal, por exemplo `15000,00`. Para permitir os cálculos em Python, substituí a vírgula por ponto e converti o campo para número decimal (`float`).

Essa decisão foi necessária para calcular soma da carteira, valores por status, valores por cedente e taxa de inadimplência.

### Conversão das datas

Os campos `data_aquisicao` e `data_vencimento` estavam em formato brasileiro (`dia/mês/ano`). Converti esses campos para tipo data usando `pd.to_datetime`.

Essa conversão foi necessária porque o teste pede a comparação da `data_vencimento` com a data-base `01/01/2026` para identificar títulos vencidos.

### Conversão de `id` e `numero_parcela`

Depois da limpeza, converti os campos `id` e `numero_parcela` para inteiro.

Fiz isso porque esses campos representam valores numéricos inteiros e essa conversão ajuda a manter os dados padronizados e prontos para processamento.

### Preservação do CPF/CNPJ como texto

Mantive o campo `cpf_cnpj` como texto, porque documentos podem começar com zero. Se esse campo fosse tratado como número, os zeros à esquerda poderiam ser perdidos.

Essa decisão foi importante para manter a integridade dos documentos antes da validação do Bloco 2.

Ao final do Bloco 1, a base ficou com 199 registros limpos, após remover o cabeçalho fora do lugar, a duplicidade e o registro com valor nominal vazio.

---

## 2. Explique o algoritmo que você implementou para validar CPF e CNPJ. Como funciona o cálculo dos dígitos verificadores em cada caso?

No Bloco 2, implementei a validação manual de CPF e CNPJ, sem utilizar bibliotecas externas. Primeiro, o código identifica o tipo de documento pelo tamanho:

- Se o documento possui 11 dígitos, ele é tratado como CPF.
- Se o documento possui 14 dígitos, ele é tratado como CNPJ.
- Se não possui 11 nem 14 dígitos, é considerado inválido.

Também implementei uma regra para rejeitar documentos com todos os dígitos iguais, como `00000000000`, `11111111111` ou `99999999999999`, pois esse tipo de sequência não deve ser considerado válido.

### Validação de CPF

O CPF possui 11 dígitos. Os 9 primeiros são a base e os 2 últimos são os dígitos verificadores.

Para calcular o primeiro dígito verificador, o algoritmo multiplica os 9 primeiros dígitos pelos pesos de 10 até 2. Depois soma os resultados e calcula o resto da divisão por 11. Se o resto for menor que 2, o dígito verificador será 0. Caso contrário, será `11 - resto`.

Depois, para calcular o segundo dígito verificador, o algoritmo usa os 9 primeiros dígitos mais o primeiro dígito calculado, multiplicando pelos pesos de 11 até 2. O processo de soma, resto da divisão por 11 e definição do dígito é o mesmo.

No final, os dois dígitos calculados são comparados com os dois últimos dígitos do CPF original. Se forem iguais, o CPF é considerado válido. Caso contrário, é considerado inválido.

### Validação de CNPJ

O CNPJ possui 14 dígitos. Os 12 primeiros são a base e os 2 últimos são os dígitos verificadores.

Para calcular o primeiro dígito verificador do CNPJ, utilizei os pesos:

`5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2`

Cada um dos 12 primeiros dígitos é multiplicado pelo peso correspondente. Depois, o algoritmo soma os resultados e calcula o resto da divisão por 11. Se o resto for menor que 2, o dígito será 0. Caso contrário, será `11 - resto`.

Para calcular o segundo dígito verificador, utilizei os pesos:

`6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2`

O cálculo segue a mesma lógica, agora considerando os 12 primeiros dígitos mais o primeiro dígito calculado.

Ao final, os dois dígitos calculados são comparados com os dois últimos dígitos do CNPJ original.

No meu código, os documentos inválidos não foram removidos da carteira. Eles foram mantidos e sinalizados com a coluna `documento_invalido = True`, conforme solicitado no enunciado.

---

## 3. Quais inconsistências lógicas entre campos você implementou no Bloco 3 e no método `tem_inconsistencia()`? Por que escolheu essas e não outras?

Implementei inconsistências simples, objetivas e ligadas diretamente aos campos existentes no arquivo. As mesmas regras foram usadas no Bloco 3 e também na classe `DireitoCreditorio`, por meio dos métodos `inconsistencias()` e `tem_inconsistencia()`.

As inconsistências implementadas foram:

### Data de vencimento anterior à data de aquisição

Essa regra verifica se `data_vencimento` é menor que `data_aquisicao`.

Escolhi essa regra porque, em uma operação normal, um direito creditório adquirido em determinada data não deveria ter uma data de vencimento anterior à data de aquisição. Quando isso acontece, existe um conflito lógico entre os campos.

### Status `a_vencer` com vencimento anterior à data-base

Essa regra verifica se o status está como `a_vencer`, mas a `data_vencimento` é anterior à data-base `01/01/2026`.

Escolhi essa regra porque, se o título já estava vencido antes da data-base, ele não deveria estar marcado como `a_vencer`.

### Status `vencido` com vencimento igual ou posterior à data-base

Essa regra verifica se o status está como `vencido`, mas a `data_vencimento` é igual ou posterior à data-base `01/01/2026`.

Escolhi essa regra porque, considerando a data-base do teste, um título com vencimento futuro não deveria estar classificado como vencido.

### Valor nominal menor ou igual a zero

Essa regra verifica se o `valor_nominal` é menor ou igual a zero.

Escolhi essa regra porque um direito creditório deve possuir valor financeiro positivo. Mesmo que o arquivo analisado não tenha apresentado esse problema após a limpeza, essa validação deixa o pipeline mais seguro.

### Número da parcela menor ou igual a zero

Essa regra verifica se `numero_parcela` é menor ou igual a zero.

Escolhi essa regra porque o número da parcela deve ser um número inteiro positivo. Uma parcela zero ou negativa não faria sentido no contexto da carteira.

Não implementei regras mais complexas porque o objetivo foi manter o código claro, coerente com uma vaga júnior e fácil de explicar. Preferi validar conflitos diretamente relacionados aos campos disponíveis no arquivo, evitando suposições que não estavam no enunciado.

---

## 4. No método `taxa_inadimplencia()` da classe `Carteira`, o que acontece se a carteira estiver vazia? Como você tratou esse caso?

No método `taxa_inadimplencia()` da classe `Carteira`, primeiro calculo o valor total da carteira usando o método `valor_total()`.

Se a carteira estiver vazia, o valor total será zero. Nesse caso, o método retorna `0`, evitando erro de divisão por zero.

A lógica usada foi:

- Calcular o valor total da carteira.
- Se o total for igual a zero, retornar `0`.
- Caso contrário, somar o valor dos títulos com status `inadimplente` e dividir pelo valor total da carteira.

Essa decisão foi tomada porque uma carteira vazia não possui valor inadimplente nem valor total para comparação. Assim, retornar zero é uma forma segura de tratar o caso sem interromper a execução do programa.

---

## 5. Se você precisasse adaptar este pipeline para rodar diariamente de forma automatizada, o que mudaria na sua implementação?

Se eu precisasse adaptar este pipeline para rodar diariamente de forma automatizada, faria algumas melhorias na organização e no controle da execução.

Primeiro, eu separaria melhor as responsabilidades do código em funções, por exemplo:

- função para leitura do arquivo;
- função para limpeza dos dados;
- função para validação de documentos;
- função para análise da carteira;
- função para geração do relatório.

Também adicionaria logs mais estruturados, registrando horário de início, horário de fim, quantidade de registros processados, problemas encontrados e se a execução terminou com sucesso ou erro.

Outra melhoria seria parametrizar o caminho do arquivo de entrada e o caminho do relatório de saída, para que o processo pudesse receber arquivos diferentes diariamente sem alterar o código.

Também criaria uma rotina de validação antes do processamento, conferindo se o arquivo existe, se possui as colunas esperadas e se está no formato correto.

Para a automação diária, o script poderia ser agendado pelo Agendador de Tarefas do Windows, cron em Linux ou por alguma ferramenta de orquestração, dependendo do ambiente da empresa.

Além disso, eu manteria os relatórios gerados com nome contendo a data de execução, por exemplo `relatorio_2026_06_06.json`, para preservar o histórico diário.

Por fim, eu criaria algum tipo de alerta em caso de falha, como envio de e-mail ou registro em ferramenta interna, para que o time responsável soubesse rapidamente se o processamento não fosse concluído.

---

## 6. Se a carteira tivesse 10 milhões de linhas, o que mudaria na sua abordagem de leitura, validação e geração do relatório?

Se a carteira tivesse 10 milhões de linhas, eu mudaria a abordagem para lidar melhor com volume alto de dados.

Na leitura, evitaria carregar tudo de uma vez na memória se o ambiente não suportasse esse volume. Uma alternativa seria ler o arquivo em partes usando `chunksize` no `pandas`, processando blocos menores de dados por vez.

Na validação de CPF e CNPJ, eu manteria a regra manual, mas teria cuidado com desempenho. Como validar documento linha a linha pode ser custoso em milhões de registros, eu tentaria reduzir retrabalho, por exemplo validando documentos únicos uma vez e depois reaproveitando o resultado para registros repetidos.

Na limpeza, eu também buscaria trabalhar de forma incremental, registrando quantos registros foram removidos ou corrigidos em cada parte do processamento.

Nos agrupamentos por status e cedente, em vez de depender apenas de uma grande tabela em memória, eu poderia acumular os resultados por lote e consolidar no final.

Para geração do relatório JSON, eu não colocaria detalhes linha a linha no arquivo final. Manteria apenas informações consolidadas, como totais, percentuais, agrupamentos e alertas resumidos. Isso evita gerar um JSON muito grande e difícil de abrir.

Se o volume fosse recorrente, também avaliaria usar banco de dados ou ferramentas mais adequadas para grandes volumes, como SQL, processamento distribuído ou serviços de dados em nuvem. A escolha dependeria da infraestrutura disponível.

De forma geral, a principal mudança seria sair de um processamento simples em memória para um processamento mais controlado, em lotes, com foco em desempenho, rastreabilidade e estabilidade.
