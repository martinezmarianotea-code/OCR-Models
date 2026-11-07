import { useEffect, useState } from "react";
import { getEngines, processDocument } from "./lib/api";
import DocumentPicker from "./components/DocumentPicker";
import EngineList from "./components/EngineList";
import ResultsTable from "./components/ResultsTable";
import TextViewer from "./components/TextViewer";
import History from "./components/History";

const REPO_URL = "https://github.com/martinezmarianotea-code/OCR-Models";

export default function App() {
  const [engines, setEngines] = useState(null);
  const [selected, setSelected] = useState(["tesseract", "layout"]);
  const [file, setFile] = useState(null); // null = receta de ejemplo
  const [reference, setReference] = useState("");
  const [response, setResponse] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [historyVersion, setHistoryVersion] = useState(0);

  useEffect(() => {
    getEngines()
      .then(setEngines)
      .catch(() => setError("No hay conexión con la API. Inicia el backend en el puerto 8000."));
  }, []);

  async function run() {
    setBusy(true);
    setError(null);
    try {
      setResponse(await processDocument({ file, engines: selected, reference }));
      setHistoryVersion((v) => v + 1);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page">
      <header className="masthead">
        <div>
          <h1>OCR-Models</h1>
          <p>Tres formas de leer una receta médica, medidas contra la transcripción correcta.</p>
        </div>
        <a href={REPO_URL} target="_blank" rel="noreferrer">Código fuente</a>
      </header>

      <div className="layout">
        <aside className="controls">
          <DocumentPicker file={file} onChange={setFile} disabled={busy} />

          <section>
            <h2>Motores</h2>
            {engines ? (
              <EngineList engines={engines} selected={selected} onChange={setSelected} disabled={busy} />
            ) : (
              !error && <p className="muted">Cargando…</p>
            )}
          </section>

          {file && (
            <section>
              <h2>
                Referencia <span className="muted">(opcional)</span>
              </h2>
              <textarea
                value={reference}
                onChange={(e) => setReference(e.target.value)}
                placeholder="Pega aquí la transcripción correcta para calcular CER y WER."
                rows={5}
                disabled={busy}
              />
            </section>
          )}

          <button className="primary" onClick={run} disabled={busy || !engines || selected.length === 0}>
            {busy ? "Procesando…" : "Comparar"}
          </button>
          {error && <p className="error" role="alert">{error}</p>}
        </aside>

        <main className="results" aria-busy={busy}>
          {response ? (
            <>
              <ResultsTable response={response} />
              <TextViewer response={response} />
            </>
          ) : (
            <Intro />
          )}
          <History version={historyVersion} />
        </main>
      </div>
    </div>
  );
}

function Intro() {
  return (
    <section className="intro">
      <h2>Cómo funciona</h2>
      <ol>
        <li>
          <strong>Tesseract</strong> lee la página completa después de limpiarla con OpenCV.
        </li>
        <li>
          <strong>Bloques + Tesseract</strong> localiza primero cada línea de texto y la lee por separado.
        </li>
        <li>
          <strong>Gemini</strong> envía la imagen a un modelo multimodal (necesita clave de API).
        </li>
      </ol>
      <p>
        Con la receta de ejemplo, que es ficticia, la app ya conoce el texto correcto y calcula el
        <abbr title="Character Error Rate: ediciones de carácter / longitud de la referencia"> CER</abbr> y el
        <abbr title="Word Error Rate: ediciones de palabra / palabras de la referencia"> WER</abbr> de cada
        motor. Pulsa <em>Comparar</em> para empezar.
      </p>
    </section>
  );
}
