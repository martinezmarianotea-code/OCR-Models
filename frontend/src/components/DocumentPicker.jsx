import { useEffect, useMemo, useRef, useState } from "react";

const ACCEPT = "image/png,image/jpeg,image/webp,image/tiff,application/pdf";

export default function DocumentPicker({ file, onChange, disabled }) {
  const input = useRef(null);
  const [dragging, setDragging] = useState(false);
  const preview = useMemo(
    () => (file && file.type !== "application/pdf" ? URL.createObjectURL(file) : null),
    [file],
  );
  useEffect(() => () => preview && URL.revokeObjectURL(preview), [preview]);

  function pick(f) {
    if (f) onChange(f);
  }

  const src = file ? preview : "/api/sample";

  return (
    <section>
      <h2>Documento</h2>
      <div
        className={`drop ${dragging ? "is-dragging" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          if (!disabled) pick(e.dataTransfer.files[0]);
        }}
      >
        {src ? <img src={src} alt="Documento seleccionado" /> : <div className="pdf-name">{file.name}</div>}
      </div>

      <p className="doc-caption">
        {file ? file.name : "Receta de ejemplo (datos ficticios)"}
      </p>

      <div className="row">
        <button type="button" onClick={() => input.current.click()} disabled={disabled}>
          Subir imagen o PDF
        </button>
        {file && (
          <button type="button" className="link" onClick={() => onChange(null)} disabled={disabled}>
            Volver al ejemplo
          </button>
        )}
      </div>
      <input
        ref={input}
        type="file"
        accept={ACCEPT}
        hidden
        onChange={(e) => {
          pick(e.target.files[0]);
          e.target.value = "";
        }}
      />
      <p className="hint">Los archivos se procesan en tu equipo y se borran al terminar, salvo si usas Gemini.</p>
    </section>
  );
}
