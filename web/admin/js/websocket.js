export class BroadcastSocket {
  constructor(url, handlers = {}) {
    this.url = url;
    this.handlers = handlers;
    this.socket = null;
    this.reconnectTimer = null;
    this.attempts = 0;
    this.isConnected = false;
  }

  connect() {
    if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
      return;
    }

    try {
      this.socket = new WebSocket(this.url);
    } catch (e) {
      this.scheduleReconnect();
      return;
    }

    this.socket.onopen = () => {
      this.isConnected = true;
      this.attempts = 0;
      if (this.handlers.onOpen) this.handlers.onOpen();
    };

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (this.handlers.onMessage) this.handlers.onMessage(data);

        const evt = data.event || data.type;
        switch (evt) {
          case "partial_subtitle":
          case "final_subtitle":
          case "subtitle":
            if (this.handlers.onSubtitle) this.handlers.onSubtitle(data);
            break;
          case "vu_meter":
          case "audio_level":
            if (this.handlers.onAudioLevel) this.handlers.onAudioLevel(data);
            break;
          case "panic_clear":
          case "panic":
            if (this.handlers.onPanic) this.handlers.onPanic(data);
            break;
          case "freeze_subtitle":
          case "freeze":
            if (this.handlers.onFreeze) this.handlers.onFreeze(data);
            break;
          case "speaker":
          case "update_speaker":
            if (this.handlers.onSpeaker) this.handlers.onSpeaker(data);
            break;
          case "translation_sentence":
          case "translation":
            if (this.handlers.onTranslation) this.handlers.onTranslation(data);
            break;
        }
      } catch (err) {}
    };

    this.socket.onerror = () => {
      if (this.socket) this.socket.close();
    };

    this.socket.onclose = () => {
      this.isConnected = false;
      if (this.handlers.onClose) this.handlers.onClose();
      this.scheduleReconnect();
    };
  }

  scheduleReconnect() {
    if (this.reconnectTimer) return;
    this.attempts += 1;
    const delay = Math.min(1000 * Math.pow(1.5, this.attempts), 5000);
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.connect();
    }, delay);
  }

  send(data) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(typeof data === "string" ? data : JSON.stringify(data));
    }
  }

  disconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}
