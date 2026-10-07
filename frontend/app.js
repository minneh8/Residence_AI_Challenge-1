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


// números no formato brasileiro, com 4 casas (os scores são pequenos, ex.: 0,0158)
const fmt = (v) => (v == null ? "–" : v.toLocaleString("pt-BR", { minimumFractionDigits: 4, maximumFractionDigits: 4 }));

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
    const t = c.tipico || {};
    corpo.append(el("tr", {},
      el("td", {}, c.nome, el("span", { class: "explica" }, c.explicacao)),
      el("td", { class: "num" }, fmt(c.score)),
      el("td", { class: "num" }, fmt(t.mediana)),
      el("td", { class: "num" }, `${fmt(t.q1)} a ${fmt(t.q3)}`),
      el("td", { class: "situacao" + (fora ? " fora" : "") }, c.situacao),
    ));
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
      el("li", {}, `${c.nome}: ${c.situacao} (score ${fmt(c.score)}; faixa comum de ${fmt(c.tipico.q1)} a ${fmt(c.tipico.q3)}).`))));
  }

  renderRegua($("#regua"), d.criterios.map((c) => ({
    ...c,
    texto: c.situacao,
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
// Cada linha tem a sua própria escala, no VALOR do critério (não no percentil):
// vai do valor baixo ao valor alto mais comuns no perfil (90% das notícias cabem na linha).
function renderRegua(alvo, linhas, porClasse = false) {
  alvo.replaceChildren();
  for (const l of linhas) {
    const [lo, hi] = l.escala;
    const pos = (v) => Math.min(100, Math.max(0, ((v - lo) / (hi - lo)) * 100));
    const trilho = el("div", { class: "trilho" });

    if (!porClasse) {
      // metade central do perfil (Q1 a Q3) e o valor típico (mediana)
      const t = l.tipico;
      trilho.append(
        el("div", { class: "banda", style: { left: pos(t.q1) + "%", width: Math.max(pos(t.q3) - pos(t.q1), 0.8) + "%" } }),
        el("div", { class: "traco-tipico", style: { left: pos(t.mediana) + "%" }, title: `Típico (mediana): ${fmt(t.mediana)}` }),
      );
    } else {
      for (const cls of ["falsas", "verdadeiras"]) {
        const f = l[cls];
        const nome = cls === "falsas" ? "falsa" : "verdadeira";
        const topo = cls === "falsas" ? 1 : 15;
        trilho.append(
          el("div", { class: `classe ${nome}`, style: { left: pos(f.q1) + "%", width: Math.max(pos(f.q3) - pos(f.q1), 0.8) + "%" },
            title: `${cls === "falsas" ? "Falsas" : "Verdadeiras"}: metade central de ${fmt(f.q1)} a ${fmt(f.q3)}` }),
          el("div", { class: "mediana", style: { left: pos(f.mediana) + "%", top: topo + "px" }, title: `Mediana: ${fmt(f.mediana)}` }),
        );
      }
    }

    // a notícia; fora da escala, o ponto fica na borda e a seta indica o lado
    const p = pos(l.score);
    const rotulo = l.score > hi ? `${fmt(l.score)} →` : l.score < lo ? `← ${fmt(l.score)}` : fmt(l.score);
    trilho.append(
      el("div", { class: "ponto", style: { left: p + "%" }, title: `Sua notícia: ${fmt(l.score)}` }),
      el("span", { class: "valor", style: { left: Math.min(Math.max(p, 6), 94) + "%" } }, rotulo),
      el("span", { class: "extremo ini" }, fmt(lo)),
      el("span", { class: "extremo fim" }, fmt(hi)),
    );
    alvo.append(el("div", { class: "linha-regua" },
      el("span", { class: "rotulo-regua" }, l.nome),
      trilho,
      el("span", { class: "lado " + (l.forte ? "forte" : "fraco") }, l.texto),
    ));
  }
}

// ---------------------------------------------------------------- radar
function renderRadar(alvo, r) {
  const NS = "http://www.w3.org/2000/svg";
  const s = (tag, attrs = {}) => {
    const n = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
    return n;
  };
  const W = 780, H = 520, cx = W / 2, cy = H / 2, R = 185, max = 1.15;
  const n = r.eixos.length;
  const ang = (i) => -Math.PI / 2 + (2 * Math.PI * i) / n;
  const pt = (i, v) => [cx + (R * v / max) * Math.cos(ang(i)), cy + (R * v / max) * Math.sin(ang(i))];
  const poli = (vals) => vals.map((v, i) => pt(i, v).join(",")).join(" ");

  const svg = s("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": "Radar: notícia analisada sobre a notícia típica do perfil" });
  // teia: fundo levemente mais claro, anéis e eixos bem visíveis (o anel de fora é o mais forte)
  svg.append(s("polygon", { points: poli(Array(n).fill(1)), fill: "rgba(255,255,255,.06)", stroke: "none" }));
  for (const anel of [0.25, 0.5, 0.75, 1]) {
    svg.append(s("polygon", { points: poli(Array(n).fill(anel)), fill: "none",
      stroke: anel === 1 ? "rgba(255,255,255,.85)" : "rgba(255,255,255,.55)", "stroke-width": anel === 1 ? 2 : 1.4 }));
  }
  r.eixos.forEach((nome, i) => {
    const [x, y] = pt(i, max);
    svg.append(s("line", { x1: cx, y1: cy, x2: x, y2: y, stroke: "rgba(255,255,255,.55)", "stroke-width": 1.4 }));
    const [lx, ly] = pt(i, max * 1.2);
    const cos = Math.cos(ang(i));
    const anchor = Math.abs(cos) < 0.2 ? "middle" : cos > 0 ? "start" : "end";
    const t = s("text", { x: lx, y: ly, "text-anchor": anchor, fill: "#f2f5fb", "font-size": 16 });
    const partes = nome.split(" ");
    const meio = Math.ceil(partes.length / 2);
    const linhas = partes.length > 2 || (partes.length === 2 && nome.length > 16) ? [partes.slice(0, meio).join(" "), partes.slice(meio).join(" ")] : [nome];
    linhas.forEach((txt, k) => {
      const ts = s("tspan", { x: lx, dy: k === 0 ? (linhas.length > 1 ? -5 : 5) : 18 });
      ts.textContent = txt;
      t.append(ts);
    });
    svg.append(t);
  });
  // notícia típica em amarelo: contorno desenhado por cima da notícia para não sumir
  const AMARELO = "#ffd166";
  svg.append(s("polygon", { points: poli(r.tipica), fill: "rgba(255,209,102,.16)", stroke: "none" }));
  svg.append(s("polygon", { points: poli(r.noticia), fill: "rgba(141,184,255,.30)", stroke: "#8db8ff", "stroke-width": 3 }));
  svg.append(s("polygon", { points: poli(r.tipica), fill: "none", stroke: AMARELO, "stroke-width": 3, "stroke-dasharray": "8 5" }));
  r.tipica.forEach((v, i) => {
    const [x, y] = pt(i, v);
    svg.append(s("rect", { x: x - 4.5, y: y - 4.5, width: 9, height: 9, fill: AMARELO, stroke: "#14244a", "stroke-width": 1.5 }));
  });
  r.noticia.forEach((v, i) => {
    const [x, y] = pt(i, v);
    svg.append(s("circle", { cx: x, cy: y, r: 5.5, fill: "#8db8ff", stroke: "#fff", "stroke-width": 2 }));
  });

  const legenda = el("div", { class: "legenda" },
    el("span", {}, el("i", { class: "tipica" }), "Notícia típica do perfil (mediana)"),
    el("span", {}, el("i", { class: "ponto" }), "Sua notícia"));
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

  const TXT = { falsas: "tende para falsa", verdadeiras: "tende para verdadeira" };
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
