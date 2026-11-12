// ---------- Elemen & state global ----------
const $ = (id) => document.getElementById(id);

const chat = $("chat");
const scroll = $("scroll");
const input = $("input");
const sendBtn = $("send");
const modelSel = $("model");
const emptyEl = $("empty");
const convList = $("convList");
const titleEl = $("title");
const sidebar = $("sidebar");
const overlay = $("overlay");

let currentId = null; // ID chat yang sedang dibuka
let busy = false; // true saat menunggu jawaban model

// ---------- Konfigurasi markdown & rumus ----------
const mathOpts = {
  delimiters: [
    { left: "$$", right: "$$", display: true },
    { left: "$", right: "$", display: false },
    { left: "\\(", right: "\\)", display: false },
    { left: "\\[", right: "\\]", display: true },
  ],
  throwOnError: false,
};

const BTN_SMALL =
  "text-xs px-2.5 py-1 rounded-md border border-slate-300 dark:border-slate-600 " +
  "bg-white dark:bg-[#252a35] text-slate-600 dark:text-slate-300 " +
  "hover:text-indigo-500 hover:border-indigo-500 transition";

// ---------- Auto scroll ----------
let stickToBottom = true; // true = layar ikut turun saat ada teks baru

// Dianggap "di bawah" jika selisih kurang dari 80px
scroll.addEventListener("scroll", () => {
  const distance = scroll.scrollHeight - scroll.scrollTop - scroll.clientHeight;
  stickToBottom = distance < 80;
});

// force = true dipakai saat pesan baru dikirim atau chat dibuka
function scrollDown(force = false) {
  if (force) stickToBottom = true;
  if (stickToBottom) scroll.scrollTop = scroll.scrollHeight;
}

// ---------- Notifikasi (SweetAlert2 mode toast) ----------
// Toast kecil di kanan atas. Ikon berwarna otomatis:
// "info" (biru), "success" (hijau), "error" (merah), "warning" (kuning).
const Toast = Swal.mixin({
  toast: true,
  position: "top-end",
  showConfirmButton: false,
  timer: 2500,
  timerProgressBar: true,
  showCloseButton: true,
  didOpen: (el) => {
    // Timer berhenti saat kursor di atas notifikasi, lanjut saat kursor pergi
    el.addEventListener("mouseenter", Swal.stopTimer);
    el.addEventListener("mouseleave", Swal.resumeTimer);
  },
});

function isDarkMode() {
  return document.documentElement.classList.contains("dark");
}

// Pemakaian:
//   toast("Chat dihapus")            -> info
//   toast("Tersimpan", "success")    -> hijau
//   toast("Gagal upload", "error")   -> merah
function toast(msg, type = "info") {
  const dark = isDarkMode();
  Toast.fire({
    icon: type,
    title: msg,
    background: dark ? "#1e222b" : "#ffffff",
    color: dark ? "#e2e8f0" : "#1e293b",
  });
}

// Ubah detail error FastAPI (string atau list) menjadi teks yang bisa dibaca
function formatErr(detail) {
  if (!detail) return "";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail))
    return detail
      .map((d) => `${(d.loc || []).slice(1).join(".")}: ${d.msg}`)
      .join("; ");
  return JSON.stringify(detail);
}

// ---------- Salin teks ----------
async function copyText(text, btn) {
  try {
    await navigator.clipboard.writeText(text);
  } catch {
    // Cadangan untuk browser yang menolak Clipboard API (misalnya bukan HTTPS)
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    document.execCommand("copy");
    ta.remove();
  }
  if (btn) {
    const old = btn.textContent;
    btn.textContent = "Tersalin";
    setTimeout(() => (btn.textContent = old), 1500);
  } else {
    toast("Tersalin", "success");
  }
}
