// ---------- Riwayat / sidebar ----------
const ITEM_BASE =
  "group flex items-center gap-2 rounded-lg px-3 py-2 text-sm cursor-pointer transition";

function convItem(c) {
  const el = document.createElement("div");
  const active = c.id === currentId;
  el.className =
    ITEM_BASE +
    (active
      ? " bg-indigo-50 text-indigo-700 dark:bg-[#252a35] dark:text-indigo-300 font-medium"
      : " text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-[#1e222b]");

  el.innerHTML = `
    <span class="flex-1 truncate"></span>
    <button class="del shrink-0 p-1 rounded-md text-slate-400 hover:text-red-500 md:opacity-0 md:group-hover:opacity-100 transition"
      title="Hapus chat" aria-label="Hapus chat">
      <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 6h18M8 6V4h8v2m1 0v14H7V6h10"/>
      </svg>
    </button>`;
  el.querySelector("span").textContent = c.title;
  el.addEventListener("click", () => openConversation(c.id));
  el.querySelector(".del").addEventListener("click", (e) => {
    e.stopPropagation();
    deleteConversation(c.id);
  });
  return el;
}

async function loadList() {
  const list = await (await fetch("/api/conversations")).json();
  convList.innerHTML = "";
  list.forEach((c) => convList.appendChild(convItem(c)));

  const cur = list.find((c) => c.id === currentId);
  if (cur) titleEl.textContent = cur.title;
  return list;
}

async function openConversation(id) {
  if (busy) return;
  const res = await fetch(`/api/conversations/${id}`);
  if (!res.ok) {
    toast("Percakapan tidak ditemukan");
    return loadList();
  }
  const data = await res.json();

  currentId = id;
  clearChat();
  data.messages.forEach((m) => {
    if (m.role === "user") {
      addUserMsg(m.content);
    } else {
      const { wrap, bubble } = addAiMsg(m.model);
      wrap.raw = m.content;
      render(bubble, m.content);
    }
  });
  titleEl.textContent = data.title;
  if (!data.messages.length) emptyEl.style.display = "";
  scrollDown(true);
  setSidebar(false);
  await loadList();
}

function newChat() {
  if (busy) return;
  currentId = null;
  pendingFiles = [];
  renderChips();
  clearChat();
  emptyEl.style.display = "";
  titleEl.textContent = "Chat baru";
  setSidebar(false);
  loadList();
  input.focus();
}

// Hapus chat lewat modal konfirmasi (menggantikan confirm() bawaan browser)
async function deleteConversation(id) {
  if (busy) return;

  const ok = await Modal.confirm({
    title: "Hapus chat ini?",
    message:
      "Riwayat percakapan ini akan dihapus permanen dan tidak bisa dikembalikan.",
    confirmText: "Hapus",
    cancelText: "Batal",
    danger: true,
  });
  if (!ok) return;

  await fetch(`/api/conversations/${id}`, { method: "DELETE" });
  toast("Chat dihapus", "success");
  if (id === currentId) newChat();
  else loadList();
}

$("newChat").addEventListener("click", newChat);
