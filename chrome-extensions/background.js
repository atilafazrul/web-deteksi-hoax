// HoaxLens ID - Background Service Worker (Manifest V3)

const DEFAULT_API_BASE = "http://127.0.0.1:8000";

// Register Context Menu on Installation
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "hoaxlens_check_selection",
    title: "Periksa Hoaks dengan HoaxLens ID",
    contexts: ["selection"]
  });
});

// Handle Context Menu Click
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === "hoaxlens_check_selection") {
    const selectedText = (info.selectionText || "").trim();
    if (!selectedText) return;

    // Show initial loading notification
    chrome.notifications.create({
      type: "basic",
      iconUrl: "icons/icon48.png",
      title: "HoaxLens ID",
      message: "Sedang menganalisis teks terpilih...",
      priority: 1
    });

    try {
      const storage = await chrome.storage.local.get(["apiBaseUrl"]);
      const apiBase = storage.apiBaseUrl || DEFAULT_API_BASE;

      const response = await fetch(`${apiBase}/api/analyze-text`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: selectedText,
          title: "Pemeriksaan Teks Seleksi"
        })
      });

      const data = await response.json();

      if (data.status === "error" || !data.verdict) {
        throw new Error(data.error_msg || "Gagal menganalisis teks.");
      }

      const isHoax = data.verdict === "HOAX";
      const confidence = data.confidence || 0;
      const title = isHoax ? "Terindikasi HOAKS" : "Terindikasi VALID";
      const message = `Tingkat Keyakinan: ${confidence}%\nProb Hoaks: ${data.prob_hoax || 0}%\nTotal Kalimat: ${data.stats?.total_sentences || 1}`;

      // Store result so popup can show it
      await chrome.storage.local.set({
        lastManualResult: data,
        lastAnalysisTime: Date.now()
      });

      chrome.notifications.create({
        type: "basic",
        iconUrl: "icons/icon48.png",
        title: `HoaxLens ID: ${title}`,
        message: message,
        priority: 2
      });

    } catch (err) {
      chrome.notifications.create({
        type: "basic",
        iconUrl: "icons/icon48.png",
        title: "HoaxLens ID - Gagal",
        message: err.message || "Pastikan backend Laravel berjalan di port 8000.",
        priority: 1
      });
    }
  }
});
