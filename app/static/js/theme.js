// ---------- Tema ----------
function applyTheme(dark) {
  document.documentElement.classList.toggle("dark", dark);
}

$("theme").addEventListener("click", () => {
  const dark = !document.documentElement.classList.contains("dark");
  applyTheme(dark);
  localStorage.setItem("theme", dark ? "dark" : "light");
});

// Ikuti pengaturan sistem jika pengguna belum memilih tema sendiri
window
  .matchMedia("(prefers-color-scheme: dark)")
  .addEventListener("change", (e) => {
    if (!localStorage.getItem("theme")) applyTheme(e.matches);
  });

// ---------- Sidebar (mobile) ----------
function setSidebar(open) {
  sidebar.classList.toggle("-translate-x-full", !open);
  overlay.classList.toggle("hidden", !open);
}

$("menuBtn").addEventListener("click", () =>
  setSidebar(sidebar.classList.contains("-translate-x-full")),
);
overlay.addEventListener("click", () => setSidebar(false));
