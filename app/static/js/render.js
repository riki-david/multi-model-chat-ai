// ---------- Render pesan ----------
function enhanceCodeBlocks(container) {
  container.querySelectorAll("pre").forEach((pre) => {
    if (pre.parentElement.classList.contains("relative")) return;
    const wrap = document.createElement("div");
    wrap.className = "relative my-2";
    pre.parentNode.insertBefore(wrap, pre);
    wrap.appendChild(pre);

    const btn = document.createElement("button");
    btn.className =
      "text-xs px-2.5 py-1 rounded-md absolute top-2 right-2 " +
      "bg-slate-700 text-slate-100 border border-slate-500 hover:bg-slate-600 transition";
    btn.textContent = "Salin";
    btn.onclick = () => copyText(pre.innerText, btn);
    wrap.appendChild(btn);
  });
}

function render(bubble, raw) {
  bubble.innerHTML = DOMPurify.sanitize(marked.parse(raw));
  renderMathInElement(bubble, mathOpts);
  enhanceCodeBlocks(bubble);
}

function clearChat() {
  chat.querySelectorAll(":scope > div:not(#empty)").forEach((m) => m.remove());
}

function addUserMsg(text) {
  emptyEl.style.display = "none";
  const wrap = document.createElement("div");
  wrap.className = "flex flex-col items-end max-w-[85%] self-end";
  wrap.innerHTML = `
    <div class="whitespace-pre-wrap break-words rounded-2xl rounded-br-md bg-indigo-600 text-white px-4 py-2.5 leading-relaxed shadow-sm"></div>
    <div class="mt-1 flex"><button class="${BTN_SMALL}">Salin</button></div>`;
  wrap.querySelector(".rounded-2xl").textContent = text;
  wrap.querySelector("button").onclick = (e) => copyText(text, e.currentTarget);
  chat.appendChild(wrap);
  scrollDown(true);
}

function addAiMsg(model) {
  emptyEl.style.display = "none";
  const wrap = document.createElement("div");
  wrap.className = "flex flex-col items-start w-full self-start";
  wrap.innerHTML = `
    <div class="text-xs text-slate-500 dark:text-slate-400 mb-1 px-1"></div>
    <div class="bubble md w-full rounded-2xl rounded-bl-md bg-white dark:bg-[#1e222b] border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100 px-4 py-3 leading-relaxed break-words shadow-sm">
      <span class="inline-flex gap-1 py-1">
        <span class="w-2 h-2 rounded-full bg-slate-400 animate-bounce"></span>
        <span class="w-2 h-2 rounded-full bg-slate-400 animate-bounce [animation-delay:.15s]"></span>
        <span class="w-2 h-2 rounded-full bg-slate-400 animate-bounce [animation-delay:.3s]"></span>
      </span>
    </div>
    <div class="mt-1.5 flex gap-1.5"><button class="${BTN_SMALL}">Salin</button></div>`;
  wrap.querySelector(".text-xs").textContent = model || "";

  const bubble = wrap.querySelector(".bubble");
  const copyBtn = wrap.querySelector(":scope > div:last-child button");
  wrap.raw = "";
  copyBtn.onclick = () => copyText(wrap.raw, copyBtn);

  chat.appendChild(wrap);
  scrollDown(true);
  return { wrap, bubble };
}
