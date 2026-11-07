import { pct, secs } from "../lib/format";

function best(results, field) {
  const values = results.filter((r) => !r.error && r[field] != null).map((r) => r[field]);
  return values.length > 1 ? Math.min(...values) : null;
}

export default function ResultsTable({ response }) {
  const { results, has_reference: scored, filename } = response;
  const bestCer = best(results, "cer");
  const bestTime = best(results, "seconds");

  return (
    <section>
      <h2>
        Resultados <span className="muted">· {filename}</span>
      </h2>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Motor</th>
              {scored && <th className="num">CER</th>}
              {scored && <th className="num">WER</th>}
              <th className="num">Tiempo</th>
              <th className="num">Caracteres</th>
            </tr>
          </thead>
          <tbody>
            {results.map((r) => (
              <tr key={r.engine}>
                <td>{r.label}</td>
                {r.error ? (
                  <td colSpan={scored ? 4 : 2} className="error-cell">{r.error}</td>
                ) : (
                  <>
                    {scored && <td className={`num ${r.cer === bestCer ? "best" : ""}`}>{pct(r.cer)}</td>}
                    {scored && <td className="num">{pct(r.wer)}</td>}
                    <td className={`num ${r.seconds === bestTime ? "best" : ""}`}>{secs(r.seconds)}</td>
                    <td className="num">{r.chars.toLocaleString("es")}</td>
                  </>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {!scored && (
        <p className="hint">Sin referencia no se puede medir el error; solo se muestran tiempo y longitud.</p>
      )}
    </section>
  );
}
