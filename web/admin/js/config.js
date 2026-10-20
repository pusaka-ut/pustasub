const isFileScheme = typeof window !== "undefined" && (window.location.protocol === "file:" || !window.location.host);
const fallbackHost = "127.0.0.1:8765";
const activeHost = isFileScheme ? fallbackHost : window.location.host;
const isHttps = typeof window !== "undefined" && window.location.protocol === "https:";
const httpProto = isHttps ? "https:" : "http:";
const wsProto = isHttps ? "wss:" : "ws:";

export const Config = {
  apiBase: isFileScheme ? `${httpProto}//${fallbackHost}` : "",
  wsUrl: `${wsProto}//${activeHost}/ws`,
  defaultPreset: "academic_formal",
  defaultPosition: "bottom",
  defaultPacing: "paced_chunk",
  defaultStyles: {
    fontSize: 42,
    bgOpacity: 75,
    borderRadius: 32,
    strokeWidth: 2.5
  }
};
