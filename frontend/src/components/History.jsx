import { useEffect, useState } from "react";
import { clearHistory, getHistory } from "../lib/api";
import { pct, secs } from "../lib/format";

const time = (iso) => new Date(iso).toLocaleTimeString("es", { hour: "2-digit", minute: "2-digit" });

export default function History({ version }) {
  const [entries, setEntries] = useState([]);

  useEffect(() => {
    getHistory()
      .then(setEntries)
      .catch(() => setEntries([]));
  }, [version]);

  if (entries.length === 0) return null;

  async function clear() {
    await clearHistory();
    setEntries([]);
  }

  return (
    <section className="history">
      <div className="viewer-head">
        <h2>Esta sesión</h2>
        <button className="link" onClick={clear}>
          Borrar
        </button>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Hora</th>
              <th>Archivo</th>
              <th>Motor</th>
              <th className="num">CER</th>
              <th className="num">Tiempo</th>
            </tr>
          </thead>
          <tbody>
            {entries.flatMap((entry) =>
              entry.results.map((r, i) => (
                <tr key={`${entry.timestamp}-${r.engine}`} className={i === 0 ? "group-start" : ""}>
                  <td>{i === 0 ? time(entry.timestamp) : ""}</td>
                  <td className="truncate">{i === 0 ? entry.filename : ""}</td>
                  <td>{r.label}</td>
                  <td className="num">{r.error ? "error" : pct(r.cer)}</td>
                  <td className="num">{r.error ? "—" : secs(r.seconds)}</td>
                </tr>
              )),
            )}
          </tbody>
        </table>
      </div>
      <p className="hint">Solo se guardan métricas, en memoria; se pierden al reiniciar el servidor.</p>
    </section>
  );
}
