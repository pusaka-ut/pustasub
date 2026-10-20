import { Icons } from "./icons.js";

export class UiController {
  constructor(api, onToast) {
    this.api = api;
    this.onToast = onToast;
    this.isEngineRunning = false;
    this.isFrozen = false;
    this.peakHold = 0;
    this.previewTranslationTimer = null;
    this.initDOMElements();
  }

  initDOMElements() {
    this.toggleEngineBtn = document.getElementById("toggle-engine-btn");
    this.engineIcon = document.getElementById("engine-icon");
    this.engineBtnText = document.getElementById("engine-btn-text");

    this.panicClearBtn = document.getElementById("panic-clear-btn");
    this.freezeToggleBtn = document.getElementById("freeze-toggle-btn");
    this.freezeBtnText = document.getElementById("freeze-btn-text");

    this.vuNumericLabel = document.getElementById("vu-numeric-label");
    this.gummyVuFill = document.getElementById("gummy-vu-fill");
    this.gummyPeakPin = document.getElementById("gummy-peak-pin");
    this.activeDeviceName = document.getElementById("active-device-name");
    this.audioDeviceSelect = document.getElementById("audio-device-select");

    this.previewCard = document.getElementById("preview-subtitle-card");
    this.previewText = document.getElementById("preview-subtitle-text");
    this.previewGlossary = document.getElementById("preview-subtitle-glossary");
    this.previewSpeakerPill = document.getElementById("preview-speaker-pill");
    this.previewSpeakerName = document.getElementById("preview-speaker-name");
    this.previewSpeakerTitle = document.getElementById("preview-speaker-title");

    this.previewTranslationBox = document.getElementById("preview-translation-box");
    this.previewTranslationText = document.getElementById("preview-translation-text");
    this.liveTranslationContent = document.getElementById("live-translation-content");
    this.liveTranslationTime = document.getElementById("live-translation-time");
    this.translationToggle = document.getElementById("translation-toggle");

    this.drawerToggle = document.getElementById("drawer-toggle");
    this.drawerChevron = document.getElementById("drawer-chevron");
    this.drawerBody = document.getElementById("drawer-body");

    this.copyObsBtn = document.getElementById("copy-obs-btn");
    this.copyVmixBtn = document.getElementById("copy-vmix-btn");
    this.toastHub = document.getElementById("toast-hub");

    this.sliderFontSize = document.getElementById("slider-font-size");
    this.sliderSizeVal = document.getElementById("slider-size-val");
    this.sliderBgOpacity = document.getElementById("slider-bg-opacity");
    this.sliderOpacityVal = document.getElementById("slider-opacity-val");
    this.sliderRadius = document.getElementById("slider-radius");
    this.sliderRadiusVal = document.getElementById("slider-radius-val");
    this.sliderStroke = document.getElementById("slider-stroke");
    this.sliderStrokeVal = document.getElementById("slider-stroke-val");
  }

  showToast(message) {
    if (!this.toastHub) return;
    const toast = document.createElement("div");
    toast.className = "candy-toast";
    toast.textContent = message;
    this.toastHub.appendChild(toast);
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 2800);
  }

  setEngineRunningUI(running) {
    this.isEngineRunning = Boolean(running);
    if (!this.toggleEngineBtn) return;

    if (this.isEngineRunning) {
      this.toggleEngineBtn.className = "btn-candy-primary btn-master-engine is-running";
      if (this.engineIcon) this.engineIcon.innerHTML = Icons.stop;
      if (this.engineBtnText) this.engineBtnText.textContent = "Hentikan Subtitle";
    } else {
      this.toggleEngineBtn.className = "btn-candy-primary btn-master-engine";
      if (this.engineIcon) this.engineIcon.innerHTML = Icons.play;
      if (this.engineBtnText) this.engineBtnText.textContent = "Mulai Subtitle";
    }
  }

  setFrozenUI(frozen) {
    this.isFrozen = Boolean(frozen);
    if (!this.freezeToggleBtn) return;

    if (this.isFrozen) {
      this.freezeToggleBtn.classList.add("is-active");
      if (this.freezeBtnText) this.freezeBtnText.textContent = "Lanjutkan Teks";
      this.showToast("Tahan teks aktif: Subtitle ditahan di layar");
    } else {
      this.freezeToggleBtn.classList.remove("is-active");
      if (this.freezeBtnText) this.freezeBtnText.textContent = "Tahan Teks";
      this.showToast("Tahan teks dinonaktifkan: Subtitle kembali normal");
    }
  }

  updateAudioMeter(rmsDb, peakDb) {
    const minDb = -60.0;
    const maxDb = 0.0;
    const clampedRms = Math.max(minDb, Math.min(maxDb, rmsDb));
    const percent = Math.round(((clampedRms - minDb) / (maxDb - minDb)) * 100);

    if (this.gummyVuFill) {
      this.gummyVuFill.style.width = `${percent}%`;
    }

    if (peakDb > this.peakHold) {
      this.peakHold = peakDb;
    } else {
      this.peakHold = Math.max(minDb, this.peakHold - 0.7);
    }

    const peakPercent = Math.round(((Math.max(minDb, Math.min(maxDb, this.peakHold)) - minDb) / (maxDb - minDb)) * 100);
    if (this.gummyPeakPin) {
      this.gummyPeakPin.style.left = `${peakPercent}%`;
    }

    if (this.vuNumericLabel) {
      if (rmsDb <= -59.0) {
        this.vuNumericLabel.textContent = "-INF dB";
      } else {
        this.vuNumericLabel.textContent = `${rmsDb.toFixed(1)} dB`;
      }
    }
  }

  handleSubtitleEvent(data) {
    if (!this.previewCard || !this.previewText) return;

    if (data.is_panic) {
      this.previewText.textContent = "";
      this.previewCard.classList.remove("visible");
      return;
    }

    if (data.is_freeze && data.text) {
      this.previewText.textContent = data.text;
      this.previewCard.classList.add("visible");
      return;
    }

    if (data.text && data.text.trim()) {
      this.previewText.textContent = data.text;
      this.previewCard.classList.add("visible");

      if (data.glossary && this.previewGlossary) {
        this.previewGlossary.textContent = data.glossary;
        this.previewGlossary.style.display = "inline-block";
      } else if (this.previewGlossary) {
        this.previewGlossary.style.display = "none";
      }
    } else if (data.is_final) {
      setTimeout(() => {
        if (!this.isFrozen && this.previewCard) {
          this.previewCard.classList.remove("visible");
        }
      }, 4000);
    }
  }

  handleTranslationEvent(data) {
    if (!data) return;
    const text = (data.indonesian || data.text || "").trim();
    if (!text) return;

    if (this.liveTranslationContent) {
      this.liveTranslationContent.textContent = text;
    }
    if (this.liveTranslationTime) {
      const now = new Date();
      this.liveTranslationTime.textContent = now.toLocaleTimeString();
    }

    if (this.previewTranslationBox && this.previewTranslationText) {
      this.previewTranslationText.textContent = text;
      this.previewTranslationBox.classList.add("visible");

      if (this.previewTranslationTimer) {
        clearTimeout(this.previewTranslationTimer);
      }
      this.previewTranslationTimer = setTimeout(() => {
        if (this.previewTranslationBox) {
          this.previewTranslationBox.classList.remove("visible");
        }
      }, 6000);
    }
  }

  async populateDevices() {
    if (!this.audioDeviceSelect) return;
    try {
      const res = await this.api.getDevices();
      const devices = res.devices || [];
      this.audioDeviceSelect.innerHTML = "";

      const defaultOpt = document.createElement("option");
      defaultOpt.value = "-1";
      defaultOpt.textContent = "Suara Komputer (Loopback Default)";
      this.audioDeviceSelect.appendChild(defaultOpt);

      devices.forEach((dev) => {
        const opt = document.createElement("option");
        opt.value = String(dev.index);
        opt.textContent = `${dev.name}`;
        this.audioDeviceSelect.appendChild(opt);
      });

      if (res.active_device_name && this.activeDeviceName) {
        this.activeDeviceName.textContent = res.active_device_name;
      }
    } catch (err) {
      this.showToast("Gagal memuat daftar perangkat audio");
    }
  }

  applyLiveStyles(styles) {
    if (!this.previewCard) return;
    if (styles.fontSize) {
      this.previewText.style.fontSize = `${styles.fontSize}px`;
    }
    if (styles.bgOpacity !== undefined) {
      const alpha = (styles.bgOpacity / 100).toFixed(2);
      this.previewCard.style.backgroundColor = `rgba(10, 24, 60, ${alpha})`;
    }
    if (styles.borderRadius !== undefined) {
      this.previewCard.style.borderRadius = `${styles.borderRadius}px`;
    }
    if (styles.strokeWidth !== undefined) {
      this.previewText.style.webkitTextStrokeWidth = `${styles.strokeWidth}px`;
    }
  }
}
