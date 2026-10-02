const API_BASE_URL = 'http://localhost:8000';
const state = { text: '', features: {}, result: null, userChoice: null };
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

function showPage(id) {
  $$('.pagina').forEach((page) => page.classList.remove('ativa'));
  $(`#${id}`)?.classList.add('ativa');
}

function clearAnalysis() {
  state.text = '';
  state.features = {};
  state.result = null;
  state.userChoice = null;
  const input = $('#entrada');
  if (input) { input.value = ''; input.focus(); }
  ['#texto-noticia', '#texto-noticia-5'].forEach((selector) => { if ($(selector)) $(selector).textContent = ''; });
  $$('.corpo-tabela').forEach((tbody) => { tbody.innerHTML = ''; });
}

function fillTables(features) {
  $$('.corpo-tabela').forEach((tbody) => {
    tbody.innerHTML = '';
    Object.entries(features).forEach(([name, value]) => {
      if (name === 'types_proporcao' || name === 'num_palavras') return;
      const row = document.createElement('tr');
      const nameCell = document.createElement('td');
      const valueCell = document.createElement('td');
      nameCell.textContent = name;
      valueCell.textContent = typeof value === 'number' ? value.toFixed(6) : String(value);
      row.append(nameCell, valueCell);
      tbody.appendChild(row);
    });
  });
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, { headers: {'Content-Type': 'application/json'}, ...options });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail || `HTTP ${response.status}`);
  return body;
}

async function analyze() {
  const input = $('#entrada');
  const button = $('#btn-enviar');
  const text = input?.value.trim() || '';
  if (text.length < 20) return alert('Digite uma notícia com pelo menos 20 caracteres.');
  state.text = text;
  button.disabled = true;
  button.textContent = 'Analisando...';
  try {
    const data = await request('/features', {method:'POST', body: JSON.stringify({text})});
    state.features = data.features || {};
    fillTables(state.features);
    $('#texto-noticia').textContent = text;
    $('#texto-noticia-5').textContent = text;
    showPage('pagina3');
  } catch (error) {
    alert(`Não foi possível conectar ao backend: ${error.message}`);
  } finally {
    button.disabled = false;
    button.textContent = 'Enviar';
  }
}

async function executeModel() {
  try {
    const data = await request('/predict', {method:'POST', body: JSON.stringify({text: state.text, pipeline: 'svm', features: state.features})});
    state.result = data;
    showPage('pagina2');
  } catch (error) {
    alert(`Não foi possível executar o pipeline: ${error.message}`);
  }
}

function userChoice(choice) {
  const model = state.result?.classification === 'fake' ? 'Falsa' : 'Verdadeira';
  $$('.escolha-usuario').forEach((el) => { el.textContent = choice; });
  $$('.escolha-modelo').forEach((el) => { el.textContent = model; });
  showPage(choice === model ? 'pagina6' : 'pagina7');
}

$('#btn-enviar')?.addEventListener('click', analyze);
$('#entrada')?.addEventListener('keydown', (event) => { if (event.key === 'Enter') analyze(); });
$('#btn-avancar')?.addEventListener('click', executeModel);
$('#btn-verdadeira')?.addEventListener('click', () => userChoice('Verdadeira'));
$('#btn-falsa')?.addEventListener('click', () => userChoice('Falsa'));
$('#btn-voltar')?.addEventListener('click', () => showPage('pagina1'));
$('#btn-voltar-2')?.addEventListener('click', () => showPage('pagina3'));
$('#btn-voltar-4')?.addEventListener('click', () => showPage('pagina2'));
$('#btn-voltar-5')?.addEventListener('click', () => showPage('pagina4'));
$('#btn-voltar-6')?.addEventListener('click', () => showPage('pagina5'));
$('#btn-voltar-7')?.addEventListener('click', () => showPage('pagina5'));
$('#btn-avancar-2')?.addEventListener('click', () => showPage('pagina4'));
$('#btn-avancar-4')?.addEventListener('click', () => showPage('pagina5'));
$$('.logo-voltar').forEach((logo) => logo.addEventListener('click', () => showPage('pagina1')));
$$('.btn-nova').forEach((button) => button.addEventListener('click', () => { clearAnalysis(); showPage('pagina1'); }));
