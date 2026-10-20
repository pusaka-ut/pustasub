(function () {
  const rootElement = document.getElementById("overlay-root") || document.body;
  const cardElement = document.getElementById("subtitle-card");
  const textElement = document.getElementById("subtitle-text");
  const glossaryElement = document.getElementById("subtitle-glossary");

  const speakerBadge = document.getElementById("speaker-badge-pill");
  const speakerName = document.getElementById("speaker-badge-name");
  const speakerTitle = document.getElementById("speaker-badge-title");
  const speakerSep = document.getElementById("speaker-badge-separator");

  const translationCard = document.getElementById("floating-translation-card");
  const translationText = document.getElementById("translation-text");

  let socket = null;
  let reconnectAttempts = 0;
  let reconnectTimer = null;
  let silenceTimer = null;
  let translationSilenceTimer = null;
  let isFrozen = false;
  let currentPresetId = "academic_formal";
  let silenceFadeMs = 3500;
  let karaokeGlowEnabled = true;
  let translationEnabled = false;
  let translationPosition = "bottom-right";

  function hexToRgba(hex, opacity) {
    let cleanHex = hex.replace("#", "");
    if (cleanHex.length === 3) {
      cleanHex = cleanHex.split("").map(function (c) { return c + c; }).join("");
    }
    const r = parseInt(cleanHex.substring(0, 2), 16) || 27;
    const g = parseInt(cleanHex.substring(2, 4), 16) || 18;
    const b = parseInt(cleanHex.substring(4, 6), 16) || 56;
    return "rgba(" + r + ", " + g + ", " + b + ", " + opacity + ")";
  }

  function applyPosition(pos, offsetX, offsetY) {
    if (!rootElement) return;
    const validPositions = ["bottom", "top", "center", "left", "right"];
    const targetPos = validPositions.indexOf(pos) !== -1 ? pos : "bottom";
    rootElement.className = "overlay-container position-" + targetPos;

    if (offsetY !== undefined && offsetY !== null) {
      if (targetPos === "top") {
        rootElement.style.paddingTop = offsetY + "px";
        rootElement.style.paddingBottom = "0px";
      } else if (targetPos === "bottom" || targetPos === "left" || targetPos === "right") {
        rootElement.style.paddingBottom = offsetY + "px";
        rootElement.style.paddingTop = "0px";
      }
    }
    if (offsetX !== undefined && offsetX !== null) {
      if (targetPos === "left") {
        rootElement.style.paddingLeft = offsetX + "px";
        rootElement.style.paddingRight = "0px";
      } else if (targetPos === "right") {
        rootElement.style.paddingRight = offsetX + "px";
        rootElement.style.paddingLeft = "0px";
      }
    }
  }

  function applyTranslationPosition(pos, offsetX, offsetY) {
    if (!translationCard) return;
    translationPosition = pos || "bottom-right";
    const valid = ["bottom-right", "top-right", "below-en", "floating"];
    const target = valid.indexOf(translationPosition) !== -1 ? translationPosition : "bottom-right";
    translationCard.className = "floating-translation-card pos-" + target;

    if (target === "floating") {
      if (offsetY !== undefined && offsetY !== null) translationCard.style.bottom = offsetY + "px";
      if (offsetX !== undefined && offsetX !== null) translationCard.style.right = offsetX + "px";
    }
  }

  function updateSpeakerBadge(badgeData) {
    if (!speakerBadge) return;
    if (!badgeData || !badgeData.enabled) {
      speakerBadge.style.display = "none";
      speakerBadge.classList.remove("visible");
      return;
    }
    const name = (badgeData.name || "").trim();
    const title = (badgeData.title || "").trim();
    if (!name && !title) {
      speakerBadge.style.display = "none";
      speakerBadge.classList.remove("visible");
      return;
    }
    if (speakerName) speakerName.textContent = name;
    if (speakerTitle) speakerTitle.textContent = title;
    if (speakerSep) speakerSep.style.display = (name && title) ? "inline" : "none";
    speakerBadge.style.display = "inline-flex";
    speakerBadge.classList.add("visible");
  }

  function applyPresetStyle(presetId, style) {
    if (!cardElement || !textElement) return;

    if (presetId) {
      const basePresetId = presetId.replace(/_/g, "-");
      cardElement.className = "subtitle-card preset-" + basePresetId;
      currentPresetId = presetId;
    }

    if (!style) return;

    if (style.font_family) {
      textElement.style.fontFamily = style.font_family;
    }
    if (style.font_size_px) {
      textElement.style.fontSize = style.font_size_px + "px";
    }
    if (style.font_color) {
      const isWhite = (style.font_color || "").toLowerCase().indexOf("fff") !== -1;
      textElement.style.color = isWhite ? "#FFFDF0" : style.font_color;
    }
    if (style.stroke_color && style.stroke_width_px !== undefined) {
      textElement.style.webkitTextStroke = style.stroke_width_px + "px " + style.stroke_color;
    }
    if (style.border_radius_px !== undefined) {
      cardElement.style.borderRadius = style.border_radius_px + "px";
    }
    if (style.background_color && style.background_opacity !== undefined) {
      if (style.background_color === "transparent" || style.background_opacity === 0) {
        cardElement.style.backgroundColor = "transparent";
      } else {
        cardElement.style.backgroundColor = hexToRgba(style.background_color, style.background_opacity);
      }
    }
    if (style.animation_fade_ms) {
      silenceFadeMs = style.animation_fade_ms > 1000 ? style.animation_fade_ms : 3500;
    }
    if (style.karaoke_glow !== undefined) {
      karaokeGlowEnabled = Boolean(style.karaoke_glow);
    }
    if (style.position) {
      applyPosition(style.position, style.offset_x, style.offset_y);
    }
    if (style.translation_enabled !== undefined) {
      translationEnabled = Boolean(style.translation_enabled);
      if (!translationEnabled && translationCard) {
        translationCard.style.display = "none";
        translationCard.classList.remove("visible");
      }
    }
    if (style.translation_position) {
      applyTranslationPosition(style.translation_position, style.translation_offset_x, style.translation_offset_y);
    }
    if (style.translation_font_size_px && translationText) {
      translationText.style.fontSize = style.translation_font_size_px + "px";
    }
  }

  function scheduleSilenceFade() {
    clearTimeout(silenceTimer);
    if (isFrozen) return;

    silenceTimer = setTimeout(function () {
      if (!isFrozen && cardElement) {
        cardElement.classList.remove("visible");
        setTimeout(function () {
          if (!cardElement.classList.contains("visible") && textElement) {
            textElement.textContent = "";
            if (glossaryElement) {
              glossaryElement.textContent = "";
              glossaryElement.style.display = "none";
            }
          }
        }, 250);
      }
    }, silenceFadeMs);
  }

  function scheduleTranslationFade() {
    clearTimeout(translationSilenceTimer);
    if (isFrozen) return;

    translationSilenceTimer = setTimeout(function () {
      if (!isFrozen && translationCard) {
        translationCard.classList.remove("visible");
        setTimeout(function () {
          if (!translationCard.classList.contains("visible") && translationText) {
            translationText.textContent = "";
            translationCard.style.display = "none";
          }
        }, 250);
      }
    }, silenceFadeMs + 1000);
  }

  function displaySubtitle(text, isPartial, glossaryTag, badgeData) {
    if (!cardElement || !textElement || isFrozen) return;

    const trimmed = text ? text.trim() : "";
    if (!trimmed) return;

    if (badgeData !== undefined) {
      updateSpeakerBadge(badgeData);
    }

    cardElement.classList.remove("panic-wipe");
    cardElement.classList.add("visible");

    if (isPartial) {
      if (karaokeGlowEnabled) {
        const words = trimmed.split(/\s+/);
        if (words.length > 1) {
          const leader = words.slice(0, -1).join(" ");
          const latestWord = words[words.length - 1];
          textElement.innerHTML = leader + ' <span class="karaoke-word-glow">' + latestWord + "</span>";
        } else {
          textElement.innerHTML = '<span class="karaoke-word-glow">' + trimmed + "</span>";
        }
      } else {
        textElement.innerHTML = '<span class="partial-pulse">' + trimmed + "</span>";
      }
    } else {
      textElement.textContent = trimmed;
    }

    if (glossaryElement) {
      if (glossaryTag) {
        glossaryElement.textContent = glossaryTag;
        glossaryElement.style.display = "inline-block";
      } else {
        glossaryElement.textContent = "";
        glossaryElement.style.display = "none";
      }
    }

    scheduleSilenceFade();
  }

  function displayTranslation(indonesian, english) {
    if (!translationCard || !translationText || isFrozen) return;
    if (!translationEnabled) return;
    const trimmed = indonesian ? indonesian.trim() : "";
    if (!trimmed) return;

    translationText.textContent = trimmed;
    translationCard.style.display = "flex";
    translationCard.classList.remove("panic-wipe");
    translationCard.classList.add("visible");
    scheduleTranslationFade();
  }

  function executePanicWipe() {
    clearTimeout(silenceTimer);
    clearTimeout(translationSilenceTimer);
    if (cardElement) {
      cardElement.classList.remove("visible");
      cardElement.classList.add("panic-wipe");
    }
    if (textElement) textElement.textContent = "";
    if (glossaryElement) {
      glossaryElement.textContent = "";
      glossaryElement.style.display = "none";
    }
    if (speakerBadge) {
      speakerBadge.classList.remove("visible");
      speakerBadge.style.display = "none";
    }
    if (translationCard) {
      translationCard.classList.remove("visible");
      translationCard.classList.add("panic-wipe");
      translationCard.style.display = "none";
    }
    if (translationText) translationText.textContent = "";
  }

  function initInitialState() {
    fetch("/api/status")
      .then(function (res) {
        return res.json();
      })
      .then(function (data) {
        if (!data) return;
        isFrozen = Boolean(data.is_frozen);

        if (data.overlay_style) {
          applyPresetStyle(data.active_preset, data.overlay_style);
          if (data.overlay_style.translation_enabled !== undefined) {
            translationEnabled = Boolean(data.overlay_style.translation_enabled);
          }
          if (data.overlay_style.translation_position) {
            applyTranslationPosition(data.overlay_style.translation_position, data.overlay_style.translation_offset_x, data.overlay_style.translation_offset_y);
          }
          if (data.overlay_style.speaker_badge_enabled) {
            updateSpeakerBadge({
              name: data.overlay_style.speaker_name,
              title: data.overlay_style.speaker_title,
              enabled: data.overlay_style.speaker_badge_enabled
            });
          }
        } else if (data.active_preset) {
          applyPresetStyle(data.active_preset, data.preset_style);
        }
      })
      .catch(function () {
        applyPresetStyle("academic_formal", null);
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
            isFrozen = Boolean(data.is_frozen);
            if (data.overlay_style) {
              applyPresetStyle(data.active_preset, data.overlay_style);
              if (data.overlay_style.translation_enabled !== undefined) {
                translationEnabled = Boolean(data.overlay_style.translation_enabled);
              }
              if (data.overlay_style.translation_position) {
                applyTranslationPosition(data.overlay_style.translation_position, data.overlay_style.translation_offset_x, data.overlay_style.translation_offset_y);
              }
              if (data.overlay_style.speaker_badge_enabled) {
                updateSpeakerBadge({
                  name: data.overlay_style.speaker_name,
                  title: data.overlay_style.speaker_title,
                  enabled: data.overlay_style.speaker_badge_enabled
                });
              }
            } else if (data.active_preset) {
              applyPresetStyle(data.active_preset, data.style);
            }
            break;
          case "partial_subtitle":
            displaySubtitle(data.text, true, data.glossary_tag, data.speaker_badge);
            break;
          case "final_subtitle":
            displaySubtitle(data.text, false, data.glossary_tag, data.speaker_badge);
            break;
          case "switch_translation":
            if (data.enabled !== undefined) {
              translationEnabled = Boolean(data.enabled);
            }
            if (data.position) {
              applyTranslationPosition(data.position, data.offset_x, data.offset_y);
            }
            if (!translationEnabled && translationCard) {
              translationCard.style.display = "none";
              translationCard.classList.remove("visible");
            }
            break;
          case "translation_sentence":
            if (data.enabled !== undefined) {
              translationEnabled = Boolean(data.enabled);
            }
            if (data.position) {
              applyTranslationPosition(data.position, data.offset_x, data.offset_y);
            }
            displayTranslation(data.indonesian || data.text, data.english);
            break;
          case "panic_clear":
            executePanicWipe();
            break;
          case "freeze_subtitle":
            isFrozen = Boolean(data.is_frozen);
            if (!isFrozen) {
              scheduleSilenceFade();
            } else {
              clearTimeout(silenceTimer);
            }
            break;
          case "apply_preset":
            applyPresetStyle(data.preset_id, data.style);
            break;
          case "update_position":
            applyPosition(data.position, data.offset_x, data.offset_y);
            break;
          case "update_speaker":
            updateSpeakerBadge({
              name: data.speaker_name,
              title: data.speaker_title,
              enabled: data.speaker_badge_enabled
            });
            break;
          case "update_style":
            applyPresetStyle(currentPresetId, data.style);
            break;
          case "engine_status":
            if (data.status === "STANDBY") {
              scheduleSilenceFade();
            }
            break;
          default:
            break;
        }
      } catch (err) {
        executePanicWipe();
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
      if (socket) {
        socket.close();
      }
    };
  }

  window.addEventListener("DOMContentLoaded", function () {
    initInitialState();
    connectWebSocket();
  });
})();
