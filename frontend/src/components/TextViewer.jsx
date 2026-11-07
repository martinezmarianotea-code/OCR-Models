import { useState } from "react";
import { wordDiff } from "../lib/diff";

export default function TextViewer({ response }) {
  const ok = response.results.filter((r) => !r.error);
  const [active, setActive] = useState(ok[0]?.engine);
  const [showDiff, setShowDiff] = useState(true);

  const current = ok.find((r) => r.engine === active) ?? ok[0];
  const reference = response.reference;
  const segments = current && reference ? wordDiff(current.text, reference) : null;

  if (!current) return null;

  return (
    <section>
      <div className="viewer-head">
        <h2>Texto extraído</h2>
        <div className="tabs" role="tablist">
          {ok.map((r) => (
            <button
              key={r.engine}
              role="tab"
              aria-selected={r.engine === current.engine}
              onClick={() => setActive(r.engine)}
            >
              {r.label}
            </button>
          ))}
        </div>
      </div>

      {segments && (
        <label className="toggle">
          <input type="checkbox" checked={showDiff} onChange={(e) => setShowDiff(e.target.checked)} />
          Marcar diferencias con la referencia
        </label>
      )}

      {segments && showDiff ? (
        <>
          <p className="text-out diff">
            {segments.map((s, i) => (
              <span key={i}>
                <span className={s.type}>{s.text}</span>
                {s.br ? "\n" : " "}
              </span>
            ))}
          </p>
          <p className="legend">
            <span className="extra">sobra o está mal</span>
            <span className="missing">falta</span>
          </p>
        </>
      ) : (
        <pre className="text-out">{current.text || "(sin texto)"}</pre>
      )}
    </section>
  );
}
