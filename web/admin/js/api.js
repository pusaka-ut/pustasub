export class ApiClient {
  constructor(baseUrl = "") {
    this.baseUrl = baseUrl;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
    const response = await fetch(url, { ...options, headers });
    if (!response.ok) {
      throw new Error(`API Error ${response.status}: ${response.statusText}`);
    }
    return response.json();
  }

  getStatus() {
    return this.request("/api/status");
  }

  toggleEngine(running) {
    return this.request("/api/control/engine", {
      method: "POST",
      body: JSON.stringify({ running })
    });
  }

  panicClear() {
    return this.request("/api/control/panic", {
      method: "POST",
      body: JSON.stringify({})
    });
  }

  toggleFreeze(frozen) {
    return this.request("/api/control/freeze", {
      method: "POST",
      body: JSON.stringify({ frozen })
    });
  }

  setPreset(preset) {
    return this.request("/api/control/preset", {
      method: "POST",
      body: JSON.stringify({ preset, preset_id: preset })
    });
  }

  setPosition(position, offsetX = null, offsetY = null) {
    const payload = { position };
    if (offsetX !== null) payload.offset_x = offsetX;
    if (offsetY !== null) payload.offset_y = offsetY;
    return this.request("/api/control/position", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  }

  setSpeaker(speakerData) {
    return this.request("/api/control/speaker", {
      method: "POST",
      body: JSON.stringify(speakerData)
    });
  }

  setBilingual(enabled) {
    return this.request("/api/control/bilingual", {
      method: "POST",
      body: JSON.stringify({ enabled, bilingual_mode: enabled })
    });
  }

  setTranslation(translationData) {
    const payload = { ...translationData };
    if (payload.enabled !== undefined && payload.translation_enabled === undefined) {
      payload.translation_enabled = payload.enabled;
    }
    if (payload.position !== undefined && payload.translation_position === undefined) {
      payload.translation_position = payload.position;
    }
    return this.request("/api/control/translation", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  }

  getDevices() {
    return this.request("/api/devices");
  }

  setDevice(deviceIndex) {
    return this.request("/api/control/device", {
      method: "POST",
      body: JSON.stringify({ device_index: Number(deviceIndex) })
    });
  }

  setStyle(styleData) {
    const payload = { ...styleData };
    if (payload.font_size !== undefined && payload.font_size_px === undefined) {
      payload.font_size_px = payload.font_size;
    }
    if (payload.bg_opacity !== undefined && payload.background_opacity === undefined) {
      payload.background_opacity = payload.bg_opacity;
    }
    if (payload.border_radius !== undefined && payload.border_radius_px === undefined) {
      payload.border_radius_px = payload.border_radius;
    }
    if (payload.stroke_width !== undefined && payload.stroke_width_px === undefined) {
      payload.stroke_width_px = payload.stroke_width;
    }
    return this.request("/api/control/style", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  }

  getVocabulary() {
    return this.request("/api/vocabulary");
  }

  addVocabulary(term, category = "academic", weight = 2.5) {
    return this.request("/api/vocabulary", {
      method: "POST",
      body: JSON.stringify({ term, category, weight, boost_score: weight })
    });
  }

  deleteVocabulary(id) {
    return this.request(`/api/vocabulary/${id}`, {
      method: "DELETE"
    });
  }
}
