const API_BASE = "http://localhost:8000/api/v1";

let accessToken = localStorage.getItem("access_token") || "";
let currentDocumentId = "";

const apiOutput = document.getElementById("api-output");
const documentOutput = document.getElementById("document-output");
const authStatus = document.getElementById("auth-status");
const aiOutput = document.getElementById("ai-output");

let currentAiJobId = "";
let currentAiSuggestion = "";
let currentAiJobResolved = false;
let currentAiPollToken = 0;

function setApiOutput(data) {
  apiOutput.textContent = JSON.stringify(data, null, 2);
}

function setDocumentOutput(data) {
  documentOutput.textContent = JSON.stringify(data, null, 2);
}

function setAiOutput(data) {
  aiOutput.textContent = JSON.stringify(data, null, 2);
}

function getHeaders(auth = false) {
  const headers = {
    "Content-Type": "application/json"
  };
  if (auth && accessToken) {
    headers["Authorization"] = `Bearer ${accessToken}`;
  }
  return headers;
}

function setAiButtonsEnabled(enabled) {
  document.getElementById("ai-accept-btn").disabled = !enabled;
  document.getElementById("ai-reject-btn").disabled = !enabled;
}

function resetAiState() {
  currentAiJobId = "";
  currentAiSuggestion = "";
  currentAiJobResolved = false;
  currentAiPollToken += 1;
  setAiButtonsEnabled(false);
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function callApi(path, method = "GET", body = null, auth = false) {
  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers: getHeaders(auth),
    body: body ? JSON.stringify(body) : null
  });

  const data = await response.json();
  setApiOutput(data);

  if (!response.ok) {
    throw new Error(data?.error?.detail || "Request failed");
  }

  return data;
}

async function pollAiJob(jobId, pollToken) {
  while (true) {
    if (pollToken !== currentAiPollToken) {
      return;
    }

    try {
      const data = await callApi(`/ai/jobs/${jobId}`, "GET", null, true);

      if (pollToken !== currentAiPollToken) {
        return;
      }

      setAiOutput(data);

      if (data.status === "completed") {
        currentAiSuggestion = data.suggestion;
        currentAiJobResolved = false;
        setAiButtonsEnabled(true);
        return;
      }

      if (data.status === "failed") {
        setAiButtonsEnabled(false);
        return;
      }
    } catch (err) {
      if (pollToken !== currentAiPollToken) {
        return;
      }
      setAiButtonsEnabled(false);
      authStatus.textContent = err.message;
      return;
    }

    await sleep(2000);
  }
}

document.getElementById("register-btn").addEventListener("click", async () => {
  try {
    const data = await callApi("/auth/register", "POST", {
      name: document.getElementById("register-name").value,
      email: document.getElementById("register-email").value,
      password: document.getElementById("register-password").value
    });
    authStatus.textContent = `Registered: ${data.email}`;
  } catch (err) {
    authStatus.textContent = err.message;
  }
});

document.getElementById("login-btn").addEventListener("click", async () => {
  try {
    const data = await callApi("/auth/login", "POST", {
      email: document.getElementById("login-email").value,
      password: document.getElementById("login-password").value
    });
    accessToken = data.access_token;
    localStorage.setItem("access_token", accessToken);
    authStatus.textContent = `Logged in as user ${data.user_id}`;
  } catch (err) {
    authStatus.textContent = err.message;
  }
});

document.getElementById("create-doc-btn").addEventListener("click", async () => {
  try {
    const data = await callApi("/documents", "POST", {
      title: document.getElementById("doc-title").value
    }, true);

    currentDocumentId = data.document_id;
    document.getElementById("loaded-doc-id").value = currentDocumentId;
    document.getElementById("editor-title").value = data.title;
    document.getElementById("editor-content").value = "";
    setDocumentOutput(data);
  } catch (err) {
    authStatus.textContent = err.message;
  }
});

document.getElementById("list-docs-btn").addEventListener("click", async () => {
  try {
    const data = await callApi("/documents", "GET", null, true);
    const list = document.getElementById("documents-list");
    list.innerHTML = "";

    data.documents.forEach((doc) => {
      const li = document.createElement("li");
      li.textContent = `${doc.title} (${doc.role}) - ${doc.document_id}`;
      li.addEventListener("click", () => {
        document.getElementById("loaded-doc-id").value = doc.document_id;
      });
      list.appendChild(li);
    });
  } catch (err) {
    authStatus.textContent = err.message;
  }
});

document.getElementById("load-doc-btn").addEventListener("click", async () => {
  try {
    const documentId = document.getElementById("loaded-doc-id").value;
    const data = await callApi(`/documents/${documentId}`, "GET", null, true);
    currentDocumentId = data.document_id;
    document.getElementById("editor-title").value = data.title;
    document.getElementById("editor-content").value = data.content;
    setDocumentOutput(data);
  } catch (err) {
    authStatus.textContent = err.message;
  }
});

document.getElementById("save-doc-btn").addEventListener("click", async () => {
  try {
    const documentId = document.getElementById("loaded-doc-id").value || currentDocumentId;
    const data = await callApi(`/documents/${documentId}`, "PATCH", {
      title: document.getElementById("editor-title").value,
      content: document.getElementById("editor-content").value
    }, true);
    setDocumentOutput(data);
  } catch (err) {
    authStatus.textContent = err.message;
  }
});

document.getElementById("ai-invoke-btn").addEventListener("click", async () => {
  try {
    const documentId = document.getElementById("loaded-doc-id").value || currentDocumentId;
    const action = document.getElementById("ai-action").value;
    const targetLanguage = document.getElementById("ai-target-language").value || null;

    resetAiState();
    setAiOutput({ status: "pending" });

    const data = await callApi(`/documents/${documentId}/ai/invoke`, "POST", {
      selected_text: document.getElementById("ai-selected-text").value,
      action,
      options: {
        tone: "formal",
        target_language: targetLanguage
      }
    }, true);

    currentAiJobId = data.job_id;
    const pollToken = currentAiPollToken;
    setAiOutput(data);
    pollAiJob(currentAiJobId, pollToken);
  } catch (err) {
    authStatus.textContent = err.message;
  }
});

document.getElementById("ai-accept-btn").addEventListener("click", async () => {
  try {
    if (!currentAiJobId) {
      throw new Error("No AI job to accept");
    }
    if (currentAiJobResolved) {
      throw new Error("This AI result has already been handled");
    }

    currentAiJobResolved = true;
    setAiButtonsEnabled(false);

    const data = await callApi(`/ai/jobs/${currentAiJobId}/accept`, "POST", {
      accepted: true,
      partial_text: null
    }, true);

    setAiOutput(data);

    if (currentAiSuggestion) {
      document.getElementById("editor-content").value = currentAiSuggestion;
    }
  } catch (err) {
    authStatus.textContent = err.message;
  }
});

document.getElementById("ai-reject-btn").addEventListener("click", async () => {
  try {
    if (!currentAiJobId) {
      throw new Error("No AI job to reject");
    }
    if (currentAiJobResolved) {
      throw new Error("This AI result has already been handled");
    }

    currentAiJobResolved = true;
    setAiButtonsEnabled(false);

    const data = await callApi(`/ai/jobs/${currentAiJobId}/accept`, "POST", {
      accepted: false,
      partial_text: null
    }, true);

    setAiOutput(data);
  } catch (err) {
    authStatus.textContent = err.message;
  }
});

setAiButtonsEnabled(false);