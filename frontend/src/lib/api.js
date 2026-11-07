async function request(path, options) {
  const res = await fetch(path, options);
  if (!res.ok) {
    let detail = `Error ${res.status}`;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {
      /* respuesta sin JSON */
    }
    throw new Error(detail);
  }
  return res.status === 204 ? null : res.json();
}

export const getEngines = () => request("/api/engines");
export const getHistory = () => request("/api/history");
export const clearHistory = () => request("/api/history", { method: "DELETE" });

export function processDocument({ file, engines, reference }) {
  const form = new FormData();
  form.append("engines", engines.join(","));
  if (!file) return request("/api/sample/process", { method: "POST", body: form });
  form.append("file", file);
  if (reference.trim()) form.append("reference", reference);
  return request("/api/process", { method: "POST", body: form });
}
