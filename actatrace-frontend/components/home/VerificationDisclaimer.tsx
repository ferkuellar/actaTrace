import { Info } from "lucide-react";

export function VerificationDisclaimer() {
  return (
    <section className="act-disclaimer">
      <Info className="act-disclaimer-icon" aria-hidden="true" />
      <p>
        ActaTrace no cuenta votos ni sustituye a la autoridad electoral. Verifica
        evidencia documental, trazabilidad e integridad de registros publicos.
      </p>
    </section>
  );
}
