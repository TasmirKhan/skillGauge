const state = {
  skills: [],
  dashboard: null,
  history: [],
  selectedSkills: new Set(),
  activeView: 'overview',
  assessment: null,
  currentQuestionIndex: 0,
  answers: {},
};

const elements = {
  pageTitle: document.getElementById('pageTitle'),
  overviewScore: document.getElementById('overviewScore'),
  overviewLabel: document.getElementById('overviewLabel'),
  totalAssessments: document.getElementById('totalAssessments'),
  averageScore: document.getElementById('averageScore'),
  strongestSkill: document.getElementById('strongestSkill'),
  needsImprovementText: document.getElementById('needsImprovementText'),
  skillBars: document.getElementById('skillBars'),
  recentAttempts: document.getElementById('recentAttempts'),
  overviewStartButton: document.getElementById('overviewStartButton'),
  startAssessmentButton: document.getElementById('startAssessmentButton'),
  assessmentForm: document.getElementById('assessmentForm'),
  skillSelector: document.getElementById('skillSelector'),
  targetRole: document.getElementById('targetRole'),
  questionCount: document.getElementById('questionCount'),
  assessmentView: document.getElementById('assessmentView'),
  setupView: document.getElementById('setupView'),
  overviewView: document.getElementById('overviewView'),
  resultsView: document.getElementById('resultsView'),
  skillsView: document.getElementById('skillsView'),
  historyView: document.getElementById('historyView'),
  candidateName: document.getElementById('candidateName'),
  answerOptions: document.getElementById('answerOptions'),
  questionText: document.getElementById('questionText'),
  assessmentHeader: document.getElementById('assessmentHeader'),
  progressPill: document.getElementById('progressPill'),
  prevQuestion: document.getElementById('prevQuestion'),
  nextQuestion: document.getElementById('nextQuestion'),
  resultScore: document.getElementById('resultScore'),
  resultLabel: document.getElementById('resultLabel'),
  summaryList: document.getElementById('summaryList'),
  resultSkillList: document.getElementById('resultSkillList'),
  recommendations: document.getElementById('recommendations'),
  answerReview: document.getElementById('answerReview'),
  retakeAssessmentButton: document.getElementById('retakeAssessmentButton'),
  backToDashboardButton: document.getElementById('backToDashboardButton'),
  skillOverview: document.getElementById('skillOverview'),
  historyTableWrap: document.getElementById('historyTableWrap'),
  toast: document.getElementById('toast'),
};

function showToast(message, tone = 'info') {
  elements.toast.textContent = message;
  elements.toast.classList.remove('hidden');
  elements.toast.style.background = tone === 'error' ? '#dc2626' : '#0f172a';
  setTimeout(() => elements.toast.classList.add('hidden'), 2500);
}

async function apiRequest(url, options = {}) {
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  const isJson = response.headers.get('content-type')?.includes('application/json');
  const payload = isJson ? await response.json() : null;

  if (!response.ok) {
    const detail = payload?.detail || payload?.message || 'Request failed';
    throw new Error(detail);
  }

  return payload;
}

async function loadSkills() {
  const data = await apiRequest('/api/v1/skills');
  state.skills = data.skills || [];
  renderSkillSelector();
}

async function loadDashboard() {
  const data = await apiRequest('/api/v1/dashboard/summary');
  state.dashboard = data;
  renderOverview();
}

async function loadHistory() {
  const name = elements.candidateName.value.trim() || 'unknown';
  try {
    const data = await apiRequest(`/api/v1/candidates/${encodeURIComponent(name)}/history`);
    state.history = data.history || [];
  } catch (error) {
    state.history = [];
  }
  renderHistoryTable();
}

function renderSkillSelector() {
  elements.skillSelector.innerHTML = '';
  state.skills.forEach((skill) => {
    const chip = document.createElement('button');
    chip.type = 'button';
    chip.className = `skill-chip ${state.selectedSkills.has(skill.id) ? 'selected' : ''}`;
    chip.textContent = skill.name;
    chip.addEventListener('click', () => {
      if (state.selectedSkills.has(skill.id)) {
        state.selectedSkills.delete(skill.id);
      } else {
        state.selectedSkills.add(skill.id);
      }
      renderSkillSelector();
    });
    elements.skillSelector.appendChild(chip);
  });
}

function renderOverview() {
  const summary = state.dashboard || null;
  const score = summary && summary.average_score ? summary.average_score : 0;

  elements.overviewScore.textContent = summary ? `${Math.round(score)}%` : '--';
  elements.overviewLabel.textContent = summary && summary.total_assessments ? 'Assessment-based indicator' : 'No assessment yet';
  elements.totalAssessments.textContent = summary ? summary.total_assessments : '0';
  elements.averageScore.textContent = `${summary ? Number(summary.average_score || 0).toFixed(1) : 0}%`;
  elements.strongestSkill.textContent = summary && summary.strongest_skill ? summary.strongest_skill : 'N/A';
  elements.needsImprovementText.textContent = summary && summary.needs_improvement ? `Focus: ${summary.needs_improvement}` : 'Needs attention';

  const bars = summary && Array.isArray(summary.skill_summary) ? summary.skill_summary : [];
  elements.skillBars.innerHTML = bars.length
    ? bars.map((item) => `
        <div class="skill-row">
          <span>${escapeHtml(item.skill)}</span>
          <div class="skill-bar">
            <div class="skill-bar-fill" style="width:${Math.min(item.score, 100)}%"></div>
          </div>
          <strong>${Math.round(item.score)}%</strong>
        </div>
      `).join('')
    : '<p>No skill data available yet.</p>';

  const attempts = summary?.recent_history || [];
  elements.recentAttempts.innerHTML = attempts.length
    ? attempts.map((attempt) => `
        <div class="history-item">
          <div>
            <strong>${escapeHtml(attempt.target_role || 'Assessment')}</strong>
            <div>${new Date(attempt.started_at).toLocaleDateString()}</div>
          </div>
          <strong>${Math.round(Number(attempt.readiness_score || 0))}%</strong>
        </div>
      `).join('')
    : '<div class="list-row"><span>No assessments yet.</span><button class="secondary-button" type="button" data-open-setup>Take first test</button></div>';

  const firstButton = elements.recentAttempts.querySelector('[data-open-setup]');
  if (firstButton) {
    firstButton.addEventListener('click', () => openView('setup'));
  }
}

function renderHistoryTable() {
  if (!state.history.length) {
    elements.historyTableWrap.innerHTML = '<p>No assessment history available yet.</p>';
    return;
  }

  const rows = state.history.map((attempt) => `
    <tr>
      <td>${new Date(attempt.started_at).toLocaleDateString()}</td>
      <td>${escapeHtml(attempt.target_role || 'Unknown')}</td>
      <td>${attempt.total_questions || 0}</td>
      <td>${attempt.readiness_score != null ? `${Math.round(attempt.readiness_score)}%` : '—'}</td>
      <td><button class="secondary-button" type="button" data-report-id="${attempt.id}">View Report</button></td>
    </tr>
  `).join('');

  elements.historyTableWrap.innerHTML = `
    <table class="table">
      <thead>
        <tr>
          <th>Date</th>
          <th>Role</th>
          <th>Questions</th>
          <th>Score</th>
          <th>Report</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;

  elements.historyTableWrap.querySelectorAll('[data-report-id]').forEach((button) => {
    button.addEventListener('click', async () => {
      const id = button.getAttribute('data-report-id');
      try {
        const report = await apiRequest(`/api/v1/assessments/${id}/report`);
        renderResultReport(report);
        openView('results');
      } catch (error) {
        showToast(error.message, 'error');
      }
    });
  });
}

function openView(name) {
  state.activeView = name;
  const views = document.querySelectorAll('.view');
  views.forEach((view) => {
    view.classList.toggle('active', view.id === `${name}View`);
    view.classList.toggle('hidden', view.id !== `${name}View`);
  });

  const buttons = document.querySelectorAll('.nav-button');
  buttons.forEach((button) => {
    button.classList.toggle('active', button.dataset.view === name);
  });

  const titleMap = {
    overview: 'Overview',
    setup: 'Take Assessment',
    skills: 'My Skills',
    history: 'Test History',
  };
  elements.pageTitle.textContent = titleMap[name] || 'Overview';
}

document.querySelectorAll('.nav-button').forEach((button) => {
  button.addEventListener('click', () => openView(button.dataset.view));
});

elements.startAssessmentButton.addEventListener('click', () => openView('setup'));
elements.overviewStartButton.addEventListener('click', () => openView('setup'));

elements.assessmentForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const candidateName = document.getElementById('candidateName').value.trim();
  const skills = [...state.selectedSkills];
  if (!candidateName || !skills.length) {
    showToast('Please provide a candidate name and at least one skill.', 'error');
    return;
  }

  const difficulties = [...document.querySelectorAll('.chip input:checked')].map((box) => box.value);
  try {
    const payload = await apiRequest('/api/v1/assessments', {
      method: 'POST',
      body: JSON.stringify({
        candidate_name: candidateName,
        target_role: elements.targetRole.value,
        skills,
        question_count: Number(elements.questionCount.value),
        difficulties,
      }),
    });

    state.assessment = {
      id: payload.id,
      status: payload.status,
      total_questions: payload.total_questions,
      candidate_name: payload.candidate_name,
      target_role: payload.target_role,
    };
    state.currentQuestionIndex = 0;
    state.answers = {};

    const detail = await apiRequest(`/api/v1/assessments/${payload.id}`);
    state.assessment.questions = detail.questions || [];
    sessionStorage.setItem('skillgauge-active-assessment', JSON.stringify(state.assessment));
    renderAssessment();
    openView('assessment');
  } catch (error) {
    showToast(error.message, 'error');
  }
});

function renderAssessment() {
  if (!state.assessment || !state.assessment.questions?.length) return;
  const question = state.assessment.questions[state.currentQuestionIndex];
  elements.assessmentHeader.textContent = `Question ${state.currentQuestionIndex + 1} of ${state.assessment.questions.length}`;
  elements.progressPill.textContent = `${state.currentQuestionIndex + 1} / ${state.assessment.questions.length}`;
  elements.questionText.textContent = question.question_text;
  elements.answerOptions.innerHTML = '';

  question.options.forEach((option) => {
    const optionLabel = option.split('. ')[0];
    const optionText = option.split('. ').slice(1).join('. ');
    const button = document.createElement('button');
    button.type = 'button';
    button.className = `answer-option ${state.answers[question.id] === optionLabel ? 'selected' : ''}`;
    button.innerHTML = `<span>${optionLabel}</span><span>${escapeHtml(optionText)}</span>`;
    button.addEventListener('click', () => {
      state.answers[question.id] = optionLabel;
      renderAssessment();
    });
    elements.answerOptions.appendChild(button);
  });

  elements.prevQuestion.disabled = state.currentQuestionIndex === 0;
  elements.nextQuestion.textContent = state.currentQuestionIndex === state.assessment.questions.length - 1 ? 'Submit' : 'Next';
}

elements.prevQuestion.addEventListener('click', () => {
  if (state.currentQuestionIndex > 0) {
    state.currentQuestionIndex -= 1;
    renderAssessment();
  }
});

elements.nextQuestion.addEventListener('click', async () => {
  if (state.currentQuestionIndex < state.assessment.questions.length - 1) {
    state.currentQuestionIndex += 1;
    renderAssessment();
    return;
  }

  const answers = Object.entries(state.answers).map(([questionId, selected]) => ({
    question_id: Number(questionId),
    selected_option: selected,
  }));

  try {
    const payload = await apiRequest(`/api/v1/assessments/${state.assessment.id}/submit`, {
      method: 'POST',
      body: JSON.stringify({ answers }),
    });

    renderResultReport(payload);
    openView('results');
    sessionStorage.removeItem('skillgauge-active-assessment');
  } catch (error) {
    showToast(error.message, 'error');
  }
});

function renderResultReport(report) {
  if (!report) return;

  elements.resultScore.textContent = `${Math.round(Number(report.overall_score || 0))}%`;
  elements.resultLabel.textContent =
    Number(report.overall_score || 0) >= 80
      ? 'Strong performance'
      : Number(report.overall_score || 0) >= 60
        ? 'Developing well'
        : Number(report.overall_score || 0) >= 40
          ? 'Needs improvement'
          : 'Developing';

  elements.summaryList.innerHTML = `
    <li><strong>Correct</strong>: ${report.correct_answers ?? 0}</li>
    <li><strong>Incorrect</strong>: ${report.incorrect_answers ?? 0}</li>
    <li><strong>Unanswered</strong>: ${report.unanswered ?? 0}</li>
    <li><strong>Readiness</strong>: ${Math.round(Number(report.readiness_score || 0))}%</li>
  `;

  const skills = report.skill_scores || [];
  elements.resultSkillList.innerHTML = skills.length
    ? skills.map((skill) => `
        <div class="skill-row">
          <span>${escapeHtml(skill.skill)}</span>
          <div class="skill-bar">
            <div class="skill-bar-fill" style="width:${Math.min(Number(skill.score || 0), 100)}%"></div>
          </div>
          <strong>${Math.round(Number(skill.score || 0))}%</strong>
        </div>
      `).join('')
    : '<p>No skill breakdown available.</p>';

  const recommendations = report.recommendations || [];
  elements.recommendations.innerHTML = recommendations.length
    ? recommendations.map((item) => `
        <div class="list-row">
          <div>
            <strong>${escapeHtml(item.skill)}</strong>
            <div>${escapeHtml(item.focus)}</div>
          </div>
        </div>
      `).join('')
    : '<p>No recommendations yet.</p>';

  const reviewItems = report.question_results || [];
  elements.answerReview.innerHTML = reviewItems.length
    ? reviewItems.map((question) => `
        <div class="review-item ${question.is_correct ? 'correct' : 'incorrect'}">
          <strong>${escapeHtml(question.skill)}:</strong>
          <p>${escapeHtml(question.question_text)}</p>
          <div>Your answer: ${escapeHtml(question.selected_option || 'Unanswered')}</div>
          <div>Correct answer: ${escapeHtml(question.correct_option)}</div>
          <div>${escapeHtml(question.explanation)}</div>
        </div>
      `).join('')
    : '<p>No answer review available.</p>';

  loadHistory();
}

elements.retakeAssessmentButton.addEventListener('click', () => openView('setup'));
elements.backToDashboardButton.addEventListener('click', async () => {
  await loadDashboard();
  openView('overview');
});

function restoreAssessment() {
  const saved = sessionStorage.getItem('skillgauge-active-assessment');
  if (!saved) return;
  try {
    const payload = JSON.parse(saved);
    state.assessment = payload;
    state.currentQuestionIndex = 0;
    state.answers = {};
    renderAssessment();
    openView('assessment');
  } catch (error) {
    sessionStorage.removeItem('skillgauge-active-assessment');
  }
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

async function bootstrap() {
  await loadSkills();
  await loadDashboard();
  await loadHistory();
  renderOverview();
  restoreAssessment();
}

bootstrap();
