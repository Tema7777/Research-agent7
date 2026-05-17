const topicInput = document.getElementById('topic');
const startBtn = document.getElementById('startBtn');
const statusEl = document.getElementById('status');
const reportEl = document.getElementById('report');
const linksWrap = document.getElementById('downloadLinks');
const mdLink = document.getElementById('mdLink');
const pdfLink = document.getElementById('pdfLink');

startBtn.addEventListener('click', async () => {
  const topic = topicInput.value.trim();
  if (!topic) {
    statusEl.textContent = 'Please enter a research topic.';
    return;
  }

  startBtn.disabled = true;
  statusEl.textContent = 'Generating report...';
  reportEl.textContent = '';
  linksWrap.classList.add('hidden');

  try {
    const response = await fetch('/api/research', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic })
    });

    if (!response.ok) {
      throw new Error('Research request failed.');
    }

    const data = await response.json();
    reportEl.textContent = data.markdown_report;
    statusEl.textContent = `Done. Saved to ${data.markdown_path} and ${data.pdf_path}.`;

    const mdName = data.markdown_path.split('/').pop();
    const pdfName = data.pdf_path.split('/').pop();

    mdLink.href = `/api/reports/${mdName}`;
    mdLink.textContent = 'Download Markdown';

    pdfLink.href = `/api/reports/${pdfName}`;
    pdfLink.textContent = 'Download PDF';

    linksWrap.classList.remove('hidden');
  } catch (error) {
    statusEl.textContent = error.message;
  } finally {
    startBtn.disabled = false;
  }
});
