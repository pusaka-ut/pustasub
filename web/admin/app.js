(function () {
  const engineBadge = document.getElementById("engine-status-badge");
  const engineStatusLabel = document.getElementById("engine-status-label");
  const toggleEngineBtn = document.getElementById("toggle-engine-btn");
  const engineIcon = document.getElementById("engine-icon");
  const engineBtnText = document.getElementById("engine-btn-text");

  const panicClearBtn = document.getElementById("panic-clear-btn");
  const freezeToggleBtn = document.getElementById("freeze-toggle-btn");
  const freezeBtnText = document.getElementById("freeze-btn-text");

  const pacingBadge = document.getElementById("pacing-badge");
  const pacingChunkRadio = document.getElementById("pacing-chunk-radio");
  const pacingWordRadio = document.getElementById("pacing-word-radio");

  const vuNumericLabel = document.getElementById("vu-numeric-label");
  const gummyVuFill = document.getElementById("gummy-vu-fill");
  const gummyPeakPin = document.getElementById("gummy-peak-pin");
  const activeDeviceName = document.getElementById("active-device-name");
  const audioDeviceSelect = document.getElementById("audio-device-select");

  const previewWrapper = document.querySelector(".preview-viewport-wrapper");
  const previewCard = document.getElementById("preview-subtitle-card");
  const previewText = document.getElementById("preview-subtitle-text");
  const previewGlossary = document.getElementById("preview-subtitle-glossary");
  const previewSpeakerPill = document.getElementById("preview-speaker-pill");
  const previewSpeakerName = document.getElementById("preview-speaker-name");
  const previewSpeakerTitle = document.getElementById("preview-speaker-title");
  const previewSpeakerSep = document.getElementById("preview-speaker-sep");

  const presetGrid = document.querySelector(".preset-pill-grid");
  const drawerToggle = document.getElementById("drawer-toggle");
  const drawerChevron = document.getElementById("drawer-chevron");
  const drawerBody = document.getElementById("drawer-body");

  const posPills = document.querySelectorAll(".btn-pos-pill");
  const sliderOffsetY = document.getElementById("slider-offset-y");
  const sliderOffsetYVal = document.getElementById("slider-offset-y-val");
  const sliderOffsetX = document.getElementById("slider-offset-x");
  const sliderOffsetXVal = document.getElementById("slider-offset-x-val");

  const speakerNameInput = document.getElementById("speaker-name-input");
  const speakerTitleInput = document.getElementById("speaker-title-input");
  const speakerBadgeToggle = document.getElementById("speaker-badge-toggle");
  const applySpeakerBtn = document.getElementById("apply-speaker-btn");

  const bilingualModeToggle = document.getElementById("bilingual-mode-toggle");
  const karaokeGlowToggle = document.getElementById("karaoke-glow-toggle");

  const fontFamilySelect = document.getElementById("font-family-select");
  const customPresetName = document.getElementById("custom-preset-name");
  const saveCustomPresetBtn = document.getElementById("save-custom-preset-btn");

  const hotwordInput = document.getElementById("hotword-input");
  const hotwordCategorySelect = document.getElementById("hotword-category-select");
  const addHotwordBtn = document.getElementById("add-hotword-btn");
  const hotwordsContainer = document.getElementById("hotwords-chip-container");
  const vocabCountBadge = document.getElementById("vocab-count-badge");

  const sliderFontSize = document.getElementById("slider-font-size");
  const sliderSizeVal = document.getElementById("slider-size-val");
  const sliderBgOpacity = document.getElementById("slider-bg-opacity");
  const sliderOpacityVal = document.getElementById("slider-opacity-val");
  const sliderRadius = document.getElementById("slider-radius");
  const sliderRadiusVal = document.getElementById("slider-radius-val");
  const sliderStroke = document.getElementById("slider-stroke");
  const sliderStrokeVal = document.getElementById("slider-stroke-val");

  const copyObsBtn = document.getElementById("copy-obs-btn");
  const copyVmixBtn = document.getElementById("copy-vmix-btn");
  const toastHub = document.getElementById("toast-hub");

  const translationToggle = document.getElementById("translation-toggle");
  const transPosPills = document.querySelectorAll(".btn-trans-pos-pill");
  const liveTranslationFeed = document.getElementById("live-translation-feed");
  const liveTranslationContent = document.getElementById("live-translation-content");
  const liveTranslationTime = document.getElementById("live-translation-time");
  const previewTranslationBox = document.getElementById("preview-translation-box");
  const previewTranslationText = document.getElementById("preview-translation-text");

  let socket = null;
  let reconnectTimer = null;
  let reconnectAttempts = 0;
  let isEngineRunning = false;
  let isFrozen = false;
  let activePreset = "academic_formal";
  let pacingMode = "paced_chunk";
  let currentPosition = "bottom";
  let translationEnabled = false;
  let translationPosition = "bottom-right";
  let previewTranslationTimer = null;
  let peakHold = 0;

  function showToast(message) {
    if (!toastHub) return;
    const toast = document.createElement("div");
    toast.className = "candy-toast";
    toast.textContent = message;
    toastHub.appendChild(toast);
    setTimeout(function () {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 2800);
  }

  function updateEngineStatusUI(running) {
    isEngineRunning = Boolean(running);
    if (isEngineRunning) {
      if (engineBadge) engineBadge.className = "engine-status-badge live";
      if (engineStatusLabel) engineStatusLabel.textContent = "LIVE";
      if (toggleEngineBtn) toggleEngineBtn.className = "btn-candy-primary btn-master-engine is-running";
      if (engineIcon) engineIcon.innerHTML = "&block;";
      if (engineBtnText) engineBtnText.textContent = "STOP ENGINE";
    } else {
      if (engineBadge) engineBadge.className = "engine-status-badge standby";
      if (engineStatusLabel) engineStatusLabel.textContent = "STANDBY";
      if (toggleEngineBtn) toggleEngineBtn.className = "btn-candy-primary btn-master-engine";
      if (engineIcon) engineIcon.innerHTML = "&blacktriangleright;";
      if (engineBtnText) engineBtnText.textContent = "START ENGINE";
    }
  }

  function updateFreezeUI(frozen) {
    isFrozen = Boolean(frozen);
    if (freezeToggleBtn) {
      if (isFrozen) {
        freezeToggleBtn.classList.add("is-frozen");
        if (freezeBtnText) freezeBtnText.textContent = "FROZEN";
      } else {
        freezeToggleBtn.classList.remove("is-frozen");
        if (freezeBtnText) freezeBtnText.textContent = "FREEZE";
      }
    }
  }

  function updatePacingUI(mode) {
    pacingMode = mode;
    if (pacingBadge) {
      pacingBadge.textContent = mode === "word_flow" ? "WORD FLOW" : "PACED CHUNK";
    }
    if (pacingChunkRadio && pacingWordRadio) {
      if (mode === "word_flow") {
        pacingWordRadio.checked = true;
      } else {
        pacingChunkRadio.checked = true;
      }
    }
  }

  function updatePositionUI(pos, offsetY, offsetX) {
    currentPosition = pos || "bottom";
    if (previewWrapper) {
      previewWrapper.className = "preview-viewport-wrapper position-" + currentPosition;
    }
    posPills.forEach(function (btn) {
      if (btn.getAttribute("data-position") === currentPosition) {
        btn.classList.add("active");
      } else {
        btn.classList.remove("active");
      }
    });
    if (offsetY !== undefined && offsetY !== null) {
      if (sliderOffsetY) sliderOffsetY.value = offsetY;
      if (sliderOffsetYVal) sliderOffsetYVal.textContent = offsetY + "px";
    }
    if (offsetX !== undefined && offsetX !== null) {
      if (sliderOffsetX) sliderOffsetX.value = offsetX;
      if (sliderOffsetXVal) sliderOffsetXVal.textContent = offsetX + "px";
    }
  }

  function updateSpeakerBadgeUI(name, title, enabled) {
    if (speakerNameInput) speakerNameInput.value = name || "";
    if (speakerTitleInput) speakerTitleInput.value = title || "";
    if (speakerBadgeToggle) speakerBadgeToggle.checked = Boolean(enabled);

    if (!previewSpeakerPill) return;
    if (!enabled || (!name && !title)) {
      previewSpeakerPill.style.display = "none";
      return;
    }
    if (previewSpeakerName) previewSpeakerName.textContent = name || "";
    if (previewSpeakerTitle) previewSpeakerTitle.textContent = title || "";
    if (previewSpeakerSep) previewSpeakerSep.style.display = (name && title) ? "inline" : "none";
    previewSpeakerPill.style.display = "inline-flex";
  }

  function applyPresetToPreview(presetId, style) {
    activePreset = presetId;
    const allPresetBtns = document.querySelectorAll(".preset-pill-btn");
    allPresetBtns.forEach(function (btn) {
      if (btn.getAttribute("data-preset") === presetId) {
        btn.classList.add("active");
      } else {
        btn.classList.remove("active");
      }
    });

    if (!previewCard) return;

    const basePresetId = presetId.replace(/_/g, "-");
    previewCard.className = "preview-subtitle-card preset-" + basePresetId;

    if (!style) return;

    if (style.font_family && previewText) {
      previewText.style.fontFamily = style.font_family;
      if (fontFamilySelect) fontFamilySelect.value = style.font_family;
    }
    if (style.font_size_px && previewText) {
      previewText.style.fontSize = Math.round(style.font_size_px * 0.42) + "px";
      if (sliderFontSize) sliderFontSize.value = style.font_size_px;
      if (sliderSizeVal) sliderSizeVal.textContent = style.font_size_px + "px";
    }
    if (style.font_color && previewText) {
      const isWhite = (style.font_color || "").toLowerCase().indexOf("fff") !== -1;
      previewText.style.color = isWhite ? "#FFFDF0" : style.font_color;
    }
    if (style.stroke_color && style.stroke_width_px !== undefined && previewText) {
      const scaleStroke = Math.max(0.8, style.stroke_width_px * 0.5);
      previewText.style.webkitTextStroke = scaleStroke + "px " + style.stroke_color;
      if (sliderStroke) sliderStroke.value = style.stroke_width_px;
      if (sliderStrokeVal) sliderStrokeVal.textContent = style.stroke_width_px + "px";
    }
    if (style.border_radius_px !== undefined) {
      previewCard.style.borderRadius = Math.round(style.border_radius_px * 0.65) + "px";
      if (sliderRadius) sliderRadius.value = style.border_radius_px;
      if (sliderRadiusVal) sliderRadiusVal.textContent = style.border_radius_px + "px";
    }
    if (style.background_opacity !== undefined) {
      const pct = Math.round(style.background_opacity * 100);
      if (sliderBgOpacity) sliderBgOpacity.value = pct;
      if (sliderOpacityVal) sliderOpacityVal.textContent = pct + "%";
    }
    if (style.position) {
      updatePositionUI(style.position, style.offset_y, style.offset_x);
    }
  }

  function updateVuMeter(peak, rms) {
    if (!gummyVuFill || !gummyPeakPin || !vuNumericLabel) return;
    const clampedPeak = Math.max(0, Math.min(1, peak));
    const pct = Math.round(clampedPeak * 100);
    gummyVuFill.style.width = pct + "%";

    if (clampedPeak > peakHold) {
      peakHold = clampedPeak;
      gummyPeakPin.style.left = Math.round(peakHold * 100) + "%";
    } else {
      peakHold = Math.max(0, peakHold - 0.035);
      gummyPeakPin.style.left = Math.round(peakHold * 100) + "%";
    }

    if (clampedPeak > 0.001) {
      const db = (20 * Math.log10(clampedPeak)).toFixed(1);
      vuNumericLabel.textContent = db + " dB";
    } else {
      vuNumericLabel.textContent = "-∞ dB";
    }
  }

  function populateDevices(devices, currentDeviceIndex) {
    if (!audioDeviceSelect || !devices) return;
    audioDeviceSelect.innerHTML = "";

    const defaultOpt = document.createElement("option");
    defaultOpt.value = "-1";
    defaultOpt.textContent = "Default WASAPI Loopback (Master Output)";
    audioDeviceSelect.appendChild(defaultOpt);

    const loopbacks = devices.loopback || [];
    loopbacks.forEach(function (dev) {
      const opt = document.createElement("option");
      opt.value = dev.index;
      opt.textContent = dev.name + " [Loopback]";
      if (dev.index === currentDeviceIndex) {
        opt.selected = true;
      }
      audioDeviceSelect.appendChild(opt);
    });

    const inputs = devices.physical_input || [];
    inputs.forEach(function (dev) {
      const opt = document.createElement("option");
      opt.value = dev.index;
      opt.textContent = dev.name + " [Input]";
      if (dev.index === currentDeviceIndex) {
        opt.selected = true;
      }
      audioDeviceSelect.appendChild(opt);
    });
  }

  function fetchVocabulary() {
    fetch("/api/vocabulary")
      .then(function (res) {
        return res.json();
      })
      .then(function (data) {
        if (!hotwordsContainer) return;
        const items = Array.isArray(data) ? data : (data.items || []);
        hotwordsContainer.innerHTML = "";
        if (vocabCountBadge) {
          vocabCountBadge.textContent = items.length + " Terms";
        }
        items.forEach(function (item) {
          const chip = document.createElement("span");
          chip.className = "hotword-chip";

          const catTag = document.createElement("span");
          catTag.className = "chip-cat-tag " + (item.category || "academic");
          catTag.textContent = (item.category || "academic").toUpperCase();

          const termSpan = document.createElement("span");
          termSpan.className = "chip-term-text";
          termSpan.textContent = " " + item.term + " ";

          const removeBtn = document.createElement("button");
          removeBtn.type = "button";
          removeBtn.className = "chip-remove-btn";
          removeBtn.setAttribute("data-word", item.term);
          removeBtn.innerHTML = "&times;";
          removeBtn.title = "Hapus istilah dari database SQLite";
          removeBtn.addEventListener("click", function () {
            handleDeleteVocabulary(item.term);
          });

          chip.appendChild(catTag);
          chip.appendChild(termSpan);
          chip.appendChild(removeBtn);
          hotwordsContainer.appendChild(chip);
        });
      })
      .catch(function () {
        showToast("Gagal memuat kosakata dari SQLite");
      });
  }

  function handleDeleteVocabulary(term) {
    fetch("/api/vocabulary/" + encodeURIComponent(term), {
      method: "DELETE"
    })
      .then(function (res) {
        return res.json();
      })
      .then(function () {
        showToast("Istilah \"" + term + "\" dihapus dari SQLite");
        fetchVocabulary();
      })
      .catch(function () {
        showToast("Gagal menghapus istilah dari SQLite");
      });
  }

  function handleAddVocabulary() {
    if (!hotwordInput) return;
    const term = hotwordInput.value.trim();
    if (!term) {
      showToast("Tuliskan istilah terlebih dahulu");
      return;
    }
    const cat = hotwordCategorySelect ? hotwordCategorySelect.value : "academic";
    fetch("/api/vocabulary", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ hotword: term, category: cat })
    })
      .then(function (res) {
        return res.json();
      })
      .then(function () {
        hotwordInput.value = "";
        showToast("Istilah \"" + term + "\" ditambahkan ke SQLite (" + cat + ")");
        fetchVocabulary();
      })
      .catch(function () {
        showToast("Gagal menambahkan istilah ke SQLite");
      });
  }

  function fetchInitialStatus() {
    fetch("/api/status")
      .then(function (res) {
        return res.json();
      })
      .then(function (data) {
        if (!data) return;
        updateEngineStatusUI(data.status === "LIVE");
        updateFreezeUI(data.is_frozen);
        updatePacingUI(data.pacing_mode || "paced_chunk");

        if (data.overlay_style) {
          updatePositionUI(data.overlay_style.position, data.overlay_style.offset_y, data.overlay_style.offset_x);
          updateSpeakerBadgeUI(data.overlay_style.speaker_name, data.overlay_style.speaker_title, data.overlay_style.speaker_badge_enabled);
          if (bilingualModeToggle) bilingualModeToggle.checked = Boolean(data.overlay_style.bilingual_mode);
          if (karaokeGlowToggle) karaokeGlowToggle.checked = Boolean(data.overlay_style.karaoke_glow);
          updateTranslationUI(data.overlay_style.translation_enabled, data.overlay_style.translation_position);
        }

        if (data.active_preset && data.presets) {
          applyPresetToPreview(data.active_preset, data.presets[data.active_preset]);
        }

        if (data.active_device_name && activeDeviceName) {
          activeDeviceName.textContent = data.active_device_name;
        }

        if (data.devices) {
          populateDevices(data.devices, data.active_device_index);
        }
      })
      .catch(function () {
        showToast("Menghubungkan ke server PUSTASUB...");
      });
  }

  function connectWebSocket() {
    if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) {
      return;
    }

    const loc = window.location;
    const protocol = loc.protocol === "https:" ? "wss:" : "ws:";
    const host = loc.host || "127.0.0.1:8765";
    const wsUrl = protocol + "/" + "/" + host + "/ws";

    socket = new WebSocket(wsUrl);

    socket.onopen = function () {
      reconnectAttempts = 0;
      clearTimeout(reconnectTimer);
    };

    socket.onmessage = function (event) {
      try {
        const data = JSON.parse(event.data);
        if (!data || !data.event) return;

        switch (data.event) {
          case "init_state":
            updateEngineStatusUI(data.status === "LIVE");
            updateFreezeUI(data.is_frozen);
            if (data.overlay_style) {
              updatePositionUI(data.overlay_style.position, data.overlay_style.offset_y, data.overlay_style.offset_x);
              updateSpeakerBadgeUI(data.overlay_style.speaker_name, data.overlay_style.speaker_title, data.overlay_style.speaker_badge_enabled);
              if (bilingualModeToggle) bilingualModeToggle.checked = Boolean(data.overlay_style.bilingual_mode);
              if (karaokeGlowToggle) karaokeGlowToggle.checked = Boolean(data.overlay_style.karaoke_glow);
              updateTranslationUI(data.overlay_style.translation_enabled, data.overlay_style.translation_position);
            }
            if (data.active_preset && data.style) {
              applyPresetToPreview(data.active_preset, data.style);
            }
            break;
          case "engine_status":
            updateEngineStatusUI(data.status === "LIVE");
            break;
          case "vu_meter":
            updateVuMeter(data.peak, data.rms);
            break;
          case "partial_subtitle":
            if (previewText && !isFrozen) {
              previewText.textContent = data.text || "";
            }
            if (previewGlossary) {
              if (data.glossary_tag) {
                previewGlossary.textContent = data.glossary_tag;
                previewGlossary.style.display = "block";
              } else {
                previewGlossary.textContent = "";
                previewGlossary.style.display = "none";
              }
            }
            break;
          case "final_subtitle":
            if (previewText && !isFrozen) {
              previewText.textContent = data.text || "";
            }
            if (previewGlossary) {
              if (data.glossary_tag) {
                previewGlossary.textContent = data.glossary_tag;
                previewGlossary.style.display = "block";
              } else {
                previewGlossary.textContent = "";
                previewGlossary.style.display = "none";
              }
            }
            break;
          case "translation_sentence":
            displayTranslationSentence(data.indonesian, data.english);
            break;
          case "panic_clear":
            if (previewText) previewText.textContent = "";
            if (previewGlossary) {
              previewGlossary.textContent = "";
              previewGlossary.style.display = "none";
            }
            if (previewTranslationBox) {
              previewTranslationBox.style.display = "none";
            }
            if (previewTranslationText) {
              previewTranslationText.textContent = "";
            }
            showToast("Panic Clear Berhasil Dijalankan!");
            break;
          case "freeze_subtitle":
            updateFreezeUI(data.is_frozen);
            break;
          case "apply_preset":
            applyPresetToPreview(data.preset_id, data.style);
            break;
          case "update_position":
            updatePositionUI(data.position, data.offset_y, data.offset_x);
            break;
          case "update_speaker":
            updateSpeakerBadgeUI(data.speaker_name, data.speaker_title, data.speaker_badge_enabled);
            break;
          case "switch_bilingual":
            if (bilingualModeToggle) bilingualModeToggle.checked = Boolean(data.bilingual_mode);
            break;
          case "switch_pacing":
            updatePacingUI(data.pacing_mode);
            break;
          case "audio_failover":
            if (activeDeviceName) activeDeviceName.textContent = data.device_name;
            showToast("Failover: Terhubung ke " + data.device_name);
            break;
          default:
            break;
        }
      } catch (err) {
        showToast("Format pesan WebSocket tidak valid");
      }
    };

    socket.onclose = function () {
      socket = null;
      reconnectAttempts++;
      const delay = Math.min(1000 * Math.pow(1.5, reconnectAttempts), 5000);
      clearTimeout(reconnectTimer);
      reconnectTimer = setTimeout(connectWebSocket, delay);
    };

    socket.onerror = function () {
      if (socket) socket.close();
    };
  }

  function handleToggleEngine() {
    const endpoint = isEngineRunning ? "/api/control/stop" : "/api/control/start";
    fetch(endpoint, { method: "POST" })
      .then(function (res) {
        return res.json();
      })
      .then(function (data) {
        updateEngineStatusUI(data.status === "LIVE");
        showToast(isEngineRunning ? "Engine Siaran Aktif (LIVE)" : "Engine Dihentikan (STANDBY)");
      })
      .catch(function () {
        showToast("Gagal mengubah status Engine");
      });
  }

  function handlePanicClear() {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ event: "panic_clear" }));
    }
    fetch("/api/control/panic", { method: "POST" })
      .then(function (res) {
        return res.json();
      })
      .then(function () {
        if (previewText) previewText.textContent = "";
        if (previewGlossary) {
          previewGlossary.textContent = "";
          previewGlossary.style.display = "none";
        }
      })
      .catch(function () {
        showToast("Panic Clear Gagal Terkirim");
      });
  }

  function handleToggleFreeze() {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ event: "freeze_toggle" }));
    }
    fetch("/api/control/freeze", { method: "POST" })
      .then(function (res) {
        return res.json();
      })
      .then(function (data) {
        updateFreezeUI(data.is_frozen);
        showToast(data.is_frozen ? "Subtitle Ditahan (FROZEN)" : "Subtitle Dilepas");
      })
      .catch(function () {
        showToast("Gagal mengubah status Freeze");
      });
  }

  function handleSwitchPacing(mode) {
    fetch("/api/control/pacing", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pacing_mode: mode })
    })
      .then(function (res) {
        return res.json();
      })
      .then(function () {
        updatePacingUI(mode);
        showToast("Strategi Pacing: " + (mode === "word_flow" ? "Word Flow" : "Paced Chunk"));
      })
      .catch(function () {
        showToast("Gagal mengubah strategi pacing");
      });
  }

  function handleSwitchPreset(presetId) {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ event: "apply_preset", preset_id: presetId }));
    }
    fetch("/api/control/preset", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ preset_id: presetId })
    })
      .then(function (res) {
        return res.json();
      })
      .then(function (data) {
        if (data.style) {
          applyPresetToPreview(presetId, data.style);
        }
        showToast("Preset: " + presetId.replace(/_/g, " ").toUpperCase());
      })
      .catch(function () {
        showToast("Gagal mengganti preset");
      });
  }

  function handleSwitchPosition(pos) {
    const yVal = sliderOffsetY ? parseInt(sliderOffsetY.value, 10) : 72;
    const xVal = sliderOffsetX ? parseInt(sliderOffsetX.value, 10) : 0;
    fetch("/api/control/position", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ position: pos, offset_y: yVal, offset_x: xVal })
    })
      .then(function (res) {
        return res.json();
      })
      .then(function (data) {
        updatePositionUI(data.position, data.offset_y, data.offset_x);
        showToast("Posisi Layar: " + data.position.toUpperCase());
      })
      .catch(function () {
        showToast("Gagal memindahkan posisi layar");
      });
  }

  function handleApplySpeaker() {
    const name = speakerNameInput ? speakerNameInput.value.trim() : "";
    const title = speakerTitleInput ? speakerTitleInput.value.trim() : "";
    const enabled = speakerBadgeToggle ? speakerBadgeToggle.checked : false;

    fetch("/api/control/speaker", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ speaker_name: name, speaker_title: title, speaker_badge_enabled: enabled })
    })
      .then(function (res) {
        return res.json();
      })
      .then(function (data) {
        updateSpeakerBadgeUI(data.speaker_name, data.speaker_title, data.speaker_badge_enabled);
        showToast(enabled ? "Badge Pembicara Ditampilkan" : "Badge Pembicara Disembunyikan");
      })
      .catch(function () {
        showToast("Gagal memperbarui badge pembicara");
      });
  }

  function handleToggleBilingual() {
    const enabled = bilingualModeToggle ? bilingualModeToggle.checked : false;
    fetch("/api/control/bilingual", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ bilingual_mode: enabled })
    })
      .then(function (res) {
        return res.json();
      })
      .then(function () {
        if (previewGlossary) {
          if (enabled) {
            previewGlossary.textContent = "Pembelajaran Jarak Jauh (PJJ)";
            previewGlossary.style.display = "block";
          } else {
            previewGlossary.textContent = "";
            previewGlossary.style.display = "none";
          }
        }
        showToast(enabled ? "Mode Bilingual Glosarium UT Aktif" : "Mode Bilingual Dinonaktifkan");
      })
      .catch(function () {
        showToast("Gagal mengubah mode bilingual");
      });
  }

  function handleToggleKaraokeGlow() {
    const enabled = karaokeGlowToggle ? karaokeGlowToggle.checked : true;
    fetch("/api/control/style", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ karaoke_glow: enabled })
    })
      .then(function () {
        showToast(enabled ? "Karaoke Honey Glow Aktif" : "Karaoke Glow Dinonaktifkan");
      })
      .catch(function () {
        showToast("Gagal mengubah setting karaoke glow");
      });
  }

  function handleSaveCustomPreset() {
    if (!customPresetName) return;
    const name = customPresetName.value.trim();
    if (!name) {
      showToast("Tulis nama preset terlebih dahulu");
      return;
    }
    const cleanId = name.toLowerCase().replace(/[^a-z0-9]/g, "_");
    fetch("/api/control/preset_save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ preset_id: cleanId, action: name })
    })
      .then(function (res) {
        return res.json();
      })
      .then(function () {
        showToast("Preset Kustom \"" + name + "\" Tersimpan!");
        customPresetName.value = "";
      })
      .catch(function () {
        showToast("Gagal menyimpan preset kustom");
      });
  }

  function handleCopyObs() {
    const loc = window.location;
    const host = loc.host || "127.0.0.1:8765";
    const overlayUrl = loc.protocol + "/" + "/" + host + "/overlay";
    if (navigator.clipboard) {
      navigator.clipboard.writeText(overlayUrl).then(function () {
        showToast("URL OBS Browser Source Berhasil Disalin!");
      }).catch(function () {
        showToast("URL: " + overlayUrl);
      });
    } else {
      showToast("URL: " + overlayUrl);
    }
  }

  function handleCopyVmix() {
    const vmixPath = "output/current_subtitle.txt";
    if (navigator.clipboard) {
      navigator.clipboard.writeText(vmixPath).then(function () {
        showToast("Path File vMix Text Berhasil Disalin!");
      }).catch(function () {
        showToast("Path: " + vmixPath);
      });
    } else {
      showToast("Path: " + vmixPath);
    }
  }

  function updateTranslationUI(enabled, pos) {
    translationEnabled = Boolean(enabled);
    if (translationToggle) {
      translationToggle.checked = translationEnabled;
    }
    if (pos) {
      translationPosition = pos;
    }
    transPosPills.forEach(function (btn) {
      if (btn.getAttribute("data-trans-pos") === translationPosition) {
        btn.classList.add("active");
      } else {
        btn.classList.remove("active");
      }
    });
    if (previewTranslationBox) {
      previewTranslationBox.className = "preview-translation-box pos-" + translationPosition;
      if (!translationEnabled) {
        previewTranslationBox.style.display = "none";
      }
    }
  }

  function handleToggleTranslation() {
    const enabled = translationToggle ? translationToggle.checked : false;
    translationEnabled = enabled;
    fetch("/api/control/style", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ translation_enabled: enabled })
    })
      .then(function (res) {
        return res.json();
      })
      .then(function () {
        updateTranslationUI(enabled, translationPosition);
        showToast(enabled ? "Terjemahan Indonesia Aktif" : "Terjemahan Indonesia Dinonaktifkan");
      })
      .catch(function () {
        showToast("Gagal mengubah setting terjemahan");
      });
  }

  function handleSwitchTranslationPosition(pos) {
    translationPosition = pos;
    fetch("/api/control/style", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ translation_position: pos })
    })
      .then(function (res) {
        return res.json();
      })
      .then(function () {
        updateTranslationUI(translationEnabled, pos);
        showToast("Posisi Terjemahan: " + pos);
      })
      .catch(function () {
        showToast("Gagal mengubah posisi terjemahan");
      });
  }

  function displayTranslationSentence(indonesian, english) {
    if (!indonesian) return;
    const now = new Date();
    const timeStr = now.toTimeString().substring(0, 8);
    if (liveTranslationContent) {
      liveTranslationContent.textContent = indonesian;
      liveTranslationContent.classList.remove("live-translation-empty");
    }
    if (liveTranslationTime) {
      liveTranslationTime.textContent = timeStr;
    }
    if (translationEnabled && previewTranslationBox && previewTranslationText) {
      previewTranslationText.textContent = indonesian;
      previewTranslationBox.style.display = "flex";
      clearTimeout(previewTranslationTimer);
      previewTranslationTimer = setTimeout(function () {
        if (previewTranslationBox) {
          previewTranslationBox.style.display = "none";
        }
      }, 5500);
    }
  }

  function handleSwitchDevice() {
    if (!audioDeviceSelect) return;
    const devIndex = parseInt(audioDeviceSelect.value, 10);
    fetch("/api/control/device", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ device_index: devIndex })
    })
      .then(function (res) {
        return res.json();
      })
      .then(function (data) {
        if (data.device_name && activeDeviceName) {
          activeDeviceName.textContent = data.device_name;
        }
        showToast("Audio Ingestion: " + (data.device_name || "WASAPI"));
      })
      .catch(function () {
        showToast("Gagal beralih audio device");
      });
  }

  function handleSendStyleUpdate(styleObj) {
    fetch("/api/control/style", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(styleObj)
    }).catch(function () {
      showToast("Gagal mengirim style ke overlay");
    });
  }

  function bindEvents() {
    if (toggleEngineBtn) toggleEngineBtn.addEventListener("click", handleToggleEngine);
    if (panicClearBtn) panicClearBtn.addEventListener("click", handlePanicClear);
    if (freezeToggleBtn) freezeToggleBtn.addEventListener("click", handleToggleFreeze);

    if (pacingChunkRadio) {
      pacingChunkRadio.addEventListener("change", function () {
        if (this.checked) handleSwitchPacing("paced_chunk");
      });
    }
    if (pacingWordRadio) {
      pacingWordRadio.addEventListener("change", function () {
        if (this.checked) handleSwitchPacing("word_flow");
      });
    }

    if (audioDeviceSelect) {
      audioDeviceSelect.addEventListener("change", handleSwitchDevice);
    }

    if (translationToggle) {
      translationToggle.addEventListener("change", handleToggleTranslation);
    }

    transPosPills.forEach(function (pill) {
      pill.addEventListener("click", function () {
        const pos = this.getAttribute("data-trans-pos");
        if (pos) handleSwitchTranslationPosition(pos);
      });
    });

    const allPresetBtns = document.querySelectorAll(".preset-pill-btn");
    allPresetBtns.forEach(function (pill) {
      pill.addEventListener("click", function () {
        const id = this.getAttribute("data-preset");
        if (id) handleSwitchPreset(id);
      });
    });

    posPills.forEach(function (btn) {
      btn.addEventListener("click", function () {
        const pos = this.getAttribute("data-position");
        if (pos) handleSwitchPosition(pos);
      });
    });

    if (sliderOffsetY) {
      sliderOffsetY.addEventListener("input", function () {
        if (sliderOffsetYVal) sliderOffsetYVal.textContent = this.value + "px";
      });
      sliderOffsetY.addEventListener("change", function () {
        handleSwitchPosition(currentPosition);
      });
    }
    if (sliderOffsetX) {
      sliderOffsetX.addEventListener("input", function () {
        if (sliderOffsetXVal) sliderOffsetXVal.textContent = this.value + "px";
      });
      sliderOffsetX.addEventListener("change", function () {
        handleSwitchPosition(currentPosition);
      });
    }

    if (applySpeakerBtn) applySpeakerBtn.addEventListener("click", handleApplySpeaker);
    if (bilingualModeToggle) bilingualModeToggle.addEventListener("change", handleToggleBilingual);
    if (karaokeGlowToggle) karaokeGlowToggle.addEventListener("change", handleToggleKaraokeGlow);

    if (fontFamilySelect) {
      fontFamilySelect.addEventListener("change", function () {
        const font = this.value;
        if (previewText) previewText.style.fontFamily = font;
        fetch("/api/control/style", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ font_family: font })
        }).then(function () {
          showToast("Font diubah ke " + font.split(",")[0]);
        });
      });
    }

    if (saveCustomPresetBtn) saveCustomPresetBtn.addEventListener("click", handleSaveCustomPreset);

    if (drawerToggle && drawerBody) {
      drawerToggle.addEventListener("click", function () {
        const isCollapsed = drawerBody.classList.toggle("collapsed");
        drawerToggle.classList.toggle("collapsed", isCollapsed);
      });
    }

    if (addHotwordBtn) addHotwordBtn.addEventListener("click", handleAddVocabulary);
    if (hotwordInput) {
      hotwordInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
          e.preventDefault();
          handleAddVocabulary();
        }
      });
    }

    if (sliderFontSize) {
      sliderFontSize.addEventListener("input", function () {
        const val = this.value;
        if (sliderSizeVal) sliderSizeVal.textContent = val + "px";
        if (previewText) previewText.style.fontSize = Math.round(val * 0.42) + "px";
      });
      sliderFontSize.addEventListener("change", function () {
        handleSendStyleUpdate({ font_size_px: parseInt(this.value, 10) });
      });
    }

    if (sliderBgOpacity) {
      sliderBgOpacity.addEventListener("input", function () {
        const val = this.value;
        if (sliderOpacityVal) sliderOpacityVal.textContent = val + "%";
      });
      sliderBgOpacity.addEventListener("change", function () {
        handleSendStyleUpdate({ background_opacity: parseFloat(this.value) / 100 });
      });
    }

    if (sliderRadius) {
      sliderRadius.addEventListener("input", function () {
        const val = this.value;
        if (sliderRadiusVal) sliderRadiusVal.textContent = val + "px";
        if (previewCard) previewCard.style.borderRadius = Math.round(val * 0.65) + "px";
      });
      sliderRadius.addEventListener("change", function () {
        handleSendStyleUpdate({ border_radius_px: parseInt(this.value, 10) });
      });
    }

    if (sliderStroke) {
      sliderStroke.addEventListener("input", function () {
        const val = this.value;
        if (sliderStrokeVal) sliderStrokeVal.textContent = val + "px";
      });
      sliderStroke.addEventListener("change", function () {
        handleSendStyleUpdate({ stroke_width_px: parseFloat(this.value) });
      });
    }

    if (copyObsBtn) copyObsBtn.addEventListener("click", handleCopyObs);
    if (copyVmixBtn) copyVmixBtn.addEventListener("click", handleCopyVmix);

    window.addEventListener("keydown", function (e) {
      const activeTag = document.activeElement ? document.activeElement.tagName : "";
      if (["INPUT", "SELECT", "TEXTAREA"].indexOf(activeTag) !== -1) {
        return;
      }
      if (e.key === "Escape") {
        e.preventDefault();
        handlePanicClear();
      } else if (e.key === " " || e.code === "Space") {
        e.preventDefault();
        handleToggleFreeze();
      }
    });
  }

  window.addEventListener("DOMContentLoaded", function () {
    bindEvents();
    fetchInitialStatus();
    fetchVocabulary();
    connectWebSocket();
  });
})();
