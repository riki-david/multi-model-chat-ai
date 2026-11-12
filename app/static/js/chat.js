// ---------- Kirim pesan / hentikan jawaban ----------
let abortCtrl = null; // AbortController untuk jawaban yang sedang berjalan

// Tombol berubah jadi "Stop" selama model menjawab
function setSendMode(isBusy) {
  sendBtn.textContent = isBusy ? "Stop" : "Kirim";
  sendBtn.classList.toggle("bg-red-600", isBusy);
  sendBtn.classList.toggle("hover:bg-red-500", isBusy);
  sendBtn.classList.toggle("bg-indigo-600", !isBusy);
  sendBtn.classList.toggle("hover:bg-indigo-500", !isBusy);
}

function stopGeneration() {
  if (abortCtrl) abortCtrl.abort();
}

async function send() {
  if (busy) return;

  const msg = input.value.trim();
  if (!msg && !pendingFiles.length) return;

  busy = true;
  abortCtrl = new AbortController();
  setSendMode(true);

  const files = pendingFiles; // ambil lampiran, lalu kosongkan
  pendingFiles = [];
  renderChips();
  input.value = "";
  autoResize();

  const model = modelSel.value;
  const shown = files.length
    ? `📎 ${files.map((f) => f.name).join(", ")}${msg ? "\n" + msg : ""}`
    : msg;
  addUserMsg(shown);
  const { wrap, bubble } = addAiMsg(model);

  try {
    if (!currentId) {
      const r = await fetch("/api/conversations", { method: "POST" });
      currentId = (await r.json()).id;
    }

    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        conv_id: currentId,
        message: msg,
        model,
        attachments: files,
      }),
      signal: abortCtrl.signal,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(formatErr(err.detail) || `HTTP ${res.status}`);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      wrap.raw += decoder.decode(value, { stream: true });
      render(bubble, wrap.raw);
      scrollDown(); // menghormati posisi scroll pengguna
    }
  } catch (e) {
    if (e.name === "AbortError") {
      wrap.raw += wrap.raw ? "\n\n[Dihentikan]" : "[Dihentikan]";
    } else {
      wrap.raw += `\n\n[Gagal: ${e.message || e}]`;
    }
    render(bubble, wrap.raw);
  } finally {
    busy = false;
    abortCtrl = null;
    setSendMode(false);
    input.focus();
    await loadList();
  }
}

// ---------- Input ----------
function autoResize() {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 200) + "px";
}

input.addEventListener("input", autoResize);

// Enter saat jawaban berjalan diabaikan, supaya tidak menghentikan jawaban tanpa sengaja
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    if (!busy) send();
  }
});

// Tombol Kirim berfungsi sebagai Stop saat jawaban berjalan
$("form").addEventListener("submit", (e) => {
  e.preventDefault();
  if (busy) stopGeneration();
  else send();
});

// ---------- Mulai ----------
(async function init() {
  const list = await loadList();
  if (list.length) openConversation(list[0].id);
  else newChat();
})();
