export default function EngineList({ engines, selected, onChange, disabled }) {
  function toggle(key) {
    onChange(selected.includes(key) ? selected.filter((k) => k !== key) : [...selected, key]);
  }

  return (
    <ul className="engines">
      {Object.entries(engines).map(([key, engine]) => {
        const unavailable = !engine.available;
        return (
          <li key={key}>
            <label className={unavailable ? "is-disabled" : ""}>
              <input
                type="checkbox"
                checked={selected.includes(key)}
                onChange={() => toggle(key)}
                disabled={disabled || unavailable}
              />
              <span>
                <span className="engine-name">
                  {engine.label}
                  {engine.uses_network && <span className="tag">usa internet</span>}
                </span>
                <span className="engine-desc">
                  {unavailable && key === "gemini" ? "Agrega GEMINI_API_KEY al archivo .env para activarlo." : engine.description}
                </span>
              </span>
            </label>
          </li>
        );
      })}
    </ul>
  );
}
