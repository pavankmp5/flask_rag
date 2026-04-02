const state = {
  stats: null,
  config: null,
};

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || `Request failed with status ${response.status}`);
  }
  return payload;
}

function setText(id, value) {
  const node = document.getElementById(id);
  if (node) {
    node.textContent = value;
  }
}

function renderJson(id, value) {
  const node = document.getElementById(id);
  if (node) {
    node.textContent = JSON.stringify(value, null, 2);
  }
}

function renderStats(stats) {
  state.stats = stats;
  setText("knowledge-rows", String(stats.knowledge_rows ?? "--"));
  setText("indexed-chunks", String(stats.indexed_chunks ?? "--"));
  setText("runtime-mode", stats.mode || "llm_only");
  renderJson("stats-json", stats);
}

function renderConfig(config) {
  state.config = config;
  const baseUrl = config.openai_base_url || "OpenAI default";
  setText("provider-base-url", baseUrl.replace("https://", ""));
  renderJson("config-json", config);
}

function renderCitations(citations) {
  const list = document.getElementById("chat-citations");
  list.innerHTML = "";

  if (!citations || citations.length === 0) {
    const item = document.createElement("li");
    item.textContent = "No citations for this response.";
    list.appendChild(item);
    return;
  }

  for (const citation of citations) {
    const item = document.createElement("li");
    item.textContent = `${citation.title} | ${citation.source} | ${citation.category}`;
    list.appendChild(item);
  }
}

function renderSearchResults(payload) {
  setText("search-mode", payload.mode || "none");
  const container = document.getElementById("search-results");
  container.innerHTML = "";

  if (!payload.results || payload.results.length === 0) {
    container.innerHTML = '<p class="empty-state">No answer returned.</p>';
    return;
  }

  for (const result of payload.results) {
    const article = document.createElement("article");
    article.className = "search-item";
    article.innerHTML = `
      <h3>${result.title || "Untitled"}</h3>
      <p><strong>Source:</strong> ${result.source} | <strong>Category:</strong> ${result.category}</p>
      <p>${result.text}</p>
    `;
    container.appendChild(article);
  }
}

async function loadDiagnostics() {
  const [stats, config] = await Promise.all([
    fetchJson("/stats"),
    fetchJson("/config-check"),
  ]);
  renderStats(stats);
  renderConfig(config);
}

async function handleChatSubmit(event) {
  event.preventDefault();
  const message = document.getElementById("chat-message").value.trim();
  if (!message) {
    setText("chat-reply", "Please enter a message first.");
    return;
  }

  setText("chat-reply", "Thinking...");
  setText("chat-mode", "running");
  renderCitations([]);

  try {
    const payload = await fetchJson("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    setText("chat-reply", payload.reply || "No reply returned.");
    setText("chat-mode", payload.response_mode || "unknown");
    renderCitations(payload.citations || []);
  } catch (error) {
    setText("chat-reply", error.message);
    setText("chat-mode", "error");
  }
}

async function handleSearchSubmit(event) {
  event.preventDefault();
  const query = document.getElementById("search-query").value.trim();

  if (!query) {
    renderSearchResults({ mode: "none", results: [] });
    return;
  }

  setText("search-mode", "running");
  try {
    const payload = await fetchJson(`/search?q=${encodeURIComponent(query)}`);
    renderSearchResults(payload);
  } catch (error) {
    const container = document.getElementById("search-results");
    container.innerHTML = `<p class="empty-state">${error.message}</p>`;
    setText("search-mode", "error");
  }
}

function wireSamples() {
  document.getElementById("chat-sample").addEventListener("click", () => {
    document.getElementById("chat-message").value = "Which country is Dubai in?";
  });

  document.getElementById("search-sample").addEventListener("click", () => {
    document.getElementById("search-query").value = "Dubai";
  });

  for (const button of document.querySelectorAll("[data-fill-chat]")) {
    button.addEventListener("click", () => {
      document.getElementById("chat-message").value = button.dataset.fillChat;
    });
  }

  for (const button of document.querySelectorAll("[data-fill-search]")) {
    button.addEventListener("click", () => {
      document.getElementById("search-query").value = button.dataset.fillSearch;
    });
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  document.getElementById("chat-form").addEventListener("submit", handleChatSubmit);
  document.getElementById("search-form").addEventListener("submit", handleSearchSubmit);
  wireSamples();

  try {
    await loadDiagnostics();
  } catch (error) {
    renderJson("stats-json", { error: error.message });
    renderJson("config-json", { error: error.message });
  }
});
