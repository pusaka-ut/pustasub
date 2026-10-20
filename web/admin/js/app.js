import { Config } from "./config.js";
import { Icons } from "./icons.js";
import { ApiClient } from "./api.js";
import { BroadcastSocket } from "./websocket.js";
import { VocabManager } from "./vocab-manager.js";
import { UiController } from "./ui-controller.js";

document.addEventListener("DOMContentLoaded", () => {
  const api = new ApiClient(Config.apiBase);
  const ui = new UiController(api, (msg) => ui.showToast(msg));
  const vocab = new VocabManager(api, "hotwords-chip-container", "vocab-count-badge", (msg) => ui.showToast(msg));

  const copyToClipboard = async (text) => {
    if (navigator.clipboard && window.isSecureContext) {
      try {
        await navigator.clipboard.writeText(text);
        return true;
      } catch (err) {}
    }
    const textArea = document.createElement("textarea");
    textArea.value = text;
    textArea.style.position = "fixed";
    textArea.style.opacity = "0";
    textArea.style.left = "-9999px";
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    try {
      const successful = document.execCommand("copy");
      textArea.remove();
      return successful;
    } catch (e) {
      textArea.remove();
      return false;
    }
  };

  const socket = new BroadcastSocket(Config.wsUrl, {
    onSubtitle: (data) => ui.handleSubtitleEvent(data),
    onTranslation: (data) => ui.handleTranslationEvent(data),
    onAudioLevel: (data) => {
      const rmsDb = data.rms_db !== undefined ? data.rms_db : (20 * Math.log10(Math.max(data.rms || 1e-5, 1e-5)));
      const peakDb = data.peak_db !== undefined ? data.peak_db : (20 * Math.log10(Math.max(data.peak || 1e-5, 1e-5)));
      ui.updateAudioMeter(rmsDb, peakDb);
    },
    onPanic: () => {
      ui.showToast("Layar subtitle telah dikosongkan");
      ui.handleSubtitleEvent({ is_panic: true });
    },
    onFreeze: (data) => ui.setFrozenUI(data.frozen !== undefined ? data.frozen : data.is_frozen)
  });

  socket.connect();

  if (ui.toggleEngineBtn) {
    ui.toggleEngineBtn.addEventListener("click", async () => {
      const nextState = !ui.isEngineRunning;
      try {
        const res = await api.toggleEngine(nextState);
        if (nextState && res && res.success === false) {
          ui.showToast("Gagal memulai siaran subtitle");
          return;
        }
        ui.setEngineRunningUI(nextState);
        ui.showToast(nextState ? "Siaran subtitle dimulai" : "Siaran subtitle dihentikan");
      } catch (err) {
        ui.showToast("Gagal mengubah status siaran");
      }
    });
  }

  if (ui.panicClearBtn) {
    ui.panicClearBtn.addEventListener("click", async () => {
      try {
        await api.panicClear();
        ui.showToast("Layar subtitle telah dikosongkan");
      } catch (err) {
        ui.showToast("Gagal mengosongkan layar");
      }
    });
  }

  if (ui.freezeToggleBtn) {
    ui.freezeToggleBtn.addEventListener("click", async () => {
      const nextState = !ui.isFrozen;
      try {
        await api.toggleFreeze(nextState);
        ui.setFrozenUI(nextState);
      } catch (err) {
        ui.showToast("Gagal mengubah status penahanan teks");
      }
    });
  }

  if (ui.copyObsBtn) {
    ui.copyObsBtn.innerHTML = `${Icons.copy} <span>Salin Tautan OBS</span>`;
    ui.copyObsBtn.addEventListener("click", async () => {
      const isFile = window.location.protocol === "file:" || !window.location.host;
      const host = isFile ? "127.0.0.1:8765" : window.location.host;
      const proto = window.location.protocol === "https:" ? "https:" : "http:";
      const url = `${proto}//${host}/overlay`;
      const ok = await copyToClipboard(url);
      if (ok) {
        ui.showToast("Tautan overlay OBS tersalin");
      } else {
        ui.showToast(`Overlay OBS: ${url}`);
      }
    });
  }

  if (ui.copyVmixBtn) {
    ui.copyVmixBtn.innerHTML = `${Icons.fileText} <span>Salin Jalur vMix</span>`;
    ui.copyVmixBtn.addEventListener("click", async () => {
      try {
        const status = await api.getStatus();
        const path = status.vmix_file_path || "output/current_subtitle.txt";
        const ok = await copyToClipboard(path);
        if (ok) {
          ui.showToast("Jalur berkas vMix tersalin");
        } else {
          ui.showToast(`Jalur vMix: ${path}`);
        }
      } catch (err) {
        const fallbackPath = "output/current_subtitle.txt";
        await copyToClipboard(fallbackPath);
        ui.showToast("Jalur berkas vMix tersalin");
      }
    });
  }

  if (ui.audioDeviceSelect) {
    ui.audioDeviceSelect.addEventListener("change", async (e) => {
      const devIndex = e.target.value;
      try {
        await api.setDevice(devIndex);
        const selectedText = e.target.options[e.target.selectedIndex].text;
        if (ui.activeDeviceName) ui.activeDeviceName.textContent = selectedText;
        ui.showToast(`Audio beralih ke: ${selectedText}`);
      } catch (err) {
        ui.showToast("Gagal mengalihkan perangkat audio");
      }
    });
  }

  const presetPills = document.querySelectorAll(".btn-preset-pill");
  presetPills.forEach((pill) => {
    pill.addEventListener("click", async () => {
      const preset = pill.getAttribute("data-preset");
      presetPills.forEach((p) => p.classList.remove("active"));
      pill.classList.add("active");

      try {
        await api.setPreset(preset);
        if (ui.previewCard) {
          ui.previewCard.className = `preview-subtitle-card preset-${preset.replace(/_/g, "-")}`;
        }
        ui.showToast(`Preset: ${preset.replace(/_/g, " ")}`);
      } catch (err) {
        ui.showToast("Gagal mengubah preset");
      }
    });
  });

  const posPills = document.querySelectorAll(".btn-pos-pill");
  posPills.forEach((pill) => {
    pill.addEventListener("click", async () => {
      const pos = pill.getAttribute("data-pos");
      posPills.forEach((p) => p.classList.remove("active"));
      pill.classList.add("active");

      try {
        await api.setPosition(pos);
        ui.showToast(`Posisi subtitle: ${pos}`);
      } catch (err) {
        ui.showToast("Gagal mengubah posisi subtitle");
      }
    });
  });

  if (ui.translationToggle) {
    ui.translationToggle.addEventListener("change", async (e) => {
      const enabled = e.target.checked;
      try {
        await api.setTranslation({ enabled });
        ui.showToast(enabled ? "Terjemahan Indonesia Aktif" : "Terjemahan Indonesia Nonaktif");
      } catch (err) {
        ui.showToast("Gagal mengubah saklar terjemahan");
      }
    });
  }

  const transPosPills = document.querySelectorAll(".btn-trans-pos-pill");
  transPosPills.forEach((pill) => {
    pill.addEventListener("click", async () => {
      const pos = pill.getAttribute("data-pos");
      transPosPills.forEach((p) => p.classList.remove("active"));
      pill.classList.add("active");

      try {
        await api.setTranslation({ position: pos });
        ui.showToast(`Posisi kotak terjemahan: ${pos}`);
      } catch (err) {
        ui.showToast("Gagal mengubah posisi terjemahan");
      }
    });
  });

  const hotwordInput = document.getElementById("hotword-input");
  const hotwordCat = document.getElementById("hotword-category-select");
  const addHotwordBtn = document.getElementById("add-hotword-btn");

  const submitHotword = () => {
    if (!hotwordInput) return;
    const term = hotwordInput.value;
    const cat = hotwordCat ? hotwordCat.value : "academic";
    if (term.trim()) {
      vocab.add(term, cat);
      hotwordInput.value = "";
    }
  };

  if (addHotwordBtn) {
    addHotwordBtn.addEventListener("click", submitHotword);
  }
  if (hotwordInput) {
    hotwordInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") submitHotword();
    });
  }

  if (ui.drawerToggle && ui.drawerBody) {
    ui.drawerToggle.addEventListener("click", () => {
      const isExpanded = ui.drawerBody.style.display === "block";
      ui.drawerBody.style.display = isExpanded ? "none" : "block";
      if (ui.drawerChevron) {
        ui.drawerChevron.style.transform = isExpanded ? "rotate(0deg)" : "rotate(180deg)";
      }
    });
  }

  let styleDebounceTimer = null;
  const syncSliders = () => {
    const fontSize = ui.sliderFontSize ? Number(ui.sliderFontSize.value) : 42;
    const bgOpacity = ui.sliderBgOpacity ? Number(ui.sliderBgOpacity.value) : 75;
    const borderRadius = ui.sliderRadius ? Number(ui.sliderRadius.value) : 32;
    const strokeWidth = ui.sliderStroke ? Number(ui.sliderStroke.value) : 2.5;

    if (ui.sliderSizeVal) ui.sliderSizeVal.textContent = `${fontSize}px`;
    if (ui.sliderOpacityVal) ui.sliderOpacityVal.textContent = `${bgOpacity}%`;
    if (ui.sliderRadiusVal) ui.sliderRadiusVal.textContent = `${borderRadius}px`;
    if (ui.sliderStrokeVal) ui.sliderStrokeVal.textContent = `${strokeWidth}px`;

    ui.applyLiveStyles({ fontSize, bgOpacity, borderRadius, strokeWidth });

    if (styleDebounceTimer) clearTimeout(styleDebounceTimer);
    styleDebounceTimer = setTimeout(() => {
      api.setStyle({
        font_size: fontSize,
        bg_opacity: bgOpacity / 100,
        border_radius: borderRadius,
        stroke_width: strokeWidth
      }).catch(() => {});
    }, 250);
  };

  if (ui.sliderFontSize) ui.sliderFontSize.addEventListener("input", syncSliders);
  if (ui.sliderBgOpacity) ui.sliderBgOpacity.addEventListener("input", syncSliders);
  if (ui.sliderRadius) ui.sliderRadius.addEventListener("input", syncSliders);
  if (ui.sliderStroke) ui.sliderStroke.addEventListener("input", syncSliders);

  document.addEventListener("keydown", (e) => {
    const activeTag = document.activeElement ? document.activeElement.tagName.toLowerCase() : "";
    if (activeTag === "input" || activeTag === "textarea" || activeTag === "select") {
      return;
    }

    if (e.key === "Escape") {
      e.preventDefault();
      if (vocab.isModalOpen()) {
        vocab.closeModal();
      } else {
        api.panicClear().catch(() => {});
        ui.showToast("Layar subtitle telah dikosongkan");
      }
    } else if (e.code === "Space") {
      e.preventDefault();
      const nextFrozen = !ui.isFrozen;
      api.toggleFreeze(nextFrozen).then(() => {
        ui.setFrozenUI(nextFrozen);
      }).catch(() => {});
    }
  });

  ui.populateDevices();
  vocab.load();

  api.getStatus().then((status) => {
    ui.setEngineRunningUI(status.is_running || status.status === "LIVE");
    ui.setFrozenUI(status.is_frozen);
    if (status.active_preset) {
      presetPills.forEach((p) => {
        if (p.getAttribute("data-preset") === status.active_preset) {
          presetPills.forEach((pill) => pill.classList.remove("active"));
          p.classList.add("active");
        }
      });
    }
    if (status.overlay_style) {
      if (ui.translationToggle && status.overlay_style.translation_enabled !== undefined) {
        ui.translationToggle.checked = Boolean(status.overlay_style.translation_enabled);
      }
      if (status.overlay_style.translation_position) {
        transPosPills.forEach((p) => {
          if (p.getAttribute("data-pos") === status.overlay_style.translation_position) {
            transPosPills.forEach((pill) => pill.classList.remove("active"));
            p.classList.add("active");
          }
        });
      }
    }
  }).catch(() => {});
});
