const API_BASE_URL = 'http://localhost:8000';

const state = {
  text: '',
  features: {},
  result: null,
  pipeline: 'svm',
  userChoice: null
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

function showPage(pageId) {
  $$('.pagina').forEach((page) => page.classList.remove('ativa'));
  const page = $(`#${pageId}`);
  if (page) page.classList.add('ativa');
}

function setCells(tbody, values) {
  if (!tbody) return;
  tbody.innerHTML = '';
  Object.entries(values || {}).forEach(([name, value]) => {
    const row = document.createElement('tr');
    const featureCell = document.createElement('td');
    const valueCell = document.createElement('td');
    featureCell.textContent = name;
    valueCell.textContent = typeof value === 'number' ? value.toFixed(6) : String(value);
    row.append(featureCell, valueCell);
    tbody.appendChild(row);
  });
}

function fillFeatureTables(features) {
  $$('.corpo-tabela').forEach((tbody) => setCells(tbody, features));
}

function setText(selector, value) {
  const element = $(selector);
  if (element) element.textContent = value || '';
}

function pipelineName(name) {
  return {
    svm: 'SVM',
    kmeans: 'K-Means',
    pipeline_kmeans_duat: 'K-Means DUAT',
    dbscan: 'DBSCAN + Isolation Forest',
    isolation_forest: 'DBSCAN + Isolation Forest',
    duat_dbscan_isolation_forest: 'DBSCAN + Isolation Forest'
  }[name] || name;
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail || `Erro HTTP ${response.status}`);
  return body;
}

async function analyzeText() {
  const input = $('#entrada');
  const button = $('#btn-enviar');
  const text = input?.value.trim() || '';
  if (text.length < 20) {
    alert('Digite uma notícia com pelo menos 20 caracteres.');
    return;
  }

  state.text = text;
  if (button) {
    button.disabled = true;
    button.textContent = 'Analisando...';
  }

  try {
    const featureResponse = await request('/features', {
      method: 'POST',
      body: JSON.stringify({ text })
    });
    state.features = featureResponse.features || {};
    fillFeatureTables(state.features);
    setText('#texto-noticia', text);
    setText('#texto-noticia-5', text);
    showPage('pagina3');
  } catch (error) {
    alert(`Não foi possível conectar ao backend: ${error.message}`);
  } finally {
    if (button) {
      button.disabled = false;
      button.textContent = 'Enviar';
    }
  }
}

async function runPipeline(pipeline = state.pipeline) {
  state.pipeline = pipeline;
  const isCombined = pipeline === 'duat_dbscan_isolation_forest' || pipeline === 'dbscan' || pipeline === 'isolation_forest';
  const endpoint = isCombined ? '/anomaly' : '/predict';
  return request(endpoint, {
    method: 'POST',
    body: JSON.stringify({ text: state.text, pipeline, features: state.features })
  });
}

function modelLabel(data) {
  if (data.classification === 'fake') return 'Falsa';
  if (data.classification === 'true') return 'Verdadeira';
  if (data.classification === 'anomaly') return 'Anomalia';
  if (data.classification === 'normal') return 'Normal';
  if (data.label !== null && data.label !== undefined) return `Cluster ${data.label}`;
  return 'Indisponível';
}

async function continueFromFeatures() {
  try {
    const data = await runPipeline('svm');
    state.result = data;
    showPage('pagina2');
  } catch (error) {
    alert(`Não foi possível executar o pipeline: ${error.message}`);
  }
}

function showUserDecision(choice) {
  state.userChoice = choice;
  const modelChoice = modelLabel(state.result || {});
  const normalizedModel = modelChoice.toLowerCase();
  const agrees = (choice === 'Verdadeira' && normalizedModel === 'verdadeira')
    || (choice === 'Falsa' && normalizedModel === 'falsa');
  const page = agrees ? 'pagina6' : 'pagina7';
  $$('.escolha-usuario').forEach((element) => { element.textContent = choice; });
  $$('.escolha-modelo').forEach((element) => { element.textContent = modelChoice; });
  showPage(page);
}

function setupNavigation() {
  $('#btn-enviar')?.addEventListener('click', analyzeText);
  $('#entrada')?.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') analyzeText();
  });
  $('#btn-avancar')?.addEventListener('click', continueFromFeatures);
  $('#btn-avancar-2')?.addEventListener('click', () => showPage('pagina4'));
  $('#btn-avancar-4')?.addEventListener('click', () => showPage('pagina5'));
  $('#btn-verdadeira')?.addEventListener('click', () => showUserDecision('Verdadeira'));
  $('#btn-falsa')?.addEventListener('click', () => showUserDecision('Falsa'));

  $('#btn-ver-tabela')?.addEventListener('click', () => {
    $('#vista-tabela')?.classList.remove('oculto');
    $('#vista-graficos')?.classList.remove('visivel');
    $('#btn-ver-tabela')?.classList.add('ativo');
    $('#btn-ver-graficos')?.classList.remove('ativo');
  });
  $('#btn-ver-graficos')?.addEventListener('click', () => {
    $('#vista-tabela')?.classList.add('oculto');
    $('#vista-graficos')?.classList.add('visivel');
    $('#btn-ver-graficos')?.classList.add('ativo');
    $('#btn-ver-tabela')?.classList.remove('ativo');
  });

  $('#btn-voltar')?.addEventListener('click', () => showPage('pagina1'));
  $('#btn-voltar-2')?.addEventListener('click', () => showPage('pagina3'));
  $('#btn-voltar-4')?.addEventListener('click', () => showPage('pagina2'));
  $('#btn-voltar-5')?.addEventListener('click', () => showPage('pagina4'));
  $('#btn-voltar-6')?.addEventListener('click', () => showPage('pagina5'));
  $('#btn-voltar-7')?.addEventListener('click', () => showPage('pagina5'));
  $$('.logo-voltar').forEach((logo) => logo.addEventListener('click', () => showPage('pagina1')));
  $$('.btn-nova').forEach((button) => button.addEventListener('click', () => {
    state.text = '';
    state.features = {};
    state.result = null;
    if ($('#entrada')) $('#entrada').value = '';
    showPage('pagina1');
  }));
}

async function checkBackend() {
  try {
    await request('/health');
  } catch (error) {
    console.warn(`Backend indisponível: ${error.message}`);
  }
}

setupNavigation();
checkBackend();
