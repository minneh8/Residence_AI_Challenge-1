const API_BASE_URL = 'http://localhost:8000';

const elements = {
  form: document.querySelector('#news-form') || document.querySelector('form'),
  text: document.querySelector('#news-text') || document.querySelector('textarea'),
  pipeline: document.querySelector('#pipeline-select'),
  submit: document.querySelector('#analyze-button') || document.querySelector('button[type="submit"]'),
  status: document.querySelector('#status'),
  result: document.querySelector('#result'),
  classification: document.querySelector('#classification'),
  fakeProbability: document.querySelector('#fake-probability'),
  trueProbability: document.querySelector('#true-probability'),
  confidence: document.querySelector('#confidence'),
  explanation: document.querySelector('#explanation'),
  modelStatus: document.querySelector('#model-status')
};

const pipelineLabels = {
  svm: 'SVM',
  kmeans: 'K-Means',
  dbscan: 'DBSCAN',
  isolation_forest: 'Isolation Forest'
};

function setStatus(message, type = '') {
  if (!elements.status) return;
  elements.status.textContent = message;
  elements.status.dataset.type = type;
}

function setLoading(loading) {
  if (!elements.submit) return;
  elements.submit.disabled = loading;
  elements.submit.textContent = loading ? 'Analisando...' : 'Analisar notícia';
}

function selectedPipeline() {
  return elements.pipeline?.value || 'svm';
}

function formatPercent(value) {
  return typeof value === 'number' ? `${(value * 100).toFixed(2)}%` : 'Indisponível';
}

function renderClassification(data) {
  if (elements.classification) {
    if (data.pipeline === 'kmeans') {
      elements.classification.textContent = `Cluster ${data.label}`;
    } else {
      elements.classification.textContent = data.classification === 'fake'
        ? 'Possível notícia falsa'
        : 'Possível notícia verdadeira';
    }
  }
  if (elements.fakeProbability) elements.fakeProbability.textContent = formatPercent(data.fake_probability);
  if (elements.trueProbability) elements.trueProbability.textContent = formatPercent(data.true_probability);
  if (elements.confidence) elements.confidence.textContent = formatPercent(data.confidence);
  if (elements.explanation) {
    elements.explanation.innerHTML = (data.explanation || [])
      .map(item => `<li>${item}</li>`)
      .join('');
  }
  if (elements.result) elements.result.classList.remove('hidden');
}

function renderAnomaly(data) {
  if (elements.classification) {
    elements.classification.textContent = data.anomaly
      ? 'Anomalia detectada'
      : 'Nenhuma anomalia detectada';
  }
  if (elements.confidence) {
    elements.confidence.textContent = data.score === null || data.score === undefined
      ? 'Indisponível'
      : data.score.toFixed(6);
  }
  if (elements.fakeProbability) elements.fakeProbability.textContent = 'N/A';
  if (elements.trueProbability) elements.trueProbability.textContent = data.cluster ?? 'N/A';
  if (elements.explanation) {
    elements.explanation.innerHTML = `<li>Pipeline: ${pipelineLabels[data.pipeline] || data.pipeline}</li>`;
  }
  if (elements.result) elements.result.classList.remove('hidden');
}

async function requestJson(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail || `Erro HTTP ${response.status}`);
  return body;
}

async function loadPipelineStatus() {
  try {
    const data = await requestJson('/pipelines');
    if (elements.modelStatus) {
      const loaded = Object.entries(data.status || {})
        .filter(([, value]) => value)
        .map(([name]) => pipelineLabels[name] || name);
      elements.modelStatus.textContent = loaded.length
        ? `Carregados: ${loaded.join(', ')}`
        : 'Nenhum pipeline treinado carregado; modo de desenvolvimento.';
    }
  } catch (error) {
    if (elements.modelStatus) elements.modelStatus.textContent = `API indisponível: ${error.message}`;
  }
}

async function handleSubmit(event) {
  event.preventDefault();
  const text = elements.text?.value.trim() || '';
  const pipeline = selectedPipeline();

  if (text.length < 20) {
    setStatus('Digite uma notícia com pelo menos 20 caracteres.', 'error');
    return;
  }

  setLoading(true);
  setStatus('Processando notícia...', 'loading');
  try {
    const anomalyPipeline = pipeline === 'dbscan' || pipeline === 'isolation_forest';
    const data = await requestJson(anomalyPipeline ? '/anomaly' : '/predict', {
      method: 'POST',
      body: JSON.stringify({ text, pipeline })
    });
    anomalyPipeline ? renderAnomaly(data) : renderClassification(data);
    setStatus(data.model_loaded ? 'Análise concluída com pipeline treinado.' : 'Análise concluída no modo de desenvolvimento.', data.model_loaded ? 'success' : 'warning');
  } catch (error) {
    setStatus(`Não foi possível analisar a notícia: ${error.message}`, 'error');
  } finally {
    setLoading(false);
  }
}

if (elements.form) elements.form.addEventListener('submit', handleSubmit);
if (elements.pipeline) elements.pipeline.addEventListener('change', loadPipelineStatus);
loadPipelineStatus();
