// ---------- Kirim pesan ----------
async function send() {
  const msg = input.value.trim();
  if ((!msg && !pendingFiles.length) || busy) return;

  busy = true;
  sendBtn.disabled = true;

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
    wrap.raw += `\n\n[Gagal: ${e.message || e}]`;
    render(bubble, wrap.raw);
  } finally {
    busy = false;
    sendBtn.disabled = false;
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

input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    send();
  }
});

$("form").addEventListener("submit", (e) => {
  e.preventDefault();
  send();
});

// ---------- Mulai ----------
(async function init() {
  const list = await loadList();
  if (list.length) openConversation(list[0].id);
  else newChat();
})();
