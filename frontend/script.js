const API_BASE_URL = 'http://localhost:8000';

const form = document.querySelector('form');
const textarea = document.querySelector('textarea');
const submitButton = document.querySelector('button[type="submit"]') || document.querySelector('button');
const statusElement = document.querySelector('#status');
const resultElement = document.querySelector('#result');
const classificationElement = document.querySelector('#classification');
const fakeProbabilityElement = document.querySelector('#fake-probability');
const trueProbabilityElement = document.querySelector('#true-probability');
const confidenceElement = document.querySelector('#confidence');
const explanationElement = document.querySelector('#explanation');

const pipelineNames = {
  svm: 'SVM',
  kmeans: 'K-Means',
  dbscan: 'DBSCAN',
  isolation_forest: 'Isolation Forest'
};

function getPipeline() {
  const selected = document.querySelector('[name="pipeline"]:checked')
    || document.querySelector('select[name="pipeline"]')
    || document.querySelector('#pipeline');
  return selected?.value || 'svm';
}

function setStatus(message) {
  if (statusElement) statusElement.textContent = message;
}

function formatPercentage(value) {
  return typeof value === 'number'
    ? `${(value * 100).toFixed(2)}%`
    : 'Indisponível';
}

function showResult(data) {
  if (classificationElement) {
    if (data.pipeline === 'kmeans') {
      classificationElement.textContent = `Cluster ${data.label}`;
    } else {
      classificationElement.textContent = data.classification === 'fake'
        ? 'Possível notícia falsa'
        : 'Possível notícia verdadeira';
    }
  }

  if (fakeProbabilityElement) {
    fakeProbabilityElement.textContent = formatPercentage(data.fake_probability);
  }

  if (trueProbabilityElement) {
    trueProbabilityElement.textContent = formatPercentage(data.true_probability);
  }

  if (confidenceElement) {
    confidenceElement.textContent = formatPercentage(data.confidence);
  }

  if (explanationElement) {
    explanationElement.textContent = (data.explanation || []).join(' ');
  }

  if (resultElement) {
    resultElement.classList.remove('hidden');
  }
}

function showAnomaly(data) {
  if (classificationElement) {
    classificationElement.textContent = data.anomaly
      ? 'Anomalia detectada'
      : 'Nenhuma anomalia detectada';
  }

  if (fakeProbabilityElement) {
    fakeProbabilityElement.textContent = 'N/A';
  }

  if (trueProbabilityElement) {
    trueProbabilityElement.textContent = data.cluster ?? 'N/A';
  }

  if (confidenceElement) {
    confidenceElement.textContent = typeof data.score === 'number'
      ? data.score.toFixed(6)
      : 'Indisponível';
  }

  if (explanationElement) {
    explanationElement.textContent = `Pipeline: ${pipelineNames[data.pipeline] || data.pipeline}`;
  }

  if (resultElement) {
    resultElement.classList.remove('hidden');
  }
}

async function requestApi(path, payload) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || `Erro HTTP ${response.status}`);
  }
  return data;
}

async function checkBackend() {
  try {
    const response = await fetch(`${API_BASE_URL}/pipelines`);
    if (!response.ok) throw new Error(`Erro HTTP ${response.status}`);
    const data = await response.json();
    setStatus(data.available?.length
      ? `Pipelines carregados: ${data.available.map(name => pipelineNames[name] || name).join(', ')}`
      : 'Backend conectado. Pipelines ainda não carregados.');
  } catch (error) {
    setStatus(`Backend indisponível: ${error.message}`);
  }
}

async function handleSubmit(event) {
  event.preventDefault();

  const text = textarea?.value.trim() || '';
  const pipeline = getPipeline();

  if (text.length < 20) {
    setStatus('Digite pelo menos 20 caracteres.');
    return;
  }

  if (submitButton) {
    submitButton.disabled = true;
    submitButton.dataset.originalText = submitButton.textContent;
    submitButton.textContent = 'Analisando...';
  }

  setStatus(`Analisando com ${pipelineNames[pipeline] || pipeline}...`);

  try {
    const anomalyPipeline = pipeline === 'dbscan' || pipeline === 'isolation_forest';
    const data = await requestApi(
      anomalyPipeline ? '/anomaly' : '/predict',
      { text, pipeline }
    );

    anomalyPipeline ? showAnomaly(data) : showResult(data);

    setStatus(data.model_loaded
      ? 'Análise concluída.'
      : 'Backend conectado, mas o pipeline ainda não foi carregado.');
  } catch (error) {
    setStatus(`Não foi possível analisar: ${error.message}`);
  } finally {
    if (submitButton) {
      submitButton.disabled = false;
      submitButton.textContent = submitButton.dataset.originalText || 'Analisar';
    }
  }
}

if (form && textarea) {
  form.addEventListener('submit', handleSubmit);
}

checkBackend();
