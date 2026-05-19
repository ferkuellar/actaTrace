import { FileCheck2, Search, ShieldCheck } from "lucide-react";

export function HeroSection() {
  return (
    <section className="act-hero">
      <div className="act-hero-shell">
        <div className="act-hero-copy">
          <p className="act-eyebrow">
            ActaTrace verificacion ciudadana
          </p>
          <h1 className="act-hero-title">
            Verifica evidencia electoral con registros trazables
          </h1>
          <p className="act-hero-subtitle">
            Consulta casillas, revisa actas publicas y confirma si los resultados
            coinciden con evidencia verificable.
          </p>
          <div className="act-proof-grid">
            {[
              { icon: Search, label: "Busca casillas publicas" },
              { icon: FileCheck2, label: "Revisa huellas documentales" },
              { icon: ShieldCheck, label: "Consulta trazabilidad publica" },
            ].map((item) => (
              <div
                key={item.label}
                className="act-proof-pill"
              >
                <item.icon className="act-proof-icon" aria-hidden="true" />
                <span>{item.label}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="act-principle-card">
          <p className="act-principle-label">
            Principio publico
          </p>
          <p className="act-principle-title">
            ActaTrace no cuenta votos. Verifica si la evidencia registrada se
            mantiene consistente.
          </p>
          <div className="act-principle-list">
            <p>1. Conserva la direccion oficial como evidencia.</p>
            <p>2. Marca coordenadas como dato operativo derivado.</p>
            <p>3. Muestra pruebas publicas sin exponer datos internos.</p>
          </div>
        </div>
      </div>
    </section>
  );
}
