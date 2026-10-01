// Features da tabela (valores fixos de exemplo, como no projeto original)
const FEATURES = [
  ["tamanho_medio_palavra","0,2"],["pct_erro_ortografico","0,3"],["estudos_previos_proporcao","0,07"],
  ["fontes_proporcao","0,9"],["emotividade","0,55"],["sensacionalismo_proporcao","0,15"],
  ["verbos_proporcao","0,85"],["verbos_subj_imp_proporcao","0,55"],["substantivos_proporcao","0,15"],
  ["adjetivos_proporcao","0,85"],["adverbios_proporcao","0,55"],["modais_proporcao","0,15"],
  ["pronomes_proporcao","0,2"],["pausalidade","0,3"],["indice_legibilidade","0,07"],
  ["tamanho_medio_frase","0,2"]
];

const entrada = document.getElementById("entrada");
let noticiaAtual = "";

// Preenche as tabelas das páginas 2 e 3
document.querySelectorAll(".corpo-tabela").forEach(tbody => {
  FEATURES.forEach(([nome, valor]) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${nome}</td><td>${valor}</td>`;
    tbody.appendChild(tr);
  });
});

// Mostra uma página e esconde as outras
function mostrarPagina(id) {
  document.querySelectorAll(".pagina").forEach(p => p.classList.toggle("ativa", p.id === id));
}

// Limita a notícia exibida a 50 palavras
function resumirNoticia(texto, limite = 50) {
  const palavras = texto.split(/\s+/).filter(Boolean);
  return palavras.length > limite ? palavras.slice(0, limite).join(" ") + "..." : texto;
}

function mostrarPagina1() { 
  mostrarPagina("pagina1"); 
  entrada.focus(); 
}

function mostrarPagina3(texto) { 
  noticiaAtual = texto; 
  mostrarPagina("pagina3"); 
}

function mostrarPagina2(texto) {
  document.getElementById("texto-noticia").textContent = resumirNoticia(texto);
  mostrarVista("tabela");
  mostrarPagina("pagina2");
}

// Alterna a página 2 entre a tabela e os gráficos (e destaca o botão correspondente)
function mostrarVista(vista) {
  const graficos = vista === "graficos";
  document.getElementById("vista-tabela").classList.toggle("oculto", graficos);
  document.getElementById("vista-graficos").classList.toggle("visivel", graficos);
  document.getElementById("btn-ver-tabela").classList.toggle("ativo", !graficos);
  document.getElementById("btn-ver-graficos").classList.toggle("ativo", graficos);
}

// Recomeça do zero: apaga a notícia digitada/guardada e volta ao estado inicial
function reiniciar() {
  entrada.value = "";
  noticiaAtual = "";
  document.getElementById("texto-noticia").textContent = "";
  document.getElementById("texto-noticia-5").textContent = "";
  mostrarVista("tabela");
  document.querySelectorAll(".tabela-scroll").forEach(el => { el.scrollTop = 0; el.scrollLeft = 0; });
  window.scrollTo(0, 0);
  mostrarPagina1();
}

// Envio da notícia (botão ou Enter)
function enviar() {
  const texto = entrada.value.trim();
  if (!texto) { 
    alert("Digite algo antes de enviar."); 
    return; 
  }

  console.log("Enviado:", texto);
  mostrarPagina3(texto);
}

document.getElementById("btn-enviar").addEventListener("click", enviar);
entrada.addEventListener("keydown", e => { if (e.key === "Enter") enviar(); });
document.getElementById("btn-avancar").addEventListener("click", () => mostrarPagina("pagina4"));
document.querySelectorAll(".logo-voltar").forEach(l => l.addEventListener("click", reiniciar));
document.getElementById("btn-voltar").addEventListener("click", mostrarPagina1);
document.getElementById("btn-voltar-2").addEventListener("click", () => mostrarPagina("pagina4"));

// ---------- PÁGINA 4: exemplos de notícias ----------
// Dados de exemplo (fixos): 5 verdadeiras e 5 falsas. Troque pelos valores reais quando tiver o cálculo.
const PERFIL_VERDADEIRA = [0.45,0.10,0.70,0.85,0.30,0.10,0.55,0.35,0.40,0.35,0.30,0.25,0.30,0.45,0.70,0.50];
const PERFIL_FALSA      = [0.35,0.45,0.10,0.15,0.80,0.75,0.60,0.60,0.20,0.70,0.65,0.45,0.40,0.70,0.25,0.30];
const NOTICIAS = [
  ["Governo anuncia novo calendário de vacinação, segundo o Ministério da Saúde", true],
  ["Pesquisa da USP aponta queda no desmatamento da Amazônia em 2025", true],
  ["Banco Central mantém a taxa de juros após reunião do Copom", true],
  ["Prefeitura inaugura nova linha de ônibus ligando zona sul ao centro", true],
  ["Estudo publicado em revista científica relaciona sono e desempenho escolar", true],
  ["URGENTE: remédio caseiro cura todas as doenças e médicos escondem a verdade!", false],
  ["Você não vai acreditar o que aconteceu com famoso ao sair do mercado", false],
  ["Compartilhe antes que apaguem: governo vai confiscar poupanças amanhã", false],
  ["Cientistas chocados: dieta de 3 dias elimina 10 kg sem esforço", false],
  ["Bomba! Político é flagrado em esquema secreto, mas a mídia não mostra", false],
];

// Gerador pseudoaleatório fixo (os valores não mudam a cada abertura)
function gerarValores(perfil, semente) {
  let x = semente;
  const rand = () => (x = (x * 9301 + 49297) % 233280) / 233280;
  return perfil.map(v => Math.min(1, Math.max(0, v + (rand() - 0.5) * 0.16)));
}

function montarTabelaExemplos() {
  const thead = document.querySelector("#tabela-exemplos thead");
  const tbody = document.querySelector("#tabela-exemplos tbody");
  thead.innerHTML = "<tr><th class='col-noticia'>Notícia</th><th>Rótulo</th>" +
    FEATURES.map(([nome]) => `<th>${nome}</th>`).join("") + "</tr>";
  NOTICIAS.forEach(([titulo, verdadeira], i) => {
    const valores = gerarValores(verdadeira ? PERFIL_VERDADEIRA : PERFIL_FALSA, 17 + i * 31);
    const tr = document.createElement("tr");
    const tdTitulo = document.createElement("td");
    tdTitulo.className = "col-noticia";
    tdTitulo.textContent = titulo;
    const tdRotulo = document.createElement("td");
    tdRotulo.innerHTML = `<span class="rotulo-tag ${verdadeira ? "verdadeira" : "falsa"}">${verdadeira ? "Verdadeira" : "Falsa"}</span>`;
    tr.append(tdTitulo, tdRotulo);
    valores.forEach(v => {
      const td = document.createElement("td");
      td.textContent = v.toFixed(2).replace(".", ",");
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
}
montarTabelaExemplos();

document.getElementById("btn-avancar-2").addEventListener("click", mostrarPagina5);
document.getElementById("btn-ver-tabela").addEventListener("click", () => mostrarVista("tabela"));
document.getElementById("btn-ver-graficos").addEventListener("click", () => mostrarVista("graficos"));
document.getElementById("btn-voltar-4").addEventListener("click", () => mostrarPagina("pagina3"));
document.getElementById("btn-avancar-4").addEventListener("click", () => mostrarPagina2(noticiaAtual));
document.getElementById("btn-voltar-5").addEventListener("click", () => mostrarPagina("pagina2"));
document.getElementById("btn-voltar-6").addEventListener("click", () => mostrarPagina("pagina5"));
document.getElementById("btn-voltar-7").addEventListener("click", () => mostrarPagina("pagina5"));
document.getElementById("btn-verdadeira").addEventListener("click", () => escolher("verdadeira"));
document.getElementById("btn-falsa").addEventListener("click", () => escolher("falsa"));
document.querySelectorAll(".btn-nova").forEach(b => b.addEventListener("click", reiniciar));

// ---------- PÁGINAS 5, 6 e 7: palpite do usuário x resposta do modelo ----------
// Resposta do modelo para a notícia enviada ("verdadeira" ou "falsa").
// Valor fixo de exemplo: troque pelo resultado real do modelo quando ele estiver integrado.
let RESULTADO_MODELO = "verdadeira";

function mostrarPagina5() {
  document.getElementById("texto-noticia-5").textContent = resumirNoticia(noticiaAtual);
  mostrarPagina("pagina5");
}

// Compara o palpite do usuário com o modelo: concordou -> página 6; discordou -> página 7
function escolher(palpite) {
  const nomes = { verdadeira: "Verdadeira", falsa: "Falsa" };
  document.querySelectorAll(".escolha-usuario").forEach(e => e.textContent = nomes[palpite]);
  document.querySelectorAll(".escolha-modelo").forEach(e => e.textContent = nomes[RESULTADO_MODELO]);
  mostrarPagina(palpite === RESULTADO_MODELO ? "pagina6" : "pagina7");
}

// ESC: no navegador não dá para fechar a aba por script, então volta ao início
document.addEventListener("keydown", e => { if (e.key === "Escape") mostrarPagina1(); });