const cvInput = document.getElementById('cvInput');
const charCount = document.getElementById('charCount');
const loading = document.getElementById('loading');
const submitButton = document.getElementById('submitButton');
const sampleButton = document.getElementById('sampleButton');
const clearButton = document.getElementById('clearButton');
const cvFileInput = document.getElementById('cvFileInput');
const uploadStatus = document.getElementById('uploadStatus');
const emptyState = document.getElementById('emptyState');
const resultContent = document.getElementById('resultContent');

const scoreValue = document.getElementById('scoreValue');
const statusValue = document.getElementById('statusValue');
const totalSections = document.getElementById('totalSections');
const passedSections = document.getElementById('passedSections');
const failedSections = document.getElementById('failedSections');
const detectedSections = document.getElementById('detectedSections');
const emailStatus = document.getElementById('emailStatus');
const phoneStatus = document.getElementById('phoneStatus');
const detectedList = document.getElementById('detectedList');
const missingList = document.getElementById('missingList');
const suggestionsList = document.getElementById('suggestionsList');
const atsScore = document.getElementById('atsScore');
const atsSummary = document.getElementById('atsSummary');
const atsLimitation = document.getElementById('atsLimitation');
const atsChecks = document.getElementById('atsChecks');
const atsRecommendations = document.getElementById('atsRecommendations');

function updateCharCount() {
  const length = cvInput.value.length;
  charCount.textContent = `${length} / 20000`;
}

function setLoading(isLoading, message = 'Checking your CV / Resume...') {
  loading.classList.toggle('hidden', !isLoading);
  loading.textContent = message;
  submitButton.disabled = isLoading;
  submitButton.textContent = isLoading ? 'Checking...' : 'Check My CV / Resume';
  cvFileInput.disabled = isLoading;
  sampleButton.disabled = isLoading;
  clearButton.disabled = isLoading;
}

function hideResults() {
  emptyState.classList.remove('hidden');
  resultContent.classList.add('hidden');
}

function renderStatus(element, valid, label) {
  if (valid) {
    element.textContent = `${label}: Valid`;
    element.className = 'pill success';
    return;
  }

  element.textContent = `${label}: Missing or Invalid`;
  element.className = 'pill failure';
}

function renderList(listElement, items, emptyText) {
  listElement.innerHTML = '';

  if (!items.length) {
    const item = document.createElement('li');
    item.textContent = emptyText;
    listElement.appendChild(item);
    return;
  }

  items.forEach((itemText) => {
    const item = document.createElement('li');
    item.textContent = itemText;
    listElement.appendChild(item);
  });
}

function renderAtsAnalysis(analysis) {
  atsScore.textContent = analysis.score;
  atsSummary.textContent =
    `${analysis.passed_checks} of ${analysis.total_checks} text checks passed`;
  atsLimitation.textContent = analysis.limitation;

  atsChecks.innerHTML = '';
  analysis.checks.forEach((check) => {
    const item = document.createElement('li');
    item.textContent = `${check.passed ? 'Pass' : 'Review'}: ${check.name}`;
    item.className = check.passed ? 'ats-check-passed' : 'ats-check-failed';
    atsChecks.appendChild(item);
  });

  renderList(
    atsRecommendations,
    analysis.recommendations,
    'No ATS tips available.',
  );
}

async function parseApiResponse(response) {
  const text = await response.text();
  let payload = null;

  try {
    payload = JSON.parse(text);
  } catch {
    payload = null;
  }

  if (!response.ok) {
    const message =
      (payload && (payload.detail || payload.message)) ||
      text.trim().slice(0, 200) ||
      `Request failed with status ${response.status}.`;
    throw new Error(message);
  }

  if (!payload) {
    throw new Error(
      `Unexpected non-JSON response from the server (status ${response.status}).`,
    );
  }

  return payload;
}

function showResults(result) {
  emptyState.classList.add('hidden');
  resultContent.classList.remove('hidden');

  scoreValue.textContent = result.score;
  statusValue.textContent = result.status;

  totalSections.textContent = result.total_sections;
  passedSections.textContent = result.passed_sections;
  failedSections.textContent = result.failed_sections;
  detectedSections.textContent = result.passed_sections;

  renderStatus(emailStatus, result.email_valid, 'Email');
  renderStatus(phoneStatus, result.phone_valid, 'Phone');

  const detected = result.checks
    .filter((check) => check.present)
    .map((check) => check.section);

  const missing = result.missing_fields;

  renderList(detectedList, detected, 'No required sections detected.');
  renderList(missingList, missing, 'No missing sections.');
  renderList(suggestionsList, result.suggestions, 'No suggestions available.');
  renderAtsAnalysis(result.ats_analysis);
}

async function validateCv() {
  const text = cvInput.value.trim();

  if (!text) {
    alert('Please enter some CV text before checking.');
    cvInput.focus();
    return;
  }

  setLoading(true);

  try {
    const response = await fetch('/api/validate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cv_text: text }),
    });

    const result = await parseApiResponse(response);

    showResults(result);
  } catch (error) {
    alert(error.message || 'Unable to validate CV right now.');
  } finally {
    setLoading(false);
  }
}

async function loadTextFile(filename) {
  const response = await fetch(filename);
  if (!response.ok) {
    throw new Error(`Could not load ${filename}`);
  }
  const text = await response.text();
  cvInput.value = text;
  updateCharCount();
}

async function uploadCvFile(file) {
  const allowedExtensions = ['.txt', '.pdf', '.docx'];
  const extension = file.name.slice(file.name.lastIndexOf('.')).toLowerCase();

  if (!allowedExtensions.includes(extension)) {
    throw new Error('Please choose a TXT, PDF, or DOCX file.');
  }
  if (file.size > 5 * 1024 * 1024) {
    throw new Error('The selected file must be 5 MB or smaller.');
  }

  setLoading(true, 'Extracting text from your file...');
  uploadStatus.textContent = '';

  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('/api/extract', {
      method: 'POST',
      body: formData,
    });
    const result = await parseApiResponse(response);

    cvInput.value = result.cv_text;
    updateCharCount();
    hideResults();
    uploadStatus.textContent =
      `${result.file_name} loaded. Review the text, then click “Check My CV / Resume.”`;
  } finally {
    setLoading(false);
  }
}

cvInput.addEventListener('input', updateCharCount);
submitButton.addEventListener('click', validateCv);

cvFileInput.addEventListener('change', async () => {
  const file = cvFileInput.files[0];
  if (!file) {
    return;
  }

  try {
    await uploadCvFile(file);
  } catch (error) {
    uploadStatus.textContent = error.message || 'Unable to read the selected file.';
  } finally {
    cvFileInput.value = '';
  }
});

sampleButton.addEventListener('click', async () => {
  try {
    await loadTextFile('/sample_cv.txt');
    hideResults();
    uploadStatus.textContent = '';
  } catch (error) {
    alert(error.message);
  }
});

clearButton.addEventListener('click', () => {
  cvInput.value = '';
  updateCharCount();
  cvFileInput.value = '';
  uploadStatus.textContent = '';
  hideResults();
});

updateCharCount();
