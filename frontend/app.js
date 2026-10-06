// DUAT — frontend. Fala com o backend em /api (mesmo endereço por padrão).
const API = window.DUAT_API || "";

const $ = (s) => document.querySelector(s);
const app = $("#app");
const form = $("#form-noticia");
const texto = $("#texto");
const enviar = $("#enviar");
const status = $("#status");
const resultado = $("#resultado");
const avaliacao = $("#avaliacao");
let idAnalise = null;

// cria um elemento com texto (nunca HTML vindo de fora)
function el(tag, attrs = {}, ...filhos) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") n.className = v;
    else if (k === "style") Object.assign(n.style, v);
    else n.setAttribute(k, v);
  }
  for (const f of filhos) if (f != null) n.append(f);
  return n;
}

async function chamar(rota, corpo) {
  const r = await fetch(API + rota, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(corpo),
  });
  const dados = await r.json().catch(() => ({}));
  if (!r.ok) {
    const msg = typeof dados.detail === "string" ? dados.detail : "Não foi possível concluir a análise.";
    throw new Error(msg);
  }
  return dados;
}

function mostrarStatus(msg, erro = false) {
  status.textContent = msg;
  status.classList.toggle("erro", erro);
}

// ---------------------------------------------------------------- textarea
function ajustarAltura() {
  texto.style.height = "auto";
  texto.style.height = texto.scrollHeight + 3 + "px";
}
texto.addEventListener("input", ajustarAltura);
texto.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) form.requestSubmit();
});

// ---------------------------------------------------------------- 1) análise
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const conteudo = texto.value.trim();
  if (!conteudo) return;
  enviar.disabled = true;
  resultado.hidden = true;
  app.className = "resultado";
  mostrarStatus("Analisando a notícia...");
  try {
    const dados = await chamar("/api/analisar", { texto: conteudo });
    idAnalise = dados.id;
    renderAnalise(dados);
    mostrarStatus("");
    resultado.hidden = false;
    resultado.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (err) {
    mostrarStatus(err.message, true);
  } finally {
    enviar.disabled = false;
  }
});

const SITUACAO = {
  "abaixo do comum": "abaixo da faixa típica",
  "dentro do comum": "dentro da faixa típica",
  "acima do comum": "acima da faixa típica",
};

// trecho da frase do percentil, adaptado a cada critério
const FRASE_PERCENTIL = {
  tamanho_medio_palavra: "possuem o Tamanho médio da palavra",
  pct_erro_ortografico: "têm uma porcentagem de Erros ortográficos",
  fontes_proporcao: "têm uma proporção de Fontes citadas",
  estudos_previos_proporcao: "têm uma proporção de Estudos prévios citados",
  emotividade: "têm um nível de Emotividade",
  sensacionalismo_proporcao: "têm uma proporção de Palavras sensacionalistas",
  verbos_proporcao: "têm uma proporção de Verbos",
  verbos_subj_imp_proporcao: "têm uma proporção de Verbos de dúvida ou de ordem",
  substantivos_proporcao: "têm uma proporção de Substantivos",
  adjetivos_proporcao: "têm uma proporção de Adjetivos",
  adverbios_proporcao: "têm uma proporção de Advérbios",
  modais_proporcao: "têm uma proporção de Verbos modais",
  pronomes_proporcao: "têm uma proporção de Pronomes",
  pausalidade: "têm um nível de Pausalidade",
  indice_legibilidade: "possuem o Índice de legibilidade",
  tamanho_medio_frase: "possuem o Tamanho médio da frase",
};
const frasePercentil = (c) => FRASE_PERCENTIL[c.feature] || `têm ${c.nome}`;

function renderAnalise(d) {
  $("#perfil-nome").textContent = d.perfil.nome;
  $("#perfil-descricao").textContent =
    `${d.perfil.descricao.charAt(0).toUpperCase()}${d.perfil.descricao.slice(1)}. ` +
    `A notícia é comparada com as ${d.perfil.noticias_no_perfil.toLocaleString("pt-BR")} notícias do dataset neste perfil.`;

  const avisos = $("#avisos");
  avisos.replaceChildren();
  if (d.aviso_texto_curto)
    avisos.append(el("li", {}, `O texto tem ${d.n_palavras} palavras. Textos curtos geram critérios pouco confiáveis; se possível, use a notícia completa.`));
  if (d.fora_da_faixa.length)
    avisos.append(el("li", {}, `Valores fora da faixa do dataset: ${d.fora_da_faixa.join(", ")}.`));

  // tabela
  const corpo = $("#tabela");
  corpo.replaceChildren();
  for (const c of d.criterios) {
    const fora = c.situacao !== "dentro do comum";
    const p = Math.round(c.percentil);
    const detalhe = el("tr", { class: "detalhe", hidden: "" },
      el("td", { colspan: "4" },
        el("p", {}, `${p}% das notícias do perfil ${frasePercentil(c)} menor que a sua notícia`),
        el("p", {}, `${100 - p}% das notícias do perfil ${frasePercentil(c)} maior que a sua notícia`)));
    const botao = el("button", { type: "button", class: "pct", "aria-expanded": "false",
      title: "Clique para ver o que significa" }, String(p));
    botao.addEventListener("click", () => {
      const aberto = detalhe.hidden;
      detalhe.hidden = !aberto;
      botao.setAttribute("aria-expanded", String(aberto));
    });
    corpo.append(el("tr", {},
      el("td", {}, c.nome, el("span", { class: "explica" }, c.explicacao)),
      el("td", { class: "num" }, c.score != null ? c.score.toFixed(4) : "–"),
      el("td", { class: "num" }, botao),
      el("td", { class: "situacao" + (fora ? " fora" : "") }, c.situacao),
    ), detalhe);
  }

  // mensagem de critérios fora do comum
  const caixa = $("#fora-do-comum");
  caixa.replaceChildren();
  const foraLista = d.criterios.filter((c) => c.situacao !== "dentro do comum");
  if (!foraLista.length) {
    caixa.append(el("p", {}, "Todos os critérios prioritários estão dentro da faixa comum para notícias deste perfil."));
  } else {
    caixa.append(el("strong", {}, "Critérios que fogem do comum para notícias deste perfil:"));
    caixa.append(el("ul", {}, ...foraLista.map((c) =>
      el("li", {}, `${c.nome}: ${c.situacao} (percentil ${Math.round(c.percentil)}).`))));
  }

  renderRegua($("#regua"), d.criterios.map((c) => ({
    nome: c.nome,
    percentil: c.percentil,
    texto: SITUACAO[c.situacao],
    forte: c.situacao !== "dentro do comum",
  })));
  renderRadar($("#radar"), d.radar);

  // reinicia a pergunta e esconde a avaliação anterior
  avaliacao.hidden = true;
  document.querySelectorAll(".opcoes button").forEach((b) => {
    b.disabled = false;
    b.classList.remove("escolhida");
  });
}

// ---------------------------------------------------------------- régua
function renderRegua(alvo, linhas, porClasse = false) {
  alvo.replaceChildren();
  for (const l of linhas) {
    const trilho = el("div", { class: "trilho" });
    if (!porClasse) {
      trilho.append(el("div", { class: "banda", style: { left: "25%", width: "50%" } }));
    } else {
      for (const cls of ["falsas", "verdadeiras"]) {
        const f = l[cls];
        const nome = cls === "falsas" ? "falsa" : "verdadeira";
        const larg = Math.max(f.q3 - f.q1, 1);
        const barra = el("div", { class: `classe ${nome}`, style: { left: f.q1 + "%", width: larg + "%" } });
        const topo = cls === "falsas" ? 2 : 14;
        trilho.append(barra, el("div", { class: "mediana", style: { left: f.mediana + "%", top: topo + "px" } }));
      }
    }
    trilho.append(
      el("div", { class: "ponto", style: { left: l.percentil + "%" }, title: `Percentil ${Math.round(l.percentil)}` }),
      el("span", { class: "valor", style: { left: l.percentil + "%" } }, String(Math.round(l.percentil))),
    );
    alvo.append(el("div", { class: "linha-regua" },
      el("span", { class: "rotulo-regua" }, l.nome),
      trilho,
      el("span", { class: "lado " + (l.forte ? "forte" : "fraco") }, l.texto),
    ));
  }
  const marcas = el("div", { class: "marcas" },
    ...[0, 25, 50, 75, 100].map((v) => el("span", { style: { left: v + "%" } }, String(v))));
  alvo.append(el("div", { class: "eixo" }, el("span"), marcas, el("span")));
}

// ---------------------------------------------------------------- radar
function renderRadar(alvo, r) {
  const NS = "http://www.w3.org/2000/svg";
  const s = (tag, attrs = {}) => {
    const n = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
    return n;
  };
  const W = 680, H = 470, cx = W / 2, cy = H / 2, R = 165, max = 1.15;
  const n = r.eixos.length;
  const ang = (i) => -Math.PI / 2 + (2 * Math.PI * i) / n;
  const pt = (i, v) => [cx + (R * v / max) * Math.cos(ang(i)), cy + (R * v / max) * Math.sin(ang(i))];
  const poli = (vals) => vals.map((v, i) => pt(i, v).join(",")).join(" ");

  const svg = s("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": "Radar: notícia analisada sobre a notícia típica do perfil" });
  for (const anel of [0.25, 0.5, 0.75, 1]) {
    svg.append(s("polygon", { points: poli(Array(n).fill(anel)), fill: "none", stroke: "rgba(255,255,255,.12)" }));
  }
  r.eixos.forEach((nome, i) => {
    const [x, y] = pt(i, max);
    svg.append(s("line", { x1: cx, y1: cy, x2: x, y2: y, stroke: "rgba(255,255,255,.12)" }));
    const [lx, ly] = pt(i, max * 1.2);
    const cos = Math.cos(ang(i));
    const anchor = Math.abs(cos) < 0.2 ? "middle" : cos > 0 ? "start" : "end";
    const t = s("text", { x: lx, y: ly, "text-anchor": anchor, fill: "#e7ecf6", "font-size": 14 });
    const partes = nome.split(" ");
    const meio = Math.ceil(partes.length / 2);
    const linhas = partes.length > 2 ? [partes.slice(0, meio).join(" "), partes.slice(meio).join(" ")] : [nome];
    linhas.forEach((txt, k) => {
      const ts = s("tspan", { x: lx, dy: k === 0 ? (linhas.length > 1 ? -4 : 4) : 16 });
      ts.textContent = txt;
      t.append(ts);
    });
    svg.append(t);
  });
  svg.append(s("polygon", { points: poli(r.tipica), fill: "rgba(255,255,255,.10)", stroke: "#9fb0d1", "stroke-width": 1.5, "stroke-dasharray": "5 4" }));
  svg.append(s("polygon", { points: poli(r.noticia), fill: "rgba(122,167,255,.20)", stroke: "#7aa7ff", "stroke-width": 2.2 }));
  r.noticia.forEach((v, i) => {
    const [x, y] = pt(i, v);
    svg.append(s("circle", { cx: x, cy: y, r: 3.5, fill: "#7aa7ff" }));
  });

  const legenda = el("div", { class: "legenda" },
    el("span", {}, el("i", { class: "tipica" }), "Notícia típica do perfil (mediana)"),
    el("span", {}, el("i", { class: "ponto" }), "Notícia analisada"));
  alvo.replaceChildren(el("div", {}, svg, legenda));
}

// ---------------------------------------------------------------- 2) resposta e SVM
document.querySelectorAll(".opcoes button").forEach((botao) => {
  botao.addEventListener("click", async () => {
    if (!idAnalise) return;
    document.querySelectorAll(".opcoes button").forEach((b) => (b.disabled = true));
    botao.classList.add("escolhida");
    mostrarStatus("Consultando o modelo...");
    try {
      const d = await chamar("/api/avaliar", { id: idAnalise, resposta: botao.dataset.resposta });
      renderAvaliacao(d);
      mostrarStatus("");
      avaliacao.hidden = false;
      avaliacao.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (err) {
      mostrarStatus(err.message, true);
      document.querySelectorAll(".opcoes button").forEach((b) => (b.disabled = false));
      botao.classList.remove("escolhida");
    }
  });
});

function renderAvaliacao(d) {
  const rot = d.modelo.rotulo;
  $("#veredito").replaceChildren(
    "A notícia tem características de notícia ",
    el("span", { class: `rotulo ${rot}` }, rot.toUpperCase()), ".");
  $("#seguranca").textContent =
    `Segurança da avaliação: ${d.modelo.seguranca}, em comparação com as notícias do dataset. Não é uma probabilidade de acerto.`;
  $("#comparacao").textContent = d.comparacao;

  const listas = $("#listas");
  listas.replaceChildren();
  const ordem = rot === "falsa"
    ? [["falsas", d.criterios_como_falsas], ["verdadeiras", d.criterios_como_verdadeiras]]
    : [["verdadeiras", d.criterios_como_verdadeiras], ["falsas", d.criterios_como_falsas]];
  for (const [classe, itens] of ordem) {
    if (itens.length)
      listas.append(el("p", {}, el("strong", {}, `Se parece com as notícias ${classe} deste perfil: `), itens.join(", ") + "."));
  }

  const TXT = { falsas: "mais perto das falsas", verdadeiras: "mais perto das verdadeiras" };
  renderRegua($("#regua-classe"), d.por_classe.map((c) => ({
    ...c,
    texto: c.lado ? TXT[c.lado] : "não distingue as classes",
    forte: Boolean(c.lado),
  })), true);
}

// ---------------------------------------------------------------- nova análise
$("#nova").addEventListener("click", () => {
  idAnalise = null;
  texto.value = "";
  ajustarAltura();
  resultado.hidden = true;
  avaliacao.hidden = true;
  app.className = "inicio";
  mostrarStatus("");
  window.scrollTo({ top: 0 });
  texto.focus();
});
