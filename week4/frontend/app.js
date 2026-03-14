// ── Utility ──────────────────────────────────────────────────────────────────

async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) {
    const msg = await res.text().catch(() => res.statusText);
    throw new Error(msg);
  }
  if (res.status === 204) return null;
  return res.json();
}

function showError(msg) {
  const banner = document.getElementById("error-banner");
  if (!banner) {
    alert(msg);
    return;
  }
  banner.textContent = msg;
  banner.style.display = "block";
  setTimeout(() => {
    banner.style.display = "none";
  }, 4000);
}

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

// ── State ─────────────────────────────────────────────────────────────────────

let editingNoteId = null;

// ── Notes ─────────────────────────────────────────────────────────────────────

function currentSearchQuery() {
  return (document.getElementById("search-input")?.value ?? "").trim();
}

async function loadNotes(query = "") {
  const list = document.getElementById("notes");
  list.innerHTML = "";

  try {
    const url = query
      ? `/notes/search/?q=${encodeURIComponent(query)}`
      : "/notes/";
    const notes = await fetchJSON(url);

    if (notes.length === 0) {
      const li = document.createElement("li");
      li.className = "empty-state";
      li.textContent = query ? "No notes match your search." : "No notes yet.";
      list.appendChild(li);
      return;
    }

    for (const n of notes) {
      list.appendChild(buildNoteItem(n));
    }
  } catch (err) {
    showError("Failed to load notes: " + err.message);
  }
}

function buildNoteItem(n) {
  const li = document.createElement("li");
  li.dataset.id = n.id;
  li.className = "note-item";

  const textSpan = document.createElement("span");
  textSpan.className = "note-text";
  textSpan.innerHTML = `<strong>${escapeHtml(n.title)}</strong>: ${escapeHtml(n.content)}`;
  li.appendChild(textSpan);

  const actions = document.createElement("span");
  actions.className = "note-actions";

  const editBtn = document.createElement("button");
  editBtn.textContent = "Edit";
  editBtn.className = "btn-edit";
  editBtn.onclick = () => enterEditMode(n);
  actions.appendChild(editBtn);

  const extractBtn = document.createElement("button");
  extractBtn.textContent = "Extract";
  extractBtn.className = "btn-extract";
  extractBtn.title = "Extract action items and tags from this note";
  extractBtn.onclick = () => extractFromNote(n.id, li);
  actions.appendChild(extractBtn);

  const deleteBtn = document.createElement("button");
  deleteBtn.textContent = "Delete";
  deleteBtn.className = "btn-delete";
  deleteBtn.onclick = () => deleteNote(n.id);
  actions.appendChild(deleteBtn);

  li.appendChild(actions);
  return li;
}

function enterEditMode(note) {
  editingNoteId = note.id;
  document.getElementById("note-title").value = note.title;
  document.getElementById("note-content").value = note.content;
  document.getElementById("note-submit-btn").textContent = "Save Changes";
  document.getElementById("note-cancel-btn").style.display = "inline-block";
  document.getElementById("note-title").focus();
}

function exitEditMode() {
  editingNoteId = null;
  document.getElementById("note-form").reset();
  document.getElementById("note-submit-btn").textContent = "Add Note";
  document.getElementById("note-cancel-btn").style.display = "none";
}

async function saveNote(title, content) {
  if (editingNoteId !== null) {
    await fetchJSON(`/notes/${editingNoteId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, content }),
    });
  } else {
    await fetchJSON("/notes/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, content }),
    });
  }
}

async function deleteNote(id) {
  if (!confirm("Delete this note?")) return;
  try {
    await fetchJSON(`/notes/${id}`, { method: "DELETE" });
    loadNotes(currentSearchQuery());
  } catch (err) {
    showError("Failed to delete note: " + err.message);
  }
}

async function extractFromNote(noteId, liElement) {
  try {
    const result = await fetchJSON(`/notes/${noteId}/extract?save_items=true`, {
      method: "POST",
    });

    const { action_items, tags } = result;

    let existing = liElement.querySelector(".extract-result");
    if (existing) existing.remove();

    const summary = document.createElement("div");
    summary.className = "extract-result";

    if (action_items.length === 0 && tags.length === 0) {
      summary.textContent = "Nothing extracted.";
    } else {
      if (action_items.length > 0) {
        summary.innerHTML += `<span class="extract-label">✅ ${action_items.length} action item(s) saved</span>`;
      }
      if (tags.length > 0) {
        summary.innerHTML += ` <span class="extract-tags">🏷 ${tags.map((t) => "#" + t).join(" ")}</span>`;
      }
    }

    liElement.appendChild(summary);

    if (action_items.length > 0) {
      loadActions();
    }
  } catch (err) {
    showError("Failed to extract from note: " + err.message);
  }
}

// ── Action Items ─────────────────────────────────────────────────────────────

async function loadActions() {
  const list = document.getElementById("actions");
  list.innerHTML = "";

  try {
    const items = await fetchJSON("/action-items/");

    if (items.length === 0) {
      const li = document.createElement("li");
      li.className = "empty-state";
      li.textContent = "No action items yet.";
      list.appendChild(li);
      return;
    }

    for (const a of items) {
      list.appendChild(buildActionItem(a));
    }
  } catch (err) {
    showError("Failed to load action items: " + err.message);
  }
}

function buildActionItem(a) {
  const li = document.createElement("li");
  li.className = "action-item" + (a.completed ? " completed" : "");

  const label = document.createElement("span");
  label.textContent = a.description;
  li.appendChild(label);

  const badge = document.createElement("span");
  badge.className =
    "status-badge " + (a.completed ? "badge-done" : "badge-open");
  badge.textContent = a.completed ? "done" : "open";
  li.appendChild(badge);

  if (!a.completed) {
    const btn = document.createElement("button");
    btn.textContent = "Complete";
    btn.className = "btn-complete";
    btn.onclick = async () => {
      try {
        await fetchJSON(`/action-items/${a.id}/complete`, { method: "PUT" });
        loadActions();
      } catch (err) {
        showError("Failed to complete item: " + err.message);
      }
    };
    li.appendChild(btn);
  }

  return li;
}

// ── Bootstrap ─────────────────────────────────────────────────────────────────

window.addEventListener("DOMContentLoaded", () => {
  // Note form (add / edit)
  document.getElementById("note-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const title = document.getElementById("note-title").value.trim();
    const content = document.getElementById("note-content").value.trim();
    if (!title || !content) return;

    try {
      await saveNote(title, content);
      exitEditMode();
      loadNotes(currentSearchQuery());
    } catch (err) {
      showError("Failed to save note: " + err.message);
    }
  });

  document.getElementById("note-cancel-btn")?.addEventListener("click", () => {
    exitEditMode();
  });

  // Search
  document.getElementById("search-btn")?.addEventListener("click", () => {
    loadNotes(currentSearchQuery());
  });

  document.getElementById("search-input")?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") loadNotes(currentSearchQuery());
  });

  document.getElementById("search-clear-btn")?.addEventListener("click", () => {
    document.getElementById("search-input").value = "";
    loadNotes("");
  });

  // Action item form
  document
    .getElementById("action-form")
    .addEventListener("submit", async (e) => {
      e.preventDefault();
      const description = document.getElementById("action-desc").value.trim();
      if (!description) return;

      try {
        await fetchJSON("/action-items/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ description }),
        });
        e.target.reset();
        loadActions();
      } catch (err) {
        showError("Failed to add action item: " + err.message);
      }
    });

  // Initial load
  loadNotes();
  loadActions();
});
