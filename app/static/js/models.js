// ---------- Model ----------
// <select id="model"> tetap jadi sumber nilai (dipakai send()).
// Tampilannya dropdown custom: nama model + hint di bawahnya.
let modelInfo = {}; // { nama: { hint, desc } }

function showModelDesc() {
  const name = modelSel.value;
  const m = modelInfo[name];
  $("modelName").textContent = name;
  // Deskripsi lengkap muncul sebagai tooltip saat tombol model diarahkan
  $("modelBtn").title = m?.desc ? `${name}: ${m.desc}` : name;
}

function setModel(name) {
  modelSel.value = name;
  showModelDesc();
  closeModelList();
}

function openModelList() {
  $("modelList").classList.remove("hidden");
  $("modelBtn").setAttribute("aria-expanded", "true");
}

function closeModelList() {
  $("modelList").classList.add("hidden");
  $("modelBtn").setAttribute("aria-expanded", "false");
}

$("modelBtn").addEventListener("click", (e) => {
  e.stopPropagation();
  if ($("modelList").classList.contains("hidden")) openModelList();
  else closeModelList();
});

// Tutup daftar saat klik di luar atau tekan Escape
document.addEventListener("click", (e) => {
  if (!$("modelWrap").contains(e.target)) closeModelList();
});
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeModelList();
});

fetch("/api/model-info")
  .then((r) => r.json())
  .then((list) => {
    const ul = $("modelList");
    list.forEach((m) => {
      modelInfo[m.name] = m;
      modelSel.add(new Option(m.name, m.name));

      // Satu baris dropdown: nama model (besar) + hint (kecil di bawahnya)
      const li = document.createElement("li");
      li.setAttribute("role", "option");
      li.className =
        "px-3 py-2 cursor-pointer hover:bg-slate-100 dark:hover:bg-[#252a35]";
      li.innerHTML = `
        <div class="text-sm font-medium text-slate-800 dark:text-slate-100"></div>
        <div class="text-xs text-slate-500 dark:text-slate-400"></div>`;
      li.children[0].textContent = m.name;
      li.children[1].textContent = m.hint || "";
      li.addEventListener("click", () => setModel(m.name));
      ul.appendChild(li);
    });
    if (list.length) setModel(list[0].name);
  });
