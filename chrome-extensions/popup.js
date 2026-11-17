// HoaxLens ID - Popup Script (Modern Minimalist, Scanning Animation, SVG Gauge & Actions)

const DEFAULT_API_BASE = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", async () => {
  // Navigation & Sliding Pill Glider
  const navGlider = document.getElementById("navGlider");
  const tabButtons = document.querySelectorAll(".nav-tab");
  const tabPanes = document.querySelectorAll(".tab-pane");
  const tabsTrack = document.getElementById("tabsTrack");
  const appMain = document.getElementById("appMain");

  // Header Refresh Button
  const btnHeaderRefresh = document.getElementById("btnHeaderRefresh");

  // Elements
  const themeToggle = document.getElementById("themeToggle");

  // Tab 1 (URL Scanner)
  const currentTabUrlEl = document.getElementById("currentTabUrl");
  const btnScanUrl = document.getElementById("btnScanUrl");
  const urlScanProgress = document.getElementById("urlScanProgress");
  const urlScanFill = document.getElementById("urlScanFill");
  const urlScanStepLabel = document.getElementById("urlScanStepLabel");
  const urlResultContainer = document.getElementById("urlResultContainer");

  // Tab 2 (Text Scanner)
  const inputTitle = document.getElementById("inputTitle");
  const inputText = document.getElementById("inputText");
  const btnScanText = document.getElementById("btnScanText");
  const textScanProgress = document.getElementById("textScanProgress");
  const textScanFill = document.getElementById("textScanFill");
  const textScanStepLabel = document.getElementById("textScanStepLabel");
  const textResultContainer = document.getElementById("textResultContainer");

  // Tab 3 (Service Status)
  const serviceStatusText = document.getElementById("serviceStatusText");

  // State
  let currentTab = null;
  let apiBase = DEFAULT_API_BASE;
  let lastResultData = null;

  // 1. Sliding Pill Tab Glider Positioner
  function updateGlider(activeTabEl) {
    if (!navGlider || !activeTabEl) return;
    const left = activeTabEl.offsetLeft;
    const width = activeTabEl.offsetWidth;
    navGlider.style.transform = `translateX(${left - 3}px)`;
    navGlider.style.width = `${width}px`;
  }

  // Initial glider placement
  const initialActiveTab = document.querySelector(".nav-tab.active");
  if (initialActiveTab) {
    setTimeout(() => updateGlider(initialActiveTab), 50);
  }

  // 2. Tab Navigation Switching with Synchronized Page Sliding
  let slideTimer = null;

  function switchTab(btn, targetIndex) {
    if (!btn) return;

    tabButtons.forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    updateGlider(btn);

    if (tabsTrack) {
      tabsTrack.classList.add("is-sliding");
      tabsTrack.style.transform = `translateX(-${targetIndex * (100 / 3)}%)`;
    }

    tabPanes.forEach((p, idx) => {
      if (idx === targetIndex) {
        p.classList.add("active");
      } else {
        p.classList.remove("active");
      }
    });

    if (appMain) {
      appMain.scrollTo({ top: 0, behavior: "smooth" });
    }

    // Auto-check server status in real time when Settings tab is opened
    if (targetIndex === 2) {
      checkServerStatusRealtime();
    }

    clearTimeout(slideTimer);
    slideTimer = setTimeout(() => {
      if (tabsTrack) {
        tabsTrack.classList.remove("is-sliding");
      }
    }, 280);
  }

  tabButtons.forEach((btn, index) => {
    btn.addEventListener("click", () => {
      switchTab(btn, index);
    });
  });

  window.addEventListener("resize", () => {
    const active = document.querySelector(".nav-tab.active");
    if (active) updateGlider(active);
  });

  // 3. Theme Initialization & Toggle
  const storage = await chrome.storage.local.get(["theme", "apiBaseUrl", "lastManualResult", "lastAnalysisTime"]);
  const savedTheme = storage.theme;
  const systemPrefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  const initialTheme = savedTheme || (systemPrefersDark ? "dark" : "light");

  applyTheme(initialTheme);

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    if (themeToggle) {
      themeToggle.checked = (theme === "dark");
    }
  }

  if (themeToggle) {
    themeToggle.addEventListener("change", async (e) => {
      const selectedTheme = e.target.checked ? "dark" : "light";
      applyTheme(selectedTheme);
      await chrome.storage.local.set({ theme: selectedTheme });
    });
  }

  // 4. Load Backend API Setting
  if (storage.apiBaseUrl) {
    apiBase = storage.apiBaseUrl;
  }

  // 5. Detect Active Browser Tab URL
  async function detectActiveTab() {
    try {
      const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
      if (tabs && tabs.length > 0) {
        currentTab = tabs[0];
        const url = currentTab.url || "";
        currentTabUrlEl.textContent = url;

        if (!url.startsWith("http://") && !url.startsWith("https://")) {
          btnScanUrl.disabled = true;
          btnScanUrl.textContent = "Bukan Halaman Web (HTTP/HTTPS)";
          btnScanUrl.style.opacity = "0.5";
          btnScanUrl.style.cursor = "not-allowed";
        } else {
          btnScanUrl.disabled = false;
          btnScanUrl.textContent = "Periksa Halaman Ini";
          btnScanUrl.style.opacity = "1";
          btnScanUrl.style.cursor = "pointer";
        }
      }
    } catch (err) {
      currentTabUrlEl.textContent = "Gagal mendeteksi tab.";
    }
  }

  detectActiveTab();

  // Header Re-Scan / Refresh Button Handler
  if (btnHeaderRefresh) {
    btnHeaderRefresh.addEventListener("click", async () => {
      btnHeaderRefresh.classList.add("rotating");
      // Clear previous URL scan result and re-detect tab
      urlResultContainer.classList.add("hidden");
      urlResultContainer.innerHTML = "";
      await detectActiveTab();
      checkServerStatusRealtime();
      setTimeout(() => {
        btnHeaderRefresh.classList.remove("rotating");
      }, 400);
    });
  }

  // Helper: Format ISO Date into Indonesian Locale
  function formatDateTime(dateStr) {
    if (!dateStr || typeof dateStr !== "string") return "";
    const trimmed = dateStr.trim();
    try {
      const d = new Date(trimmed);
      if (!isNaN(d.getTime())) {
        const formatted = new Intl.DateTimeFormat("id-ID", {
          day: "numeric",
          month: "short",
          year: "numeric",
          hour: "2-digit",
          minute: "2-digit",
          hour12: false
        }).format(d);

        const tzOffset = -d.getTimezoneOffset() / 60;
        let tzLabel = "";
        if (tzOffset === 7) tzLabel = " WIB";
        else if (tzOffset === 8) tzLabel = " WITA";
        else if (tzOffset === 9) tzLabel = " WIT";

        return `${formatted.replace(/\./g, ":")}${tzLabel}`;
      }
    } catch (_) {}
    return trimmed;
  }

  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Helper: Progressive Scanning Animation Controller
  async function runScanningProcess({ btn, progressBox, fillEl, labelEl, steps, task }) {
    btn.disabled = true;
    const originalText = btn.textContent;
    btn.textContent = "Sedang Menganalisis...";
    progressBox.classList.remove("hidden");
    fillEl.style.width = "10%";

    let stepIdx = 0;
    labelEl.textContent = steps[0];

    const interval = setInterval(() => {
      stepIdx++;
      if (stepIdx < steps.length) {
        labelEl.textContent = steps[stepIdx];
        const pct = Math.min(88, 25 + stepIdx * 25);
        fillEl.style.width = `${pct}%`;
      }
    }, 650);

    try {
      const result = await task();
      clearInterval(interval);
      fillEl.style.width = "100%";
      labelEl.textContent = "Analisis selesai!";
      setTimeout(() => {
        progressBox.classList.add("hidden");
        btn.disabled = false;
        btn.textContent = originalText;
      }, 400);
      return result;
    } catch (err) {
      clearInterval(interval);
      progressBox.classList.add("hidden");
      btn.disabled = false;
      btn.textContent = originalText;
      throw err;
    }
  }

  // Helper: Generate 2-3 Key Indicators
  function generateKeyIndicators(data) {
    const isHoax = (data.verdict || data.overall_prediction) === "HOAX";
    const stats = data.stats || {};
    const triggers = (data.top_hoax_words || []).slice(0, 3);
    const indicators = [];

    if (isHoax) {
      if ((stats.high_risk_sentences || 0) > 0) {
        indicators.push({
          type: "danger",
          text: `Ditemukan ${stats.high_risk_sentences} kalimat terindikasi manipulasi / berisiko tinggi.`
        });
      } else {
        indicators.push({
          type: "danger",
          text: `Pola redaksional melampaui ambang batas kewajaran cek fakta.`
        });
      }

      if (triggers.length > 0) {
        indicators.push({
          type: "danger",
          text: `Terdeteksi kata pemicu sensasional/klaim sepihak: "${triggers.join('", "')}".`
        });
      } else {
        indicators.push({
          type: "danger",
          text: `Struktur narasi mengindikasikan gaya pesan berantai tanpa verifikasi sumber.`
        });
      }

      indicators.push({
        type: "danger",
        text: `Tidak teridentifikasi rujukan siaran pers atau pernyataan resmi instansi terkait.`
      });
    } else {
      indicators.push({
        type: "success",
        text: `Didominasi kalimat bernada faktual resmi (${stats.low_risk_sentences || 0} kalimat aman).`
      });

      if (triggers.length === 0) {
        indicators.push({
          type: "success",
          text: `Tidak ditemukan kata pemicu manipulatif atau clickbait sensasional.`
        });
      } else {
        indicators.push({
          type: "success",
          text: `Konstruksi kalimat selaras dengan standar tata bahasa jurnalistik.`
        });
      }

      indicators.push({
        type: "success",
        text: `Kredibilitas narasi tergolong konsisten dan berimbang.`
      });
    }

    return indicators;
  }

  // Helper: Render Result Card
  function renderResult(data, container) {
    lastResultData = data;
    container.classList.remove("hidden");
    container.innerHTML = "";

    const isHoax = (data.verdict || data.overall_prediction) === "HOAX";
    const badgeText = isHoax ? "Terindikasi Hoaks" : "Faktual / Valid";
    const badgeClass = isHoax ? "hoax" : "valid";
    const confidence = parseFloat(data.confidence || data.overall_confidence || 0);
    const stats = data.stats || {};
    const meta = data.metadata || {};

    // Arc gauge calculation (circumference of radius 72 is pi*72 = 226.19)
    const totalArc = 226.2;
    const dashOffset = totalArc * (1 - Math.min(100, Math.max(0, confidence)) / 100);

    const metaItems = [];
    if (meta.domain) metaItems.push(`<span>${escapeHtml(meta.domain)}</span>`);
    if (meta.author) metaItems.push(`<span>${escapeHtml(meta.author)}</span>`);
    if (meta.date) metaItems.push(`<span>${escapeHtml(formatDateTime(meta.date))}</span>`);

    const indicators = generateKeyIndicators(data);

    let html = `
      <!-- Polished Semi-Circle Gauge Hero Card -->
      <div class="gauge-hero">
        <div class="gauge-svg-container">
          <svg class="gauge-svg" viewBox="0 0 180 105">
            <path class="gauge-track" d="M 18 95 A 72 72 0 0 1 162 95" />
            <path class="gauge-arc ${badgeClass}" id="gaugeArc" d="M 18 95 A 72 72 0 0 1 162 95" style="stroke-dasharray: 226.2; stroke-dashoffset: 226.2;" />
          </svg>
          <div class="gauge-center-content">
            <span class="gauge-hero-number">${confidence.toFixed(1)}%</span>
            <span class="gauge-hero-sublabel">Skor Probabilitas</span>
          </div>
        </div>
        <div class="gauge-badge-row">
          <span class="status-badge ${badgeClass}">${badgeText}</span>
        </div>
      </div>

      <h4 class="result-title">${escapeHtml(data.title || meta.title || "Analisis Berita")}</h4>
      ${metaItems.length > 0 ? `<div class="result-meta">${metaItems.join('<span class="meta-sep">&bull;</span>')}</div>` : ""}

      <!-- Key Indicators Section -->
      <div class="indicators-card">
        <div class="indicators-title">Indikator Kunci Analisis</div>
        <ul class="indicator-items">
          ${indicators.map(ind => `
            <li class="indicator-item">
              <span class="indicator-bullet ${ind.type}"></span>
              <span>${escapeHtml(ind.text)}</span>
            </li>
          `).join("")}
        </ul>
      </div>

      <!-- Stats Grid -->
      <div class="stats-grid">
        <div class="stat-box danger">
          <span class="stat-num">${stats.high_risk_sentences || 0}</span>
          <span class="stat-label">Risiko Tinggi</span>
        </div>
        <div class="stat-box warning">
          <span class="stat-num">${stats.medium_risk_sentences || 0}</span>
          <span class="stat-label">Mencurigakan</span>
        </div>
        <div class="stat-box success">
          <span class="stat-num">${stats.low_risk_sentences || 0}</span>
          <span class="stat-label">Faktual</span>
        </div>
      </div>
    `;

    // Sentences preview
    const sentences = data.sentences || [];
    if (sentences.length > 0) {
      html += `
        <div class="mt-3">
          <h5 class="section-heading">Sorotan Kalimat Kunci</h5>
          <div class="sentence-scroll">
      `;

      sentences.slice(0, 5).forEach((s, idx) => {
        const tier = s.risk_tier || "low";
        const triggers = (s.top_hoax_triggers || []).map(t => typeof t === "object" ? t.word : t).filter(Boolean);

        html += `
          <div class="sentence-card ${tier}">
            <p><span class="sentence-index">#${idx + 1}</span> "${escapeHtml(s.text)}"</p>
            ${triggers.length > 0 ? `<p class="sentence-trigger-words">Kata Pemicu: ${escapeHtml(triggers.join(", "))}</p>` : ""}
          </div>
        `;
      });

      if (sentences.length > 5) {
        html += `<p class="sentence-overflow-note">+${sentences.length - 5} kalimat lainnya tersimpan di database</p>`;
      }

      html += `</div></div>`;
    }

    container.innerHTML = html;

    // Animate Gauge Arc after rendering
    setTimeout(() => {
      const arc = container.querySelector("#gaugeArc");
      if (arc) {
        arc.style.strokeDashoffset = `${dashOffset}`;
      }
    }, 50);
  }

  // 6. Action: Scan Active Tab URL with Progressive Feedback
  btnScanUrl.addEventListener("click", async () => {
    if (!currentTab || !currentTab.url) return;

    try {
      const data = await runScanningProcess({
        btn: btnScanUrl,
        progressBox: urlScanProgress,
        fillEl: urlScanFill,
        labelEl: urlScanStepLabel,
        steps: [
          "1. Mengekstrak teks & struktur halaman...",
          "2. Menganalisis kalimat & pola semantik...",
          "3. Menghitung skor probabilitas..."
        ],
        task: async () => {
          const response = await fetch(`${apiBase}/api/analyze-url`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url: currentTab.url })
          });

          const json = await response.json();
          if (json.status === "error" || response.status !== 200) {
            throw new Error(json.error_msg || "Gagal memproses berita dari URL ini.");
          }
          return json;
        }
      });

      renderResult(data, urlResultContainer, true);
    } catch (err) {
      urlResultContainer.classList.remove("hidden");
      urlResultContainer.innerHTML = `
        <div class="error-box">
          <span class="error-title">Gagal Menganalisis</span>
          <p>${escapeHtml(err.message)}</p>
          <span class="error-hint">Pastikan service backend Laravel aktif (php artisan serve)</span>
        </div>
      `;
    }
  });

  // 7. Action: Scan Manual Text with Progressive Feedback
  btnScanText.addEventListener("click", async () => {
    const text = inputText.value.trim();
    const title = inputTitle.value.trim();

    if (!text) {
      alert("Silakan masukkan teks berita terlebih dahulu.");
      return;
    }

    try {
      const data = await runScanningProcess({
        btn: btnScanText,
        progressBox: textScanProgress,
        fillEl: textScanFill,
        labelEl: textScanStepLabel,
        steps: [
          "1. Memproses naskah teks...",
          "2. Menganalisis kalimat dengan model SVM...",
          "3. Menyusun skor verifikasi..."
        ],
        task: async () => {
          const response = await fetch(`${apiBase}/api/analyze-text`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text, title })
          });

          const json = await response.json();
          if (json.status === "error" || response.status !== 200) {
            throw new Error(json.error_msg || "Gagal menganalisis teks.");
          }
          return json;
        }
      });

      renderResult(data, textResultContainer, false);
    } catch (err) {
      textResultContainer.classList.remove("hidden");
      textResultContainer.innerHTML = `
        <div class="error-box">
          <span class="error-title">Gagal Menganalisis</span>
          <p>${escapeHtml(err.message)}</p>
        </div>
      `;
    }
  });

  // 8. Service Status Check Function (Minimalist)
  async function checkServerStatusRealtime() {
    if (!serviceStatusText) return;

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3500);
      const res = await fetch(`${apiBase}/api/stats`, { signal: controller.signal });
      clearTimeout(timeoutId);

      if (res.ok) {
        serviceStatusText.textContent = "Aktif";
        serviceStatusText.classList.remove("offline");
      } else {
        throw new Error();
      }
    } catch (_) {
      serviceStatusText.textContent = "Tidak Aktif";
      serviceStatusText.classList.add("offline");
    }
  }

  // Initial check on popup load
  checkServerStatusRealtime();

  // 9. Auto-display last manual result if triggered from context menu
  if (storage.lastManualResult) {
    const timeDiff = Date.now() - (storage.lastAnalysisTime || 0);
    if (timeDiff < 120000) {
      const btnTextTab = document.querySelector('[data-tab="tab-text"]');
      if (btnTextTab) btnTextTab.click();
      renderResult(storage.lastManualResult, textResultContainer, false);
    }
  }
});
