// Gerador da apresentação (docs/apresentacao.pptx) a partir dos dados
// extraídos do próprio código (ferramentas/dados_slides.json).
//
// Uso: node ferramentas/gerar_apresentacao.js

const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

const RAIZ = path.resolve(__dirname, "..");
const FICHAS = JSON.parse(
  fs.readFileSync(path.join(RAIZ, "ferramentas", "dados_slides.json"), "utf8")
);
const DIAG = (id) => path.join(RAIZ, "docs", "diagramas", "png", `${id}.png`);

// ---------------------------------------------------------------------------
// Paleta "Ocean Gradient" (tema meteorológico) + acento âmbar de alerta
// ---------------------------------------------------------------------------
const AZUL_PROFUNDO = "065A82";
const TEAL = "1C7293";
const MEIA_NOITE = "21295C";
const GELO = "EAF3F8";
const BRANCO = "FFFFFF";
const TEXTO = "132339";
const CINZA = "5B6B7C";
const AMBAR = "C97A2B";
const VERDE_OK = "2E7D4F";
const VERMELHO_NAO = "B3402B";
const LINHA = "D3E1EA";

const FONTE_TITULO = "Cambria";
const FONTE_CORPO = "Calibri";
const FONTE_CODIGO = "Consolas";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3" x 7.5"
const W = 13.33, H = 7.5;

pres.defineSlideMaster({
  title: "CLARO",
  background: { color: BRANCO },
});

// ---------------------------------------------------------------------------
// Auxiliares
// ---------------------------------------------------------------------------

function rodape(slide, numero) {
  slide.addText("MeteoRegex — Linguagens Formais e Autômatos", {
    x: 0.5, y: H - 0.4, w: 7, h: 0.3, fontFace: FONTE_CORPO, fontSize: 9,
    color: CINZA, isTextBox: true, margin: 0,
  });
  slide.addText(String(numero), {
    x: W - 0.9, y: H - 0.4, w: 0.5, h: 0.3, fontFace: FONTE_CORPO, fontSize: 9,
    color: CINZA, align: "right", isTextBox: true, margin: 0,
  });
}

function cabecalho(slide, titulo, subtitulo) {
  slide.addText(titulo, {
    x: 0.55, y: 0.35, w: W - 1.1, h: 0.62, fontFace: FONTE_TITULO,
    fontSize: 28, bold: true, color: MEIA_NOITE, isTextBox: true, margin: 0,
  });
  if (subtitulo) {
    slide.addText(subtitulo, {
      x: 0.55, y: 0.95, w: W - 1.1, h: 0.36, fontFace: FONTE_CORPO,
      fontSize: 14, color: TEAL, isTextBox: true, margin: 0,
    });
  }
  slide.addShape(pres.ShapeType.rect, {
    x: 0.55, y: subtitulo ? 1.34 : 1.05, w: 1.0, h: 0.045, fill: { color: AMBAR },
    line: { type: "none" },
  });
}

function bloco(slide, opts) {
  const { x, y, w, h, fill = GELO, linha = LINHA } = opts;
  slide.addShape(pres.ShapeType.roundRect, {
    x, y, w, h, rectRadius: 0.08,
    fill: { color: fill }, line: { color: linha, width: 1 },
    shadow: { type: "outer", color: "1B2A3A", opacity: 0.12, blur: 6,
              offset: 2, angle: 90 },
  });
}

// ---------------------------------------------------------------------------
// Slide 1 — capa
// ---------------------------------------------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: MEIA_NOITE };
  for (let i = 0; i < 5; i++) {
    s.addShape(pres.ShapeType.rect, {
      x: -1, y: 5.1 + i * 0.05, w: W + 2, h: 0.02,
      fill: { color: TEAL }, line: { type: "none" }, transparency: 60 + i * 6,
    });
  }
  s.addText("LINGUAGENS FORMAIS E AUTÔMATOS  •  TRABALHO DO 1º BIMESTRE", {
    x: 0.9, y: 1.55, w: W - 1.8, h: 0.4, fontFace: FONTE_CORPO, fontSize: 14,
    color: "9FC3DA", charSpacing: 2, isTextBox: true, margin: 0,
  });
  s.addText("MeteoRegex", {
    x: 0.85, y: 2.05, w: W - 1.7, h: 1.3, fontFace: FONTE_TITULO, fontSize: 60,
    bold: true, color: BRANCO, isTextBox: true, margin: 0,
  });
  s.addText("Expressões Regulares e AFNε aplicados à telemetria de estações meteorológicas", {
    x: 0.9, y: 3.35, w: W - 2.4, h: 0.6, fontFace: FONTE_CORPO, fontSize: 18,
    color: "CADCFC", isTextBox: true, margin: 0,
  });
  s.addText(
    [
      { text: "6 Expressões Regulares", options: { bold: true, color: BRANCO } },
      { text: "   •   ", options: { color: "6E86A6" } },
      { text: "6 AFNε", options: { bold: true, color: BRANCO } },
      { text: "   •   ", options: { color: "6E86A6" } },
      { text: "78 testes automatizados", options: { bold: true, color: BRANCO } },
    ],
    { x: 0.9, y: 4.15, w: W - 1.8, h: 0.4, fontFace: FONTE_CORPO, fontSize: 14,
      color: "CADCFC", isTextBox: true, margin: 0 }
  );
  s.addText("[NOME COMPLETO DO INTEGRANTE 1]  •  [NOME COMPLETO DO INTEGRANTE 2]  •  [NOME COMPLETO DO INTEGRANTE 3]  •  [NOME COMPLETO DO INTEGRANTE 4]", {
    x: 0.9, y: 6.55, w: W - 1.8, h: 0.4, fontFace: FONTE_CORPO, fontSize: 12,
    color: "8FA9C2", isTextBox: true, margin: 0,
  });
  s.addText("Entrega: 02/10/2026", {
    x: 0.9, y: 6.9, w: W - 1.8, h: 0.3, fontFace: FONTE_CORPO, fontSize: 11,
    color: "6E86A6", isTextBox: true, margin: 0,
  });
  s.addNotes(
    "Abertura: apresentar o nome do projeto e o objetivo do trabalho — " +
    "relacionar a fundamentação teórica de Linguagens Formais e Autômatos " +
    "com uma aplicação computacional funcional. Cada integrante se apresenta."
  );
}

// ---------------------------------------------------------------------------
// Slide 2 — problema e solução
// ---------------------------------------------------------------------------
{
  const s = pres.addSlide();
  cabecalho(s, "O problema", "Telemetria de estações meteorológicas chega crua, incompleta e às vezes corrompida");

  bloco(s, { x: 0.55, y: 1.75, w: 6.05, h: 4.85 });
  s.addText("Por que este tema?", {
    x: 0.85, y: 1.95, w: 5.5, h: 0.4, fontFace: FONTE_TITULO, fontSize: 17,
    bold: true, color: MEIA_NOITE, isTextBox: true, margin: 0,
  });
  const pontos = [
    "Cada registro traz código da estação, instante da coleta, posição, leituras de sensores, versão de firmware e, às vezes, um alerta.",
    "Falhas de transmissão e sensores descalibrados produzem linhas mal formadas — que precisam ser detectadas antes de qualquer análise.",
    "Cada campo, isoladamente, é uma linguagem regular: sua estrutura é descrita por união, concatenação e fechos, e reconhecida por um autômato finito.",
    "O tema evidencia também o limite do modelo: nenhuma ER decide se uma data existe no calendário.",
  ];
  s.addText(pontos.map((t) => ({ text: t, options: { bullet: { code: "2022" }, breakLine: true, paraSpaceAfter: 12 } })), {
    x: 0.85, y: 2.45, w: 5.45, h: 4.0, fontFace: FONTE_CORPO, fontSize: 13.5,
    color: TEXTO, isTextBox: true, margin: 0, valign: "top",
  });

  bloco(s, { x: 6.85, y: 1.75, w: 5.93, h: 4.85, fill: "0E3A55" });
  s.addText("A solução: MeteoRegex", {
    x: 7.15, y: 1.95, w: 5.4, h: 0.4, fontFace: FONTE_TITULO, fontSize: 17,
    bold: true, color: BRANCO, isTextBox: true, margin: 0,
  });
  s.addText("Analisador de linha de comando em Python que valida, extrai e resume registros de telemetria usando 6 ER e os AFNε equivalentes.", {
    x: 7.15, y: 2.42, w: 5.35, h: 0.8, fontFace: FONTE_CORPO, fontSize: 13,
    color: "D8E7F1", isTextBox: true, margin: 0,
  });

  const etapas = [
    ["ENTRADA", "arquivo de log, linha digitada ou cadeia avulsa"],
    ["PROCESSAMENTO", "validação por ER (fullmatch), extração e checagem semântica"],
    ["SAÍDA", "relatório com estatísticas, alertas e registros rejeitados com o motivo"],
  ];
  let y = 3.4;
  for (const [rotulo, desc] of etapas) {
    s.addShape(pres.ShapeType.roundRect, {
      x: 7.15, y, w: 1.9, h: 0.5, rectRadius: 0.06,
      fill: { color: AMBAR }, line: { type: "none" },
    });
    s.addText(rotulo, {
      x: 7.15, y, w: 1.9, h: 0.5, fontFace: FONTE_CORPO, fontSize: 11.5,
      bold: true, color: MEIA_NOITE, align: "center", valign: "middle",
      isTextBox: true, margin: 0,
    });
    s.addText(desc, {
      x: 9.2, y: y - 0.02, w: 3.35, h: 0.55, fontFace: FONTE_CORPO,
      fontSize: 11.5, color: "D8E7F1", valign: "middle", isTextBox: true, margin: 0,
    });
    y += 0.72;
  }
  s.addText('"codigo | carimbo | coordenadas | leituras | firmware [ | alerta ]"', {
    x: 7.15, y: 5.65, w: 5.35, h: 0.75, fontFace: FONTE_CODIGO, fontSize: 10.5,
    color: "AFC9DB", isTextBox: true, margin: 0,
  });
  rodape(s, 2);
  s.addNotes(
    "Explicar o problema com um exemplo verbal de linha de telemetria corrompida. " +
    "Mostrar que o formato do registro tem 5 ou 6 campos, cada um validado por uma ER diferente."
  );
}

// ---------------------------------------------------------------------------
// Slide 3 — fundamentação e metodologia (Thompson)
// ---------------------------------------------------------------------------
{
  const s = pres.addSlide();
  cabecalho(s, "Da Expressão Regular ao AFNε", "Construção de Thompson: cada operador vira um fragmento de autômato");

  const construcoes = [
    ["concatenação  r s", "fragmentos em série"],
    ["união  r | s", "ε do estado de escolha para cada ramo; ε de cada ramo para a junção"],
    ["fecho positivo  r+", "uma ocorrência obrigatória + ε de retorno"],
    ["fecho de Kleene  r*", "como r+, mais um ε de desvio (ramo vazio)"],
    ["opcionalidade  r?", "ε que salta o fragmento — é ( r | ε )"],
    ["repetição  r{m,n}", "m cópias obrigatórias + (n−m) cópias com saída por ε"],
  ];
  const largura = 4.0, altura = 1.42, gapX = 0.18, gapY = 0.18;
  const x0 = 0.55, y0 = 1.85;
  construcoes.forEach(([nome, desc], i) => {
    const col = i % 3, lin = Math.floor(i / 3);
    const x = x0 + col * (largura + gapX);
    const y = y0 + lin * (altura + gapY);
    bloco(s, { x, y, w: largura, h: altura });
    s.addText(nome, {
      x: x + 0.18, y: y + 0.1, w: largura - 0.36, h: 0.4, fontFace: FONTE_CODIGO,
      fontSize: 14, bold: true, color: AZUL_PROFUNDO, isTextBox: true, margin: 0,
    });
    s.addText(desc, {
      x: x + 0.18, y: y + 0.52, w: largura - 0.36, h: 0.82, fontFace: FONTE_CORPO,
      fontSize: 11.5, color: TEXTO, isTextBox: true, margin: 0, valign: "top",
    });
  });

  bloco(s, { x: 0.55, y: 5.15, w: 12.23, h: 1.45, fill: "FCF2E4", linha: "EBD3AA" });
  s.addText([
    { text: "Notação usada nos diagramas:  ", options: { bold: true, color: MEIA_NOITE } },
    { text: "⟨M⟩ = [A-Z]   ⟨D⟩ = [0-9]   ⟨S⟩ = [+-]   ⟨N⟩ = [1-3]", options: { color: TEXTO, fontFace: FONTE_CODIGO } },
  ], {
    x: 0.85, y: 5.35, w: 11.6, h: 0.4, fontFace: FONTE_CORPO, fontSize: 13,
    isTextBox: true, margin: 0,
  });
  s.addText(
    "Uma transição rotulada por uma classe abrevia a união das transições sobre cada símbolo dela — exatamente como [A-Z] abrevia (A | B | ... | Z). " +
    "Arestas tracejadas (laranja) são movimentos ε; arestas sólidas (azul) consomem um símbolo.",
    { x: 0.85, y: 5.78, w: 11.6, h: 0.72, fontFace: FONTE_CORPO, fontSize: 12,
      color: CINZA, isTextBox: true, margin: 0, valign: "top" }
  );
  rodape(s, 3);
  s.addNotes(
    "Recapitular rapidamente a construção de Thompson antes de entrar nas 6 expressões. " +
    "Enfatizar a notação de classe usada nos diagramas seguintes, para não confundir com símbolo literal."
  );
}

// ---------------------------------------------------------------------------
// Slides 4..9 — uma ficha por ER
// ---------------------------------------------------------------------------

function slideER(ficha, indice) {
  const s = pres.addSlide();
  cabecalho(s, `${ficha.id} — ${ficha.nome}`, ficha.campo.charAt(0).toUpperCase() + ficha.campo.slice(1));

  // coluna esquerda: notação formal + sintaxe + linguagem
  const xE = 0.55, wE = 5.55;
  bloco(s, { x: xE, y: 1.75, w: wE, h: 1.18 });
  s.addText("ER formal", { x: xE + 0.2, y: 1.85, w: wE - 0.4, h: 0.28,
    fontFace: FONTE_CORPO, fontSize: 11, bold: true, color: TEAL, isTextBox: true, margin: 0 });
  s.addText(ficha.er_formal, { x: xE + 0.2, y: 2.13, w: wE - 0.4, h: 0.75,
    fontFace: FONTE_CODIGO, fontSize: 11.5, color: TEXTO, isTextBox: true, margin: 0, valign: "top" });

  bloco(s, { x: xE, y: 3.03, w: wE, h: 0.85, fill: "0E3A55" });
  s.addText("Sintaxe no código (Python)", { x: xE + 0.2, y: 3.12, w: wE - 0.4, h: 0.26,
    fontFace: FONTE_CORPO, fontSize: 11, bold: true, color: "9FC3DA", isTextBox: true, margin: 0 });
  s.addText(`r"${ficha.sintaxe}"`, { x: xE + 0.2, y: 3.39, w: wE - 0.4, h: 0.45,
    fontFace: FONTE_CODIGO, fontSize: 11, color: BRANCO, isTextBox: true, margin: 0, valign: "top" });

  bloco(s, { x: xE, y: 3.98, w: wE, h: 1.05 });
  s.addText("Linguagem reconhecida", { x: xE + 0.2, y: 4.08, w: wE - 0.4, h: 0.26,
    fontFace: FONTE_CORPO, fontSize: 11, bold: true, color: TEAL, isTextBox: true, margin: 0 });
  s.addText(ficha.linguagem, { x: xE + 0.2, y: 4.35, w: wE - 0.4, h: 0.62,
    fontFace: FONTE_CORPO, fontSize: 10.8, color: TEXTO, isTextBox: true, margin: 0, valign: "top" });

  // testes: aceitas / rejeitadas
  const yTestes = 5.15;
  bloco(s, { x: xE, y: yTestes, w: (wE - 0.2) / 2, h: 1.45, fill: "EAF6EF", linha: "BFE1CC" });
  s.addText("Aceitas", { x: xE + 0.12, y: yTestes + 0.08, w: (wE - 0.2) / 2 - 0.24, h: 0.24,
    fontFace: FONTE_CORPO, fontSize: 10.5, bold: true, color: VERDE_OK, isTextBox: true, margin: 0 });
  s.addText(ficha.aceitas.slice(0, 4).map((c) => `✓ ${c}`).join("\n"), {
    x: xE + 0.12, y: yTestes + 0.33, w: (wE - 0.2) / 2 - 0.24, h: 1.05,
    fontFace: FONTE_CODIGO, fontSize: 9, color: "1E5B39", isTextBox: true, margin: 0, valign: "top",
    lineSpacingMultiple: 1.15,
  });

  const xRej = xE + (wE - 0.2) / 2 + 0.2;
  bloco(s, { x: xRej, y: yTestes, w: (wE - 0.2) / 2, h: 1.45, fill: "FBEAE7", linha: "F0C4BA" });
  s.addText("Rejeitadas", { x: xRej + 0.12, y: yTestes + 0.08, w: (wE - 0.2) / 2 - 0.24, h: 0.24,
    fontFace: FONTE_CORPO, fontSize: 10.5, bold: true, color: VERMELHO_NAO, isTextBox: true, margin: 0 });
  s.addText(ficha.rejeitadas.slice(0, 4).map((c) => `✗ ${c}`).join("\n"), {
    x: xRej + 0.12, y: yTestes + 0.33, w: (wE - 0.2) / 2 - 0.24, h: 1.05,
    fontFace: FONTE_CODIGO, fontSize: 9, color: "7A2A1B", isTextBox: true, margin: 0, valign: "top",
    lineSpacingMultiple: 1.15,
  });

  // coluna direita: diagrama do AFNε
  const xD = 6.35, wD = 6.43;
  bloco(s, { x: xD, y: 1.75, w: wD, h: 4.85, fill: BRANCO });
  s.addText(`AFNε ${ficha.id}  —  ${ficha.estados} estados · ${ficha.transicoes} transições · ${ficha.eps} movimentos ε`, {
    x: xD + 0.15, y: 1.83, w: wD - 0.3, h: 0.3, fontFace: FONTE_CORPO, fontSize: 10.5,
    bold: true, color: MEIA_NOITE, isTextBox: true, margin: 0,
  });
  const arquivo = DIAG(ficha.id);
  s.addImage({ path: arquivo, x: xD + 0.15, y: 2.18, w: wD - 0.3, h: 4.28, sizing: { type: "contain", w: wD - 0.3, h: 4.28 } });

  rodape(s, indice);
  s.addNotes(
    `Apresentar ${ficha.id}: ler a ER formal, mostrar a sintaxe no código (são o mesmo padrão, ` +
    "por construção), demonstrar uma cadeia aceita e uma rejeitada lendo o AFNε ao lado, " +
    `e comentar o caso-limite: ${ficha.caso_limite}`
  );
  return s;
}

FICHAS.forEach((f, i) => slideER(f, i + 4));

// ---------------------------------------------------------------------------
// Slide 10 — caso-limite consolidado (transição para a demo)
// ---------------------------------------------------------------------------
{
  const s = pres.addSlide();
  cabecalho(s, "Os seis casos-limite", "Onde cada linguagem toca sua própria fronteira");
  const linhas = FICHAS.map((f) => [f.id, f.caso_limite.split(" — ")[0].replace(/^"|"$/g, "")]);
  let y = 1.85;
  const alturaLinha = 0.78;
  linhas.forEach(([id, texto], i) => {
    bloco(s, { x: 0.55, y, w: 12.23, h: alturaLinha - 0.12, fill: i % 2 === 0 ? GELO : BRANCO });
    s.addText(id, { x: 0.75, y: y + 0.06, w: 1.1, h: alturaLinha - 0.24,
      fontFace: FONTE_CODIGO, fontSize: 13, bold: true, color: AZUL_PROFUNDO,
      valign: "middle", isTextBox: true, margin: 0 });
    s.addText(texto, { x: 2.0, y: y + 0.06, w: 10.6, h: alturaLinha - 0.24,
      fontFace: FONTE_CODIGO, fontSize: 12, color: TEXTO, valign: "middle",
      isTextBox: true, margin: 0 });
    y += alturaLinha;
  });
  rodape(s, 10);
  s.addNotes(
    "Passar rapidamente pelos seis casos-limite juntos, mostrando o padrão comum: " +
    "todos ficam na fronteira de um fecho (opcional vazio, fecho positivo com zero ocorrências, " +
    "repetição fora do intervalo)."
  );
}

// ---------------------------------------------------------------------------
// Slide 11 — demonstração
// ---------------------------------------------------------------------------
{
  const s = pres.addSlide();
  cabecalho(s, "Demonstração", "Execução do programa sobre um registro real");

  bloco(s, { x: 0.55, y: 1.8, w: 12.23, h: 1.55, fill: "0E3A55" });
  s.addText("$ python main.py -l \"PA-BEL-004A|2026-09-21T14:35:02Z|-1.455833,-48.503889|TEMP=+27.4C;UMID=85%;PLUV=12.5mm|fw-v3.11.2-beta.4|!ALERTA:NIVEL2:CHUVA_FORTE\"", {
    x: 0.8, y: 1.98, w: 11.7, h: 0.5, fontFace: FONTE_CODIGO, fontSize: 11,
    color: "9FC3DA", isTextBox: true, margin: 0,
  });
  s.addText(
    "Registro VÁLIDO.\n" +
    "  estação   : PA-BEL-004A\n" +
    "  instante  : 2026-09-21T14:35:02+00:00\n" +
    "  leitura   : TEMP = 27.4 C\n" +
    "  firmware  : fw-v3.11.2-beta.4 (pré-lançamento)\n" +
    "  alerta    : nível 2 — CHUVA_FORTE",
    { x: 0.8, y: 2.5, w: 11.7, h: 0.85, fontFace: FONTE_CODIGO, fontSize: 11,
      color: BRANCO, isTextBox: true, margin: 0, valign: "top", lineSpacingMultiple: 1.05 }
  );

  const cartoes = [
    ["ER e AFNε concordam", "Toda validação exibe, lado a lado, o veredito da Expressão Regular e o da simulação do AFNε."],
    ["Trilha do autômato", "A opção -e/-c mostra o conjunto de estados após cada símbolo consumido, até o estado final."],
    ["Mensagens claras", "Arquivo inexistente, campo vazio ou ER desconhecida nunca geram rastreamento de erro."],
  ];
  let x = 0.55;
  const wCard = 3.94;
  for (const [titulo, texto] of cartoes) {
    bloco(s, { x, y: 3.65, w: wCard, h: 2.95 });
    s.addShape(pres.ShapeType.roundRect, {
      x: x + 0.25, y: 3.9, w: 0.55, h: 0.55, rectRadius: 0.28,
      fill: { color: AMBAR }, line: { type: "none" },
    });
    s.addText("›", { x: x + 0.25, y: 3.9, w: 0.55, h: 0.55, fontFace: FONTE_TITULO,
      fontSize: 22, bold: true, color: MEIA_NOITE, align: "center", valign: "middle",
      isTextBox: true, margin: 0 });
    s.addText(titulo, { x: x + 0.25, y: 4.58, w: wCard - 0.5, h: 0.45,
      fontFace: FONTE_TITULO, fontSize: 15, bold: true, color: MEIA_NOITE,
      isTextBox: true, margin: 0 });
    s.addText(texto, { x: x + 0.25, y: 5.05, w: wCard - 0.5, h: 1.45,
      fontFace: FONTE_CORPO, fontSize: 11.5, color: TEXTO, isTextBox: true,
      margin: 0, valign: "top" });
    x += wCard + 0.2;
  }
  rodape(s, 11);
  s.addNotes(
    "Executar ao vivo, se possível: python main.py -l \"...\" e depois " +
    "python main.py -e ER-03 -c \"TEMP=+27.4C\" para mostrar a trilha do AFNε. " +
    "O professor pode pedir novos dados de entrada aqui."
  );
}

// ---------------------------------------------------------------------------
// Slide 12 — testes e equivalência
// ---------------------------------------------------------------------------
{
  const s = pres.addSlide();
  cabecalho(s, "Testes automatizados", "78 testes — unittest da biblioteca padrão, sem dependências externas");

  const numeros = [
    ["72", "cadeias de teste\n(6 aceitas + 6 rejeitadas × 6 ER)"],
    ["432", "comparações ER × AFNε\nnas cadeias do projeto"],
    ["12 000", "cadeias aleatórias\nsorteadas sobre o alfabeto de cada AFNε"],
    ["7 200", "mutações de cadeias válidas\n(troca, remoção, inserção de símbolo)"],
  ];
  let x = 0.55;
  const wNum = 2.98;
  for (const [numero, legenda] of numeros) {
    bloco(s, { x, y: 1.85, w: wNum, h: 1.9, fill: "0E3A55" });
    s.addText(numero, { x, y: 2.0, w: wNum, h: 0.85, fontFace: FONTE_TITULO,
      fontSize: 34, bold: true, color: BRANCO, align: "center", isTextBox: true, margin: 0 });
    s.addText(legenda, { x: x + 0.15, y: 2.85, w: wNum - 0.3, h: 0.8,
      fontFace: FONTE_CORPO, fontSize: 11, color: "CADCFC", align: "center",
      isTextBox: true, margin: 0 });
    x += wNum + 0.13;
  }

  bloco(s, { x: 0.55, y: 4.0, w: 12.23, h: 1.1, fill: "EAF6EF", linha: "BFE1CC" });
  s.addText("Resultado: 0 divergências entre Expressão Regular e AFNε em todos os testes.", {
    x: 0.85, y: 4.22, w: 11.6, h: 0.6, fontFace: FONTE_TITULO, fontSize: 18,
    bold: true, color: VERDE_OK, isTextBox: true, margin: 0, valign: "middle",
  });

  bloco(s, { x: 0.55, y: 5.3, w: 12.23, h: 1.3 });
  s.addText("$ python -m unittest discover -s testes -t .\n$ python main.py -t   # bateria visual das cadeias de teste", {
    x: 0.85, y: 5.48, w: 11.6, h: 0.9, fontFace: FONTE_CODIGO, fontSize: 13,
    color: AZUL_PROFUNDO, isTextBox: true, margin: 0, valign: "top", lineSpacingMultiple: 1.3,
  });
  rodape(s, 12);
  s.addNotes(
    "Explicar as três camadas de teste: casos manuais (mínimo exigido), aleatórios e mutações. " +
    "A ausência de divergência em 19 mil e tantas comparações é a evidência prática de que " +
    "ER e AFNε representam a mesma linguagem."
  );
}

// ---------------------------------------------------------------------------
// Slide 13 — limitações e melhorias
// ---------------------------------------------------------------------------
{
  const s = pres.addSlide();
  cabecalho(s, "Limitações e melhorias possíveis", "O que uma linguagem regular não resolve — e o que fizemos a respeito");

  const linhas = [
    ["Datas, faixas geográficas e físicas", "A ER aceita \"2026-02-30\"; a checagem de calendário e de faixa é numérica, feita depois do reconhecimento."],
    ["Registro completo em uma única ER", "Optamos por 6 expressões menores e combináveis, mantendo cada AFNε legível para o diagrama."],
    ["Simulador de AFNε sem indexação", "Percorre a lista de transições a cada símbolo; irrelevante para os tamanhos deste trabalho (até 37 estados)."],
    ["Saída apenas em texto no terminal", "Próximo passo natural: exportar CSV/JSON e gerar gráficos por estação."],
  ];
  let y = 1.85;
  for (const [lim, mel] of linhas) {
    bloco(s, { x: 0.55, y, w: 5.95, h: 1.12 });
    s.addText(lim, { x: 0.75, y: y + 0.1, w: 5.55, h: 0.9, fontFace: FONTE_CORPO,
      fontSize: 12.5, bold: true, color: VERMELHO_NAO, isTextBox: true, margin: 0, valign: "top" });
    bloco(s, { x: 6.75, y, w: 6.03, h: 1.12, fill: "EAF6EF", linha: "BFE1CC" });
    s.addText(mel, { x: 6.95, y: y + 0.1, w: 5.65, h: 0.9, fontFace: FONTE_CORPO,
      fontSize: 11.5, color: "1E5B39", isTextBox: true, margin: 0, valign: "top" });
    y += 1.24;
  }
  rodape(s, 13);
  s.addNotes(
    "Deixar claro que essas limitações são inerentes ao modelo regular, não falhas de implementação — " +
    "e que a camada semântica do processador.py existe justamente para supri-las."
  );
}

// ---------------------------------------------------------------------------
// Slide 14 — contribuições
// ---------------------------------------------------------------------------
{
  const s = pres.addSlide();
  cabecalho(s, "Contribuição de cada integrante", "Divisão do trabalho ao longo do projeto");

  const linhas = [
    ["[NOME COMPLETO DO INTEGRANTE 1]", "ER-01 e ER-02  ·  módulo expressoes.py  ·  documentação e relatório técnico"],
    ["[NOME COMPLETO DO INTEGRANTE 2]", "ER-03 e ER-04  ·  módulo processador.py  ·  dados de exemplo"],
    ["[NOME COMPLETO DO INTEGRANTE 3]", "ER-05 e ER-06  ·  módulo automatos.py  ·  diagramas dos AFNε"],
    ["[NOME COMPLETO DO INTEGRANTE 4]", "módulos cli.py e relatorio.py  ·  testes automatizados  ·  apresentação"],
  ];
  let y = 1.9;
  linhas.forEach(([nome, contrib], i) => {
    bloco(s, { x: 0.55, y, w: 12.23, h: 1.05, fill: i % 2 === 0 ? GELO : BRANCO });
    s.addShape(pres.ShapeType.roundRect, {
      x: 0.8, y: y + 0.24, w: 0.58, h: 0.58, rectRadius: 0.29,
      fill: { color: TEAL }, line: { type: "none" },
    });
    s.addText(String(i + 1), { x: 0.8, y: y + 0.24, w: 0.58, h: 0.58,
      fontFace: FONTE_TITULO, fontSize: 18, bold: true, color: BRANCO,
      align: "center", valign: "middle", isTextBox: true, margin: 0 });
    s.addText(nome, { x: 1.65, y: y + 0.13, w: 4.4, h: 0.4, fontFace: FONTE_TITULO,
      fontSize: 14, bold: true, color: MEIA_NOITE, isTextBox: true, margin: 0, valign: "middle" });
    s.addText(contrib, { x: 1.65, y: y + 0.5, w: 10.8, h: 0.45, fontFace: FONTE_CORPO,
      fontSize: 11.5, color: TEXTO, isTextBox: true, margin: 0, valign: "middle" });
    y += 1.17;
  });
  s.addText("Uso de IA declarado em README.md e no relatório técnico — apoio em redação, organização de módulos e geração dos diagramas, sempre revisado e compreendido pela equipe.", {
    x: 0.55, y: 6.65, w: 12.23, h: 0.4, fontFace: FONTE_CORPO, fontSize: 10.5,
    italic: true, color: CINZA, isTextBox: true, margin: 0,
  });
  rodape(s, 14);
  s.addNotes(
    "Cada integrante confirma sua parte e demonstra domínio dela. " +
    "Mencionar rapidamente a declaração de uso de IA, conforme exigido pelo enunciado."
  );
}

// ---------------------------------------------------------------------------
// Slide 15 — encerramento
// ---------------------------------------------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: MEIA_NOITE };
  s.addText("Obrigado!", {
    x: 0.9, y: 2.7, w: W - 1.8, h: 1.1, fontFace: FONTE_TITULO, fontSize: 54,
    bold: true, color: BRANCO, isTextBox: true, margin: 0,
  });
  s.addText("Perguntas, novos dados de entrada ou alterações — à disposição para a demonstração.", {
    x: 0.9, y: 3.85, w: W - 1.8, h: 0.5, fontFace: FONTE_CORPO, fontSize: 16,
    color: "CADCFC", isTextBox: true, margin: 0,
  });
  s.addText("Repositório e documentação completa: README.md  ·  docs/expressoes_regulares.md  ·  docs/afne_formal.md", {
    x: 0.9, y: 6.7, w: W - 1.8, h: 0.4, fontFace: FONTE_CODIGO, fontSize: 11,
    color: "8FA9C2", isTextBox: true, margin: 0,
  });
  s.addNotes("Encerramento. Convidar perguntas e se dispor a rodar o programa com dados fornecidos pelo professor.");
}

// ---------------------------------------------------------------------------
const destino = path.join(RAIZ, "docs", "apresentacao.pptx");
pres.writeFile({ fileName: destino }).then(() => {
  console.log("gerado:", path.relative(RAIZ, destino));
});
