# MeteoRegex — analisador de telemetria de estações meteorológicas

Trabalho do 1º bimestre da disciplina **Linguagens Formais e Autômatos**.
Aplicação de linha de comando, escrita em Python puro, que valida, extrai e
resume registros de telemetria de uma rede de estações meteorológicas usando
**seis Expressões Regulares** e os **AFNε** equivalentes, construídos e
simulados pelo próprio programa.

---

## 1. Problema resolvido

Estações meteorológicas automáticas gravam, a cada leitura, uma linha de texto
com campos heterogêneos (identificador, instante, posição, leituras de
sensores, versão de firmware e, eventualmente, um alerta). Esses arquivos
chegam ao centro de operações com linhas truncadas, campos em formato errado,
sensores descalibrados e firmwares não suportados. Antes de qualquer análise
climatológica é preciso **separar o que é sintaticamente válido do que não é**
e extrair os dados em forma estruturada.

O MeteoRegex faz exatamente isso:

| Entrada | Processamento | Saída |
|---------|---------------|-------|
| arquivo `.log` de telemetria, linha digitada ou cadeia avulsa | validação por ER (`re.fullmatch`), extração de campos, verificações semânticas complementares | relatório com estatísticas por grandeza, alertas, firmwares, avisos e lista de registros rejeitados com o motivo exato |

### Formato de um registro

```
codigo | carimbo | coordenadas | leituras | firmware [ | alerta ]
 ER-01    ER-02      ER-04        ER-03      ER-06        ER-05
```

Exemplo:

```
PA-BEL-004A|2026-09-21T14:35:02Z|-1.455833,-48.503889|TEMP=+27.4C;UMID=85%;PLUV=12.5mm|fw-v3.11.2-beta.4|!ALERTA:NIVEL2:CHUVA_FORTE
```

---

## 2. Expressões Regulares implementadas

| ER | Nome | Sintaxe no código (Python) |
|----|------|----------------------------|
| ER-01 | Código de estação | `[A-Z]{2}-[A-Z]{3}-[0-9]{3}[A-Z](?:\.[0-9]{1,2})?` |
| ER-02 | Carimbo temporal ISO-8601 | `[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]{1,3})?(?:Z\|[+-][0-9]{2}:[0-9]{2})?` |
| ER-03 | Leitura de sensor com unidade | `[A-Z]{3,4}=[+-]?[0-9]+(?:\.[0-9]+)?(?:C\|%\|mm\|hPa\|m/s)` |
| ER-04 | Coordenadas geodésicas | `[+-]?[0-9]{1,3}\.[0-9]{4,6},[+-]?[0-9]{1,3}\.[0-9]{4,6}` |
| ER-05 | Alerta hidrometeorológico | `!ALERTA:NIVEL[1-3]:[A-Z]+(?:_[A-Z]+)*` |
| ER-06 | Versão de firmware | `fw-v[0-9]+(?:\.[0-9]+){2}(?:-(?:alpha\|beta\|rc)\.[0-9]+)?` |

A ficha completa de cada uma (alfabeto, linguagem, ER formal, equivalência dos
operadores, AFNε, testes, caso-limite e limitações) está em
[`docs/expressoes_regulares.md`](docs/expressoes_regulares.md); a descrição
formal dos autômatos, em [`docs/afne_formal.md`](docs/afne_formal.md); os
diagramas, em [`docs/diagramas/`](docs/diagramas).

> Nenhuma expressão usa retroreferência, recursão, condicional ou lookaround,
> conforme a seção 4 do guia de sintaxe. Todos os agrupamentos são não
> capturantes `(?:r)`, equivalentes ao agrupamento formal `( r )`.

---

## 3. Instalação

Requisito único: **Python 3.10 ou superior**. O programa e os testes usam
somente a biblioteca padrão — não há dependências a instalar.

```bash
git clone <url-do-repositorio>
cd meteoregex
python --version          # deve indicar 3.10+
python main.py            # inicia o menu interativo
```

As dependências opcionais (usadas apenas para *regerar* o relatório em PDF e a
apresentação) estão em [`requirements.txt`](requirements.txt); elas **não** são
necessárias para executar ou testar a aplicação.

---

## 4. Execução

```bash
python main.py                                       # menu interativo
python main.py -a dados/telemetria_setembro.log      # analisa um arquivo
python main.py -a dados/telemetria_setembro.log -d   # com detalhe de cada registro
python main.py -l "PA-BEL-004A|2026-09-21T14:35:02Z|-1.455833,-48.503889|TEMP=+27.4C|fw-v3.11.2"
python main.py -e ER-03 -c "TEMP=+27.4C"             # testa uma cadeia (ER e AFNε)
python main.py -f                                    # fichas de todas as ER
python main.py -f -e ER-05 --afne                    # ficha + descrição formal do AFNε
python main.py -t                                    # bateria de cadeias aceitas/rejeitadas
```

Na validação avulsa o programa mostra, lado a lado, o veredito da Expressão
Regular e o do AFNε, além da trilha de conjuntos de estados percorrida pela
simulação — útil para a demonstração em sala.

---

## 5. Testes

```bash
python -m unittest discover -s testes -t .   # 78 testes, sem dependências externas
pytest -q                                     # opcional, se o pytest estiver instalado
python main.py -t                             # bateria visual das cadeias de teste
```

Os testes cobrem:

* as **6 cadeias aceitas e 6 rejeitadas** de cada ER, com o caso-limite isolado
  em um teste próprio;
* a **equivalência ER ↔ AFNε** em todas as cadeias do projeto, em 12 000
  cadeias aleatórias e em 7 200 mutações de cadeias válidas;
* a estrutura dos autômatos (estado inicial, finais, alcançabilidade, presença
  de movimentos ε);
* entradas vazias e inválidas (arquivo inexistente, arquivo vazio, diretório,
  linha vazia, campo faltando, número de campos errado, ER inexistente);
* as verificações semânticas (data inexistente no calendário, coordenada fora
  de faixa, leitura fora da faixa física, unidade incoerente, alerta fora do
  catálogo);
* a interface de linha de comando e seus códigos de retorno.

---

## 6. Estrutura do repositório

```
meteoregex/
├── main.py                     ponto de entrada
├── analisador/
│   ├── expressoes.py           as 6 ER e suas fichas (fonte única de verdade)
│   ├── automatos.py            construtor, simulador e os 6 AFNε
│   ├── processador.py          validação, extração e estatísticas
│   ├── relatorio.py            formatação das saídas
│   └── cli.py                  linha de comando e menu interativo
├── testes/                     testes automatizados (unittest)
├── dados/                      arquivos de exemplo, inclusive casos degenerados
├── docs/
│   ├── expressoes_regulares.md fichas completas (geradas do código)
│   ├── afne_formal.md          Q, Σ, δ, q₀, F de cada autômato
│   ├── contribuicoes.md        registro das contribuições da equipe
│   ├── relatorio_tecnico.pdf   relatório técnico
│   ├── apresentacao.pptx       apresentação
│   └── diagramas/              AFNε em SVG (e PNG)
└── ferramentas/                geradores de diagramas, documentação, relatório e slides
```

Os diagramas e a documentação são **gerados a partir do código**:

```bash
python ferramentas/gerar_diagramas.py
python ferramentas/gerar_documentacao.py
```

Isso garante que a ER formal, o padrão do código, os testes e o AFNε não
possam divergir entre si.

---

## 7. Equipe e contribuições

| Integrante        | Principais contribuições |
|------------       |--------------------------|
| [Pedro Lyra]      | ER-01 e ER-02, módulo `expressoes`, relatório técnico |
| [Rodrigo Marques] | ER-03 e ER-04, módulo `processador`, dados de exemplo |
| [Noam Geraldo]    | ER-05 e ER-06, módulo `automatos`, diagramas dos AFNε |
| []                | módulos `cli` e `relatorio`, testes automatizados, apresentação |

O detalhamento está em [`docs/contribuicoes.md`](docs/contribuicoes.md).

---

## 8. Declaração de uso de Inteligência Artificial

Conforme exigido pelo enunciado, a equipe declara o uso de ferramenta de IA
generativa (assistente de código baseado em LLM) nas seguintes tarefas:

| Tarefa | Uso da IA | Responsabilidade da equipe |
|--------|-----------|----------------------------|
| Estruturação inicial dos módulos Python | sugestão de organização em pacotes e funções | revisada, alterada e testada pela equipe |
| Redação de trechos da documentação e do relatório | apoio na redação e formatação | conteúdo técnico conferido e corrigido pela equipe |
| Geração dos diagramas em SVG | apoio na escrita do script de desenho | algoritmo de layout revisado; diagramas conferidos manualmente contra as ER |
| Sugestão de casos de teste adicionais | ampliação da lista de cadeias | todos os casos foram verificados manualmente, incluindo os casos-limite |

Não houve uso de IA para a definição do tema, para a escolha das linguagens
regulares, para a construção conceitual dos AFNε nem para a interpretação dos
resultados. Todos os integrantes compreendem, sabem explicar e são capazes de
modificar qualquer parte do que foi produzido.

---

## 9. Limitações conhecidas

* As ER validam **forma**, não **significado**: datas inexistentes, coordenadas
  fora do planeta e temperaturas implausíveis passam pela ER e só são barradas
  (ou sinalizadas) na etapa semântica seguinte — o que é uma consequência
  direta das limitações das linguagens regulares, e não um defeito de
  implementação.
* A estrutura do registro completo (campos separados por `|`) é tratada por
  divisão de cadeia e não por uma única ER gigante, escolha feita para manter
  cada expressão legível e com AFNε desenhável.
* O simulador de AFNε é didático: percorre a lista de transições a cada
  símbolo, sem indexação por estado. Para os tamanhos deste trabalho
  (até 37 estados) o custo é irrelevante.
