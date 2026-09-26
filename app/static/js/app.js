const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chatMessages = document.getElementById("chat-messages");
const catalogGrid = document.getElementById("catalog-grid");
const catalogSubtitle = document.getElementById("catalog-subtitle");
const onboarding = document.getElementById("onboarding");
const onboardingClose = document.getElementById("onboarding-close");

// ---------- Onboarding modal ----------
function showOnboardingIfNeeded() {
  let seen = false;
  try {
    seen = localStorage.getItem("cinematch_onboarded") === "1";
  } catch (e) {
    seen = false;
  }
  if (seen) {
    onboarding.classList.add("hidden");
  }
}

onboardingClose.addEventListener("click", () => {
  onboarding.classList.add("hidden");
  try {
    localStorage.setItem("cinematch_onboarded", "1");
  } catch (e) {
    /* ignore */
  }
});

showOnboardingIfNeeded();

// ---------- Chat ----------
function addMessage(text, sender) {
  const wrap = document.createElement("div");
  wrap.className = `msg ${sender}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = escapeAndBold(text);
  wrap.appendChild(bubble);
  chatMessages.appendChild(wrap);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeAndBold(text) {
  const div = document.createElement("div");
  div.textContent = text;
  let safe = div.innerHTML;
  safe = safe.replace(/\*\*(.+?)\*\*/g, "<b>$1</b>");
  return safe;
}

function matchClass(match) {
  if (match >= 60) return "high";
  if (match >= 30) return "mid";
  return "low";
}

function renderCatalog(recommendations) {
  const cards = Array.from(catalogGrid.querySelectorAll(".card"));

  if (!recommendations || recommendations.length === 0) {
    cards.forEach((card) => {
      card.classList.remove("dimmed", "highlight");
      const badge = card.querySelector(".match-badge");
      if (badge) badge.remove();
      const fill = card.querySelector(".match-fill");
      if (fill) fill.style.width = "0%";
      const terms = card.querySelector(".matched-terms");
      if (terms) terms.innerHTML = "";
    });
    catalogSubtitle.textContent = "All titles";
    return;
  }

  const dataById = {};
  recommendations.forEach((r) => (dataById[r.id] = r));

  cards.forEach((card) => {
    const id = Number(card.dataset.id);
    const posterWrap = card.querySelector(".poster-wrap");
    const fill = card.querySelector(".match-fill");
    const terms = card.querySelector(".matched-terms");
    let badge = card.querySelector(".match-badge");

    if (id in dataById) {
      const rec = dataById[id];
      card.classList.remove("dimmed");
      card.classList.add("highlight");
      if (!badge) {
        badge = document.createElement("span");
        badge.className = "match-badge";
        posterWrap.appendChild(badge);
      }
      badge.textContent = `${rec.match}% match`;
      badge.className = `match-badge ${matchClass(rec.match)}`;

      if (fill) {
        fill.style.width = "0%";
        requestAnimationFrame(() => {
          fill.style.width = `${Math.min(rec.match, 100)}%`;
        });
      }

      if (terms) {
        terms.innerHTML = "";
        (rec.matched_terms || []).forEach((t) => {
          const tag = document.createElement("span");
          tag.className = "term-tag";
          tag.textContent = t;
          terms.appendChild(tag);
        });
      }
    } else {
      card.classList.add("dimmed");
      card.classList.remove("highlight");
      if (badge) badge.remove();
      if (fill) fill.style.width = "0%";
      if (terms) terms.innerHTML = "";
    }
  });

  // reorder: matched first, sorted by match desc
  const sorted = [...cards].sort((a, b) => {
    const ma = dataById[Number(a.dataset.id)]?.match ?? -1;
    const mb = dataById[Number(b.dataset.id)]?.match ?? -1;
    return mb - ma;
  });
  sorted.forEach((card) => catalogGrid.appendChild(card));

  catalogSubtitle.textContent = `${recommendations.length} recommendations found`;
}

// ---------- "How CineBot thinks" pipeline animation ----------
const pipelineSteps = ["parse", "vectorize", "compare", "rank"];

function runPipelineAnimation() {
  return new Promise((resolve) => {
    const els = pipelineSteps.map((s) =>
      document.querySelector(`.pstep[data-step="${s}"]`)
    );
    els.forEach((el) => el.classList.remove("active", "done"));

    let i = 0;
    const stepDelay = 320;

    function tick() {
      if (i > 0) els[i - 1].classList.replace("active", "done");
      if (i < els.length) {
        els[i].classList.add("active");
        i += 1;
        setTimeout(tick, stepDelay);
      } else {
        resolve();
      }
    }
    tick();
  });
}

async function sendMessage(text) {
  addMessage(text, "user");
  chatInput.value = "";

  const typing = document.createElement("div");
  typing.className = "msg bot";
  typing.innerHTML = '<div class="bubble">CineBot is typing...</div>';
  chatMessages.appendChild(typing);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  try {
    const [res] = await Promise.all([
      fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      }),
      runPipelineAnimation(),
    ]);
    const data = await res.json();
    typing.remove();
    addMessage(data.reply, "bot");
    renderCatalog(data.recommendations);
  } catch (err) {
    typing.remove();
    addMessage("Oops, connection trouble. Please try again.", "bot");
  }
}

chatForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = chatInput.value.trim();
  if (!text) return;
  sendMessage(text);
});

document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    sendMessage(chip.dataset.q);
  });
});
