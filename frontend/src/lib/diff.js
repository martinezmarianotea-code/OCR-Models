// Diferencia palabra por palabra entre el texto de un motor y la referencia.
// Devuelve tokens { type: "same" | "extra" | "missing", text, br } donde br
// indica que en el texto del motor había un salto de línea después de la palabra.

function tokenize(text) {
  const tokens = [];
  for (const match of text.matchAll(/(\S+)(\s*)/g)) {
    tokens.push({ text: match[1], br: match[2].includes("\n") });
  }
  return tokens;
}

const key = (word) => word.normalize("NFC").toLowerCase();

export function wordDiff(hypothesis, reference) {
  const a = tokenize(hypothesis);
  const b = tokenize(reference);

  // Tabla LCS desde el final para reconstruir el camino hacia adelante.
  const lcs = Array.from({ length: a.length + 1 }, () => new Uint16Array(b.length + 1));
  for (let i = a.length - 1; i >= 0; i--) {
    for (let j = b.length - 1; j >= 0; j--) {
      lcs[i][j] = key(a[i].text) === key(b[j].text) ? lcs[i + 1][j + 1] + 1 : Math.max(lcs[i + 1][j], lcs[i][j + 1]);
    }
  }

  const out = [];
  let i = 0;
  let j = 0;
  while (i < a.length && j < b.length) {
    if (key(a[i].text) === key(b[j].text)) {
      out.push({ type: "same", ...a[i] });
      i++;
      j++;
    } else if (lcs[i + 1][j] >= lcs[i][j + 1]) {
      out.push({ type: "extra", ...a[i++] });
    } else {
      out.push({ type: "missing", text: b[j++].text, br: false });
    }
  }
  while (i < a.length) out.push({ type: "extra", ...a[i++] });
  while (j < b.length) out.push({ type: "missing", text: b[j++].text, br: false });
  return out;
}
