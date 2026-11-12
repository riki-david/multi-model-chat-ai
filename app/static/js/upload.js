// ---------- Lampiran ----------
let pendingFiles = []; // [{ name, kind, content?, mime?, data? }]

// Menampilkan chip lampiran di atas input
function renderChips() {
  const box = $("chips");
  box.innerHTML = "";
  pendingFiles.forEach((f, i) => {
    const chip = document.createElement("span");
    chip.className =
      "inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-full bg-slate-200 dark:bg-[#252a35]";
    chip.textContent = (f.kind === "image" ? "🖼 " : "📄 ") + f.name;

    const x = document.createElement("button");
    x.type = "button";
    x.textContent = "×";
    x.className = "ml-1 text-slate-500 hover:text-red-500";
    x.onclick = () => {
      pendingFiles.splice(i, 1);
      renderChips();
    };
    chip.appendChild(x);
    box.appendChild(chip);
  });
}

// Upload satu atau banyak file, lalu tampilkan chip-nya
async function uploadFiles(fileList) {
  for (const f of fileList) {
    const fd = new FormData();
    fd.append("file", f);
    const res = await fetch("/api/upload", { method: "POST", body: fd });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      toast(formatErr(err.detail) || `Gagal upload ${f.name}`);
      continue;
    }
    pendingFiles.push(await res.json());
    renderChips();
  }
}

// Tombol 📎
$("attach").addEventListener("click", () => $("file").click());

$("file").addEventListener("change", async (e) => {
  await uploadFiles(e.target.files);
  e.target.value = ""; // agar file yang sama bisa dipilih lagi
});

// ---------- Drag and drop ----------
const dropzone = $("dropzone");
const DROP_CLASS = ["ring-2", "ring-indigo-500"];
let dragDepth = 0; // dragenter/dragleave juga terpicu saat pindah ke elemen anak

// Hanya proses drag yang membawa file, bukan teks atau elemen halaman
function hasFiles(e) {
  return [...(e.dataTransfer?.types || [])].includes("Files");
}

dropzone.addEventListener("dragenter", (e) => {
  if (!hasFiles(e)) return;
  e.preventDefault();
  dragDepth++;
  dropzone.classList.add(...DROP_CLASS);
});

dropzone.addEventListener("dragover", (e) => {
  if (!hasFiles(e)) return;
  e.preventDefault(); // wajib agar event drop bisa terjadi
  e.dataTransfer.dropEffect = "copy";
});

dropzone.addEventListener("dragleave", () => {
  dragDepth = Math.max(0, dragDepth - 1);
  if (dragDepth === 0) dropzone.classList.remove(...DROP_CLASS);
});

dropzone.addEventListener("drop", (e) => {
  if (!hasFiles(e)) return;
  e.preventDefault();
  dragDepth = 0;
  dropzone.classList.remove(...DROP_CLASS);
  uploadFiles(e.dataTransfer.files);
});

// Jika file dilepas di luar area input, browser akan membukanya sebagai halaman.
// Blokir perilaku itu di seluruh window.
["dragover", "drop"].forEach((type) =>
  window.addEventListener(type, (e) => {
    if (hasFiles(e)) e.preventDefault();
  }),
);
