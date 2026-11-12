// ---------- Modal reusable ----------
// Pemakaian:
//   const ok = await Modal.confirm({ title, message, confirmText, danger: true });
//   const pilihan = await Modal.open({ title, body, actions: [{ label, value, variant }] });
//
// Nilai yang dikembalikan:
//   - confirm()  : true (dikonfirmasi) atau false (batal / Esc / klik luar)
//   - open()     : value dari tombol yang ditekan, atau null jika ditutup tanpa memilih

const Modal = (() => {
  // Gaya tombol: "cancel" (netral), "primary" (indigo), "danger" (merah)
  const BTN = {
    base: "px-4 py-2 text-sm rounded-xl transition",
    cancel:
      "border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-[#252a35]",
    primary: "bg-indigo-600 hover:bg-indigo-500 text-white font-semibold",
    danger: "bg-red-600 hover:bg-red-500 text-white font-semibold",
  };

  let root = null; // elemen modal, dibuat sekali saat pertama dipakai
  let resolver = null; // fungsi resolve Promise dari open()
  let lastFocus = null; // elemen yang fokus sebelum modal dibuka

  function isOpen() {
    return !!root && !root.classList.contains("hidden");
  }

  function ensureRoot() {
    if (root) return root;

    root = document.createElement("div");
    root.className =
      "hidden fixed inset-0 z-50 flex items-center justify-center p-4";
    root.setAttribute("role", "dialog");
    root.setAttribute("aria-modal", "true");
    root.innerHTML = `
      <div data-backdrop class="absolute inset-0 bg-black/50"></div>
      <div class="relative w-full max-w-sm rounded-2xl bg-white dark:bg-[#171a21] border border-slate-200 dark:border-slate-700 shadow-xl p-5">
        <h2 data-title class="text-base font-semibold text-slate-800 dark:text-slate-100"></h2>
        <div data-body class="mt-2 text-sm text-slate-600 dark:text-slate-300 break-words"></div>
        <div data-actions class="mt-5 flex justify-end gap-2"></div>
      </div>`;
    document.body.appendChild(root);

    // Klik area gelap di luar kotak = batal
    root
      .querySelector("[data-backdrop]")
      .addEventListener("click", () => close(null));

    // Esc = batal, Tab dikunci di dalam modal agar fokus tidak lari ke halaman di belakang
    document.addEventListener("keydown", (e) => {
      if (!isOpen()) return;
      if (e.key === "Escape") return close(null);
      if (e.key === "Tab") {
        const buttons = [...root.querySelectorAll("button")];
        if (!buttons.length) return;
        const first = buttons[0];
        const last = buttons[buttons.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    });

    return root;
  }

  function close(value) {
    if (!isOpen()) return;
    root.classList.add("hidden");
    document.body.classList.remove("overflow-hidden");

    const resolve = resolver;
    resolver = null;
    if (lastFocus && typeof lastFocus.focus === "function") lastFocus.focus();
    if (resolve) resolve(value);
  }

  // Modal generik. body bisa berupa teks atau elemen DOM (Node).
  function open({ title = "", body = "", actions = [] } = {}) {
    ensureRoot();

    // Jika modal sudah terbuka, tutup dulu agar Promise sebelumnya tidak menggantung
    if (isOpen()) close(null);

    lastFocus = document.activeElement;

    root.querySelector("[data-title]").textContent = title;

    const bodyEl = root.querySelector("[data-body]");
    if (body instanceof Node) {
      bodyEl.replaceChildren(body);
    } else {
      bodyEl.textContent = body;
    }

    const actionsEl = root.querySelector("[data-actions]");
    actionsEl.innerHTML = "";
    actions.forEach((a) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = a.label;
      btn.className = `${BTN.base} ${BTN[a.variant || "cancel"]}`;
      btn.addEventListener("click", () => close(a.value));
      actionsEl.appendChild(btn);
    });

    root.classList.remove("hidden");
    document.body.classList.add("overflow-hidden");

    // Fokus ke tombol pertama. Untuk konfirmasi, tombol pertama adalah "Batal"
    // supaya menekan Enter tidak langsung menghapus.
    const firstBtn = actionsEl.querySelector("button");
    if (firstBtn) firstBtn.focus();

    return new Promise((resolve) => {
      resolver = resolve;
    });
  }

  // Konfirmasi ya/tidak. Mengembalikan Promise<boolean>.
  function confirm({
    title = "Konfirmasi",
    message = "",
    confirmText = "OK",
    cancelText = "Batal",
    danger = false,
  } = {}) {
    return open({
      title,
      body: message,
      actions: [
        { label: cancelText, value: false, variant: "cancel" },
        {
          label: confirmText,
          value: true,
          variant: danger ? "danger" : "primary",
        },
      ],
    }).then((value) => value === true);
  }

  return { open, close, confirm };
})();
