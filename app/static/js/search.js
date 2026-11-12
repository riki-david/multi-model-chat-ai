// ---------- Pencarian riwayat ----------
const searchInput = $("searchInput");
const listLabel = $("listLabel");
let searchTimer = null;

// Pencarian dianggap aktif jika kata yang dicari minimal 2 karakter
function searchActive() {
  return searchInput.value.trim().length >= 2;
}

function clearSearch() {
  searchInput.value = "";
  listLabel.textContent = "Riwayat";
}

function renderSearchResults(list, q) {
  listLabel.textContent = `Hasil untuk "${q}"`;
  convList.innerHTML = "";

  if (!list.length) {
    const empty = document.createElement("div");
    empty.className = "px-3 py-2 text-sm text-slate-500 dark:text-slate-400";
    empty.textContent = "Tidak ada hasil";
    convList.appendChild(empty);
    return;
  }

  list.forEach((r) => {
    const el = document.createElement("div");
    el.className =
      "flex flex-col items-start gap-0.5 rounded-lg px-3 py-2 text-sm cursor-pointer transition " +
      "text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-[#1e222b]";

    const t = document.createElement("span");
    t.className = "w-full truncate font-medium";
    t.textContent = r.title || "(tanpa judul)";
    el.appendChild(t);

    if (r.snippet) {
      const s = document.createElement("span");
      s.className =
        "w-full truncate text-xs text-slate-500 dark:text-slate-400";
      s.textContent = r.snippet;
      el.appendChild(s);
    }

    el.addEventListener("click", () => {
      clearSearch();
      openConversation(r.id);
    });
    convList.appendChild(el);
  });
}

async function runSearch(q) {
  try {
    const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const list = await res.json();
    // Abaikan hasil lama jika kata di kotak sudah berubah
    if (searchInput.value.trim() !== q) return;
    renderSearchResults(list, q);
  } catch {
    toast("Pencarian gagal", "error");
  }
}

// Tunggu 300ms setelah mengetik sebelum mencari, supaya tidak kirim request tiap huruf
searchInput.addEventListener("input", () => {
  clearTimeout(searchTimer);
  const q = searchInput.value.trim();
  if (q.length < 2) {
    listLabel.textContent = "Riwayat";
    loadList();
    return;
  }
  searchTimer = setTimeout(() => runSearch(q), 300);
});

// Esc di kotak cari = bersihkan pencarian
searchInput.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    clearSearch();
    loadList();
  }
});
