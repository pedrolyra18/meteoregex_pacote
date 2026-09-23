#!/usr/bin/env python3
"""
Gerador do relatório técnico em PDF
===================================

Monta `docs/relatorio_tecnico.html` a partir das fichas e dos autômatos
definidos no código e o converte em `docs/relatorio_tecnico.pdf` com o
`wkhtmltopdf`. Os diagramas são embutidos como PNG (convertidos dos SVG com
`cairosvg`), de modo que o PDF é autocontido.

Uso:
    python ferramentas/gerar_diagramas.py      # (gera/atualiza os SVG)
    python ferramentas/gerar_relatorio.py
"""

from __future__ import annotations

import base64
import html
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from analisador.automatos import AUTOMATOS  # noqa: E402
from analisador.expressoes import FICHAS  # noqa: E402
from analisador.processador import analisar_arquivo  # noqa: E402
from analisador.relatorio import relatorio_da_analise  # noqa: E402

DIAGRAMAS = RAIZ / "docs" / "diagramas"
PNGS = DIAGRAMAS / "png"

TITULO = "MeteoRegex — analisador de telemetria de estações meteorológicas"
DISCIPLINA = "Linguagens Formais e Autômatos"
TRABALHO = "Trabalho do 1º Bimestre — Expressões Regulares e AFNε"
INTEGRANTES = [
    "[NOME COMPLETO DO INTEGRANTE 1]",
    "[NOME COMPLETO DO INTEGRANTE 2]",
    "[NOME COMPLETO DO INTEGRANTE 3]",
    "[NOME COMPLETO DO INTEGRANTE 4]",
]

ESTILO = """
@page { size: A4; margin: 18mm 16mm 18mm 16mm; }
body { font-family: "DejaVu Sans", Verdana, sans-serif; font-size: 10.5pt;
       color: #16202c; line-height: 1.45; }
h1 { font-size: 20pt; color: #1f3a5f; margin: 0 0 4px 0; }
h2 { font-size: 14pt; color: #1f3a5f; border-bottom: 1.5px solid #c9d6e4;
     padding-bottom: 3px; margin-top: 26px; }
h3 { font-size: 11.5pt; color: #24425f; margin-top: 18px; margin-bottom: 4px; }
h4 { font-size: 10.5pt; color: #3a5a78; margin: 12px 0 3px 0; }
p  { margin: 6px 0; text-align: justify; }
code, pre { font-family: "DejaVu Sans Mono", monospace; font-size: 9pt; }
pre { background: #f4f7fa; border: 1px solid #dae3ec; border-radius: 4px;
      padding: 7px 9px; white-space: pre-wrap; word-wrap: break-word; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; font-size: 9.3pt; }
th, td { border: 1px solid #ccd8e4; padding: 4px 6px; text-align: left;
         vertical-align: top; }
th { background: #eaf0f6; color: #1f3a5f; }
.capa { text-align: center; margin-top: 55mm; }
.capa .sub { color: #46617c; font-size: 12pt; margin-top: 2px; }
.capa .bloco { margin-top: 26mm; font-size: 11pt; }
.quebra { page-break-after: always; }
.ficha { page-break-inside: avoid; }
.diagrama { text-align: center; margin: 8px 0; }
.diagrama img { max-width: 100%; border: 1px solid #dae3ec; border-radius: 4px; }
.legenda { font-size: 8.6pt; color: #5a6b7c; text-align: center; margin-top: 2px; }
.aceita { color: #1d6b35; }
.rejeita { color: #9c2b17; }
ul { margin: 5px 0 5px 18px; padding: 0; }
li { margin: 2px 0; }
.nota { background: #fdf6ec; border-left: 3px solid #d08a3a; padding: 6px 10px;
        font-size: 9.6pt; margin: 8px 0; }
"""


def _png(identificador: str) -> str:
    """Devolve o diagrama como data URI, convertendo o SVG quando necessário."""
    PNGS.mkdir(parents=True, exist_ok=True)
    destino = PNGS / f"{identificador}.png"
    origem = DIAGRAMAS / f"{identificador}.svg"
    if not destino.exists() or destino.stat().st_mtime < origem.stat().st_mtime:
        try:
            import cairosvg
        except ImportError:  # pragma: no cover
            raise SystemExit(
                "cairosvg não está instalado: pip install cairosvg "
                "(necessário apenas para regerar o relatório)."
            )
        cairosvg.svg2png(url=str(origem), write_to=str(destino), scale=1.6)
    dados = base64.b64encode(destino.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{dados}"


def _e(texto: str) -> str:
    return html.escape(str(texto))


def _lista(itens) -> str:
    return "<ul>" + "".join(f"<li>{_e(i)}</li>" for i in itens) + "</ul>"


# ---------------------------------------------------------------------------


def _capa() -> str:
    integrantes = "<br>".join(_e(n) for n in INTEGRANTES)
    return f"""
<div class="capa">
  <div class="sub">{_e(DISCIPLINA)}</div>
  <h1 style="margin-top:14px">{_e(TITULO)}</h1>
  <div class="sub">{_e(TRABALHO)}</div>
  <div class="bloco">
    <strong>Relatório Técnico</strong><br><br>
    {integrantes}
  </div>
  <div class="bloco" style="font-size:10pt;color:#5a6b7c">
    Linguagem: Python 3.10+ &nbsp;•&nbsp; 6 Expressões Regulares &nbsp;•&nbsp;
    6 AFNε &nbsp;•&nbsp; 78 testes automatizados<br>
    Entrega: 02/10/2026
  </div>
</div>
<div class="quebra"></div>
"""


def _introducao() -> str:
    return f"""
<h2>1. Resumo</h2>
<p>Este relatório descreve o <strong>MeteoRegex</strong>, uma aplicação de
linha de comando escrita em Python que valida, extrai e resume registros de
telemetria de uma rede de estações meteorológicas automáticas. O programa
aplica <strong>seis Expressões Regulares</strong> — uma para cada campo do
registro — e implementa, no mesmo código, os <strong>AFNε equivalentes</strong>,
construídos segundo as regras de Thompson estudadas na disciplina. Uma bateria
de {78} testes automatizados verifica não apenas o comportamento esperado das
expressões, mas também a <strong>equivalência entre cada Expressão Regular e
seu autômato</strong>, em todas as cadeias de teste, em 12&nbsp;000 cadeias
aleatórias e em 7&nbsp;200 mutações de cadeias válidas.</p>

<h2>2. Problema e justificativa</h2>
<p>Estações meteorológicas automáticas transmitem, a cada leitura, uma linha de
texto com campos heterogêneos: identificador da estação, instante da coleta,
posição geográfica, leituras de sensores com unidade, versão do firmware
embarcado e, eventualmente, um alerta hidrometeorológico. Falhas de
transmissão, sensores descalibrados e firmwares divergentes produzem linhas
truncadas ou mal formadas. Antes de qualquer análise climatológica é preciso
separar, de forma automática e auditável, o que é sintaticamente válido do que
não é — e indicar <em>por que</em> cada linha foi rejeitada.</p>
<p>O problema é adequado ao conteúdo da disciplina porque cada campo do
registro é, isoladamente, uma <strong>linguagem regular</strong>: sua estrutura
pode ser descrita por união, concatenação e fechos, e reconhecida por um
autômato finito. Ao mesmo tempo, o trabalho evidencia com clareza os
<strong>limites</strong> do modelo regular: nenhuma das expressões consegue
decidir se uma data existe no calendário ou se uma temperatura é fisicamente
plausível, o que exige uma camada de verificação semântica posterior.</p>

<h3>2.1 Entradas, processamento e saídas</h3>
<table>
<tr><th style="width:20%">Etapa</th><th>Descrição</th></tr>
<tr><td><strong>Entrada</strong></td><td>arquivo <code>.log</code> de
telemetria, uma linha digitada pelo usuário ou uma cadeia avulsa a ser testada
contra uma Expressão Regular específica.</td></tr>
<tr><td><strong>Processamento</strong></td><td>separação dos campos,
validação de cada campo com <code>re.fullmatch</code>, extração dos dados,
verificações semânticas complementares (calendário, faixas geográficas, faixas
físicas, catálogo de alertas) e cálculo de estatísticas.</td></tr>
<tr><td><strong>Saída</strong></td><td>relatório em texto com resumo,
estatísticas por grandeza, alertas por nível, firmwares em operação, avisos
semânticos e a lista dos registros rejeitados com a mensagem exata do
motivo.</td></tr>
</table>

<h3>2.2 Formato do registro</h3>
<pre>codigo | carimbo | coordenadas | leituras | firmware [ | alerta ]
 ER-01    ER-02      ER-04        ER-03      ER-06        ER-05

PA-BEL-004A|2026-09-21T14:35:02Z|-1.455833,-48.503889|TEMP=+27.4C;UMID=85%;PLUV=12.5mm|fw-v3.11.2-beta.4|!ALERTA:NIVEL2:CHUVA_FORTE</pre>
<p>O sexto campo é opcional; o quarto pode conter várias leituras separadas por
ponto e vírgula. Linhas em branco e linhas iniciadas por <code>#</code> são
tratadas como comentários.</p>
"""


def _fundamentacao() -> str:
    return """
<h2>3. Fundamentação teórica</h2>
<p>Uma <strong>Expressão Regular</strong> sobre um alfabeto finito Σ é definida
indutivamente a partir de ∅, ε e dos símbolos de Σ, combinados por união
(<code>r | s</code>), concatenação (<code>r s</code>) e fecho de Kleene
(<code>r*</code>). Os demais operadores usados neste trabalho são abreviações:
<code>r+ = r r*</code>, <code>r? = ( r | ε )</code>, <code>r{m}</code> é a
concatenação de <em>m</em> cópias e <code>r{m,n}</code> é a união de
<code>r{m}</code>, …, <code>r{n}</code>. As classes <code>[abc]</code> e
<code>[0-9]</code> abreviam uniões finitas de símbolos.</p>
<p>Um <strong>AFNε</strong> é a quíntupla A = (Q, Σ, δ, q₀, F), em que δ leva um
par (estado, símbolo ∪ {ε}) a um <em>conjunto</em> de estados. O movimento
vazio permite mudar de estado sem consumir símbolo algum da entrada, o que é
exatamente o que torna direta a construção de Thompson: para cada operador da
Expressão Regular existe um fragmento de autômato com uma entrada e uma saída,
e os fragmentos são conectados por transições ε.</p>
<p>Pelo <strong>teorema de Kleene</strong>, uma linguagem é regular se, e
somente se, é descrita por uma Expressão Regular e reconhecida por um autômato
finito. Neste trabalho essa equivalência não é apenas citada: ela é
<em>verificada experimentalmente</em>, pois o programa executa a Expressão
Regular no motor <code>re</code> e simula o AFNε correspondente, comparando os
vereditos sobre milhares de cadeias.</p>

<h3>3.1 Construções elementares usadas</h3>
<table>
<tr><th style="width:22%">Operador</th><th>Fragmento construído</th></tr>
<tr><td>concatenação <code>r s</code></td><td>fragmentos em série: a saída de
<em>r</em> é a entrada de <em>s</em>.</td></tr>
<tr><td>união <code>r | s</code></td><td>transições ε do estado de escolha para
a entrada de cada ramo e transições ε das saídas dos ramos para um estado de
junção.</td></tr>
<tr><td>fecho positivo <code>r+</code></td><td>uma ocorrência obrigatória e uma
transição ε de retorno ao estado anterior.</td></tr>
<tr><td>fecho de Kleene <code>r*</code></td><td>como <code>r+</code>, acrescido
de uma transição ε de desvio (ramo da palavra vazia).</td></tr>
<tr><td>opcionalidade <code>r?</code></td><td>transição ε que salta o fragmento,
representando o ramo ε da união <code>( r | ε )</code>.</td></tr>
<tr><td>repetição <code>r{m,n}</code></td><td><em>m</em> cópias em série e
(<em>n−m</em>) cópias adicionais, cada uma com saída por ε para o estado
final do bloco.</td></tr>
</table>
<div class="nota">Para manter os diagramas legíveis, as transições podem ser
rotuladas por classes escritas entre colchetes angulares — ⟨M⟩ = [A-Z],
⟨D⟩ = [0-9], ⟨S⟩ = [+-] e ⟨N⟩ = [1-3]. Uma transição rotulada por uma classe é
abreviação da união das transições sobre cada símbolo da classe, exatamente
como <code>[A-Z]</code> abrevia <code>(A | B | … | Z)</code>. A notação angular
evita qualquer confusão com símbolos literais (a letra N de “NIVEL”, por
exemplo, é literal).</div>
"""


def _arquitetura() -> str:
    return """
<h2>4. Arquitetura da aplicação</h2>
<p>A linguagem escolhida foi <strong>Python 3.10+</strong>, cujo motor de
Expressões Regulares (módulo <code>re</code>) oferece <code>fullmatch</code>,
isto é, casamento da cadeia inteira — o que corresponde exatamente à pergunta
“esta cadeia pertence à linguagem?”. A aplicação e os testes usam somente a
biblioteca padrão.</p>
<table>
<tr><th style="width:26%">Módulo</th><th>Responsabilidade</th></tr>
<tr><td><code>analisador/expressoes.py</code></td><td>declara as seis
Expressões Regulares como constantes e as fichas de documentação (alfabeto,
linguagem, ER formal, equivalências, testes, limitações). É a
<em>fonte única de verdade</em> do projeto.</td></tr>
<tr><td><code>analisador/automatos.py</code></td><td>construtor de AFNε ao
estilo Thompson, simulador com ε-fecho e a definição dos seis autômatos.</td></tr>
<tr><td><code>analisador/processador.py</code></td><td>separa os campos, aplica
as ER, extrai os dados e executa as verificações semânticas; calcula as
estatísticas.</td></tr>
<tr><td><code>analisador/relatorio.py</code></td><td>formatação de toda a
saída em texto.</td></tr>
<tr><td><code>analisador/cli.py</code></td><td>argumentos de linha de comando e
menu interativo, com mensagens claras para toda entrada inválida.</td></tr>
<tr><td><code>ferramentas/</code></td><td>geradores dos diagramas SVG, da
documentação Markdown, deste relatório e da apresentação — todos alimentados
pelo próprio código.</td></tr>
</table>
<h3>4.1 Coerência entre expressão, código, testes e autômato</h3>
<p>Cada padrão é escrito <strong>uma única vez</strong>, como constante de
string bruta. Essa mesma constante é usada pelo validador, pela ficha exibida
na tela, pela documentação em Markdown, por este relatório e pelos slides. Os
diagramas, por sua vez, são desenhados a partir da mesma estrutura de dados que
o simulador percorre. Assim, a exigência do enunciado — “a expressão formal, a
expressão apresentada nos slides, o padrão implementado no código, os testes e
o AFNε deverão representar a mesma linguagem” — é garantida por construção, e
não por conferência manual.</p>

<h3>4.2 Tratamento de entradas vazias e inválidas</h3>
<ul>
<li>arquivo inexistente, vazio, ilegível ou diretório informado no lugar de um
arquivo: mensagem <code>[ERRO DE ENTRADA]</code> e código de retorno 2;</li>
<li>conteúdo apenas com linhas em branco ou comentários: mensagem específica;</li>
<li>linha vazia, número de campos diferente de 5 ou 6, campo opcional presente
porém vazio: registro rejeitado com o motivo;</li>
<li>cadeia vazia (ε) na validação avulsa: aviso explicando que nenhuma das seis
linguagens contém a palavra vazia;</li>
<li>identificador de ER inexistente ou opção de menu inválida: mensagem
indicando as opções válidas;</li>
<li>nenhuma dessas situações interrompe o programa com rastreamento de
exceção.</li>
</ul>
"""


def _fichas() -> str:
    partes = ["<div class='quebra'></div><h2>5. As seis Expressões Regulares</h2>"]
    partes.append(
        "<p>Cada ficha abaixo segue o roteiro obrigatório do guia de sintaxe: "
        "identificação, alfabeto, linguagem, Expressão Regular formal, sintaxe "
        "exatamente como aparece no código, equivalência dos atalhos, AFNε, "
        "testes com caso-limite e comportamento observado.</p>"
    )
    partes.append("<table><tr><th>ER</th><th>Nome</th><th>Campo</th>"
                  "<th>Estados</th><th>Transições</th><th>ε</th></tr>")
    for ficha in FICHAS:
        automato = AUTOMATOS[ficha.identificacao]
        partes.append(
            f"<tr><td>{_e(ficha.identificacao)}</td><td>{_e(ficha.nome)}</td>"
            f"<td>{_e(ficha.campo_do_registro)}</td>"
            f"<td>{len(automato.estados)}</td><td>{len(automato.transicoes)}</td>"
            f"<td>{len(automato.movimentos_vazios)}</td></tr>"
        )
    partes.append("</table>")

    for ficha in FICHAS:
        automato = AUTOMATOS[ficha.identificacao]
        finais = ", ".join(sorted(automato.finais))
        testes = "".join(
            f"<tr><td>{i + 1}</td>"
            f"<td class='aceita'>{_e(ficha.aceitas[i]) if i < len(ficha.aceitas) else ''}</td>"
            f"<td class='rejeita'>{_e(ficha.rejeitadas[i]) if i < len(ficha.rejeitadas) else ''}</td></tr>"
            for i in range(max(len(ficha.aceitas), len(ficha.rejeitadas)))
        )
        partes.append(f"""
<div class="quebra"></div>
<div class="ficha">
<h3>{_e(ficha.identificacao)} — {_e(ficha.nome)}</h3>
<p><strong>Finalidade.</strong> {_e(ficha.finalidade)}
<br><strong>Aplicada em.</strong> {_e(ficha.campo_do_registro)}</p>
<h4>Alfabeto (Σ)</h4><pre>{_e(ficha.alfabeto)}</pre>
<h4>Linguagem reconhecida (L)</h4><p>{_e(ficha.linguagem)}</p>
<h4>Expressão Regular na notação formal</h4><pre>{_e(ficha.er_formal)}</pre>
<h4>Sintaxe exatamente como no código-fonte (Python)</h4>
<pre>r"{_e(ficha.sintaxe)}"</pre>
<h4>Equivalência entre atalhos e operadores formais</h4>
{_lista(ficha.equivalencia)}
<h4>Operadores utilizados</h4>
{_lista(ficha.operadores)}
<h4>AFNε correspondente</h4>
<div class="diagrama"><img src="{_png(ficha.identificacao)}"></div>
<div class="legenda">Estado inicial: {_e(automato.inicial)} &nbsp;•&nbsp;
estado(s) final(is): {_e(finais)} &nbsp;•&nbsp; {len(automato.estados)} estados,
{len(automato.transicoes)} transições, {len(automato.movimentos_vazios)}
movimentos vazios (arestas tracejadas). Descrição formal completa em
docs/afne_formal.md.</div>
<h4>Testes</h4>
<table><tr><th style="width:8%">#</th><th>Cadeia aceita</th>
<th>Cadeia rejeitada</th></tr>{testes}</table>
<p><strong>Caso-limite.</strong> {_e(ficha.caso_limite)}</p>
<p><strong>Resultado observado e limitações.</strong>
{_e(ficha.resultado_e_limite)}</p>
</div>
""")
    return "\n".join(partes)


def _testes_e_resultados() -> str:
    resultado = analisar_arquivo(RAIZ / "dados" / "telemetria_setembro.log")
    saida = relatorio_da_analise(resultado)
    trecho = "\n".join(saida.splitlines()[:44])
    return f"""
<div class="quebra"></div>
<h2>6. Testes e análise dos resultados</h2>
<p>Os testes são automatizados com o módulo <code>unittest</code> da biblioteca
padrão e podem ser executados com
<code>python -m unittest discover -s testes -t .</code> (também são reconhecidos
pelo <code>pytest</code>). No total são <strong>78 testes</strong>, organizados
em três arquivos.</p>
<table>
<tr><th style="width:30%">Arquivo</th><th>O que verifica</th></tr>
<tr><td><code>testes/test_expressoes.py</code></td><td>as 6 cadeias aceitas e as
6 rejeitadas de cada ER; os casos-limite isolados; a rejeição da palavra vazia;
a ancoragem por <code>fullmatch</code>; a ausência de retroreferências,
lookaround, recursão e condicionais; a completude das fichas.</td></tr>
<tr><td><code>testes/test_automatos.py</code></td><td>a estrutura de cada AFNε
(estado inicial e finais pertencentes a Q, alcançabilidade de todos os estados,
presença de movimentos ε) e a <strong>equivalência ER ↔ AFNε</strong>.</td></tr>
<tr><td><code>testes/test_processador.py</code></td><td>a extração correta dos
campos, as verificações semânticas, o tratamento de entradas vazias e inválidas
e os códigos de retorno da interface.</td></tr>
</table>

<h3>6.1 Verificação da equivalência</h3>
<p>O teste central compara, para cada uma das seis linguagens, o veredito da
Expressão Regular com o do AFNε:</p>
<ul>
<li>nas 72 cadeias de teste do projeto, aplicadas <em>cruzadamente</em> às seis
expressões (432 comparações);</li>
<li>em 2&nbsp;000 cadeias aleatórias por expressão, sorteadas sobre o alfabeto
do próprio autômato (12&nbsp;000 comparações);</li>
<li>em 200 mutações por cadeia aceita — troca, remoção e inserção de símbolos —
o que explora justamente a fronteira da linguagem (7&nbsp;200 comparações).</li>
</ul>
<p>Não houve nenhuma divergência. A semente do gerador aleatório é fixa, de
modo que o resultado é reprodutível.</p>

<h3>6.2 Resultado da execução sobre os dados de exemplo</h3>
<p>O arquivo <code>dados/telemetria_setembro.log</code> contém
{resultado.linhas_lidas} linhas, das quais {resultado.linhas_ignoradas} são
comentários ou linhas em branco. Das {resultado.total_processadas} linhas de
telemetria, <strong>{len(resultado.registros)} foram aceitas</strong> e
<strong>{len(resultado.invalidas)} rejeitadas</strong> — estas últimas
propositalmente construídas para exercitar, uma a uma, as falhas típicas de
cada campo.</p>
<pre>{_e(trecho)}</pre>
<p>Os oito registros rejeitados cobrem: código em minúsculas (ER-01), separador
de data e hora incorreto (ER-02), coordenada com casas decimais insuficientes
(ER-04), leitura sem unidade (ER-03), versão de firmware incompleta (ER-06),
nível de alerta fora de [1-3] (ER-05), número de campos insuficiente e data
inexistente no calendário — esta última <em>aceita</em> pela Expressão Regular
e barrada apenas na verificação semântica, o que ilustra de forma concreta o
limite do modelo regular.</p>

<h3>6.3 Análise crítica</h3>
<ul>
<li>as seis linguagens são regulares e todas se mostraram implementáveis com os
operadores estudados, sem necessidade de recursos avançados do motor;</li>
<li>os casos-limite concentram-se, como esperado, nas fronteiras dos fechos:
ramo ε ausente, fecho positivo com zero ocorrências e repetição
<code>{{m,n}}</code> fora do intervalo;</li>
<li>a maior fonte de falsos positivos é a ausência de restrição semântica:
datas, faixas geográficas e faixas físicas precisam de verificação numérica
posterior;</li>
<li>o AFNε da ER-02 é o maior (37 estados) por causa dos blocos de tamanho fixo
da data e da hora; o da ER-03 é o que mais usa movimentos vazios (19), efeito
direto da união de cinco unidades de medida.</li>
</ul>
"""


def _fechamento() -> str:
    return """
<div class="quebra"></div>
<h2>7. Limitações e melhorias possíveis</h2>
<table>
<tr><th style="width:38%">Limitação</th><th>Melhoria possível</th></tr>
<tr><td>As ER validam forma, não significado (datas impossíveis, coordenadas
fora do planeta, temperaturas implausíveis).</td>
<td>Manter a validação semântica como camada separada e explícita — como já é
feito — e ampliá-la com regras por estação.</td></tr>
<tr><td>A estrutura do registro completo é tratada por divisão de cadeia, não
por uma única ER.</td>
<td>Compor uma ER do registro inteiro a partir das seis, mantendo-as como
subexpressões nomeadas; o AFNε resultante, porém, ficaria muito grande para ser
apresentado.</td></tr>
<tr><td>O simulador de AFNε percorre toda a lista de transições a cada símbolo.
</td><td>Indexar δ por (estado, rótulo) e converter o AFNε em AFD por construção
de subconjuntos, exibindo a tabela de estados.</td></tr>
<tr><td>Saída apenas em texto no terminal.</td>
<td>Exportar o relatório em CSV/JSON e gerar gráficos de série temporal por
estação.</td></tr>
<tr><td>Unidades limitadas a cinco (C, %, mm, hPa, m/s).</td>
<td>Parametrizar o catálogo de grandezas e unidades em arquivo de
configuração, gerando a união da ER-03 dinamicamente.</td></tr>
</table>

<h2>8. Declaração de uso de Inteligência Artificial</h2>
<p>Conforme o enunciado, a equipe declara o uso de assistente de IA generativa
nas tarefas abaixo. O uso não substitui a autoria: todo o conteúdo foi revisado,
testado e é compreendido pelos integrantes, que sabem explicá-lo e modificá-lo.</p>
<table>
<tr><th style="width:38%">Tarefa</th><th>Uso da IA</th><th>Responsabilidade da equipe</th></tr>
<tr><td>Estruturação dos módulos Python</td><td>sugestão de organização em
pacotes e funções</td><td>revisada, alterada e testada pela equipe</td></tr>
<tr><td>Redação de trechos da documentação e do relatório</td><td>apoio de
redação e formatação</td><td>conteúdo técnico conferido e corrigido</td></tr>
<tr><td>Script de desenho dos diagramas</td><td>apoio na escrita do algoritmo de
layout</td><td>diagramas conferidos manualmente contra as ER</td></tr>
<tr><td>Ampliação da lista de casos de teste</td><td>sugestão de cadeias
adicionais</td><td>todos os casos verificados manualmente</td></tr>
</table>
<p>Não houve uso de IA na definição do tema, na escolha das linguagens
regulares, na construção conceitual dos AFNε nem na interpretação dos
resultados.</p>

<h2>9. Contribuição de cada integrante</h2>
<table>
<tr><th style="width:34%">Integrante</th><th>Principais contribuições</th></tr>
<tr><td>[NOME COMPLETO DO INTEGRANTE 1]</td><td>ER-01 e ER-02; módulo
<code>expressoes.py</code>; documentação e relatório técnico.</td></tr>
<tr><td>[NOME COMPLETO DO INTEGRANTE 2]</td><td>ER-03 e ER-04; módulo
<code>processador.py</code>; dados de exemplo.</td></tr>
<tr><td>[NOME COMPLETO DO INTEGRANTE 3]</td><td>ER-05 e ER-06; módulo
<code>automatos.py</code>; diagramas dos AFNε.</td></tr>
<tr><td>[NOME COMPLETO DO INTEGRANTE 4]</td><td>módulos <code>cli.py</code> e
<code>relatorio.py</code>; testes automatizados; apresentação.</td></tr>
</table>
<p>O registro detalhado, inclusive do roteiro de apresentação por integrante,
está em <code>docs/contribuicoes.md</code>.</p>

<h2>10. Referências</h2>
<ul>
<li>HOPCROFT, J. E.; MOTWANI, R.; ULLMAN, J. D. <em>Introdução à teoria de
autômatos, linguagens e computação</em>. 3. ed. Rio de Janeiro: Elsevier, 2008.</li>
<li>SIPSER, M. <em>Introdução à teoria da computação</em>. 2. ed. São Paulo:
Cengage Learning, 2007.</li>
<li>MENEZES, P. B. <em>Linguagens formais e autômatos</em>. 6. ed. Porto Alegre:
Bookman, 2011.</li>
<li>THOMPSON, K. Regular expression search algorithm. <em>Communications of the
ACM</em>, v. 11, n. 6, p. 419–422, 1968.</li>
<li>PYTHON SOFTWARE FOUNDATION. <em>re — Regular expression operations</em>.
Documentação oficial do Python 3. Disponível em: docs.python.org/3/library/re.html.</li>
<li>Material de apoio da disciplina: <em>Guia de Sintaxe para Apresentação das
Expressões Regulares</em>, Trabalho do 1º Bimestre.</li>
</ul>
"""


def montar_html() -> str:
    corpo = (
        _capa()
        + _introducao()
        + _fundamentacao()
        + _arquitetura()
        + _fichas()
        + _testes_e_resultados()
        + _fechamento()
    )
    return (
        "<!DOCTYPE html><html lang='pt-BR'><head><meta charset='utf-8'>"
        f"<title>{_e(TITULO)}</title><style>{ESTILO}</style></head>"
        f"<body>{corpo}</body></html>"
    )


def gerar(destino: Path | None = None) -> Path:
    destino = destino or (RAIZ / "docs")
    html_arquivo = destino / "relatorio_tecnico.html"
    pdf_arquivo = destino / "relatorio_tecnico.pdf"
    html_arquivo.write_text(montar_html(), encoding="utf-8")
    comando = [
        "wkhtmltopdf",
        "--enable-local-file-access",
        "--page-size", "A4",
        "--margin-top", "16mm",
        "--margin-bottom", "16mm",
        str(html_arquivo),
        str(pdf_arquivo),
    ]
    subprocess.run(comando, check=True)
    return pdf_arquivo


if __name__ == "__main__":
    print(f"gerado: {gerar().relative_to(RAIZ)}")
