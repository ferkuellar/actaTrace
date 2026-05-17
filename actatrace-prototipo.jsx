
import { useState } from "react";

// ─── Mock Data ────────────────────────────────────────────────────────────────
const ACTAS = [
  {
    id: "ACT-CHH-01-0042-2024",
    casilla: "1042-B",
    municipio: "Chihuahua",
    distrito: "Distrito 01",
    seccion: "0394",
    votos_acta: 342,
    votos_prep: 342,
    hash: "a3f9c2d1e8b47f203c91a5d6e0b82f14c73da291",
    blockchain_tx: "0x8f2a3b91c44d6e7f...",
    blockchain_block: "14,291,038",
    estado: "verificado",
    timestamp_registro: "2024-06-02 20:14:33",
    timestamp_blockchain: "2024-06-02 20:15:01",
    custodios: [
      { nombre: "María Elena Torres", rol: "Presidenta de Casilla", ts: "20:10:12" },
      { nombre: "Carlos Ibáñez Ruiz", rol: "CAPTURISTA", ts: "20:14:33" },
      { nombre: "Lic. Fernanda Salas", rol: "SUPERVISORA", ts: "20:14:50" },
    ],
  },
  {
    id: "ACT-CHH-01-0087-2024",
    casilla: "1087-A",
    municipio: "Chihuahua",
    distrito: "Distrito 01",
    seccion: "0401",
    votos_acta: 289,
    votos_prep: 291,
    hash: "d72b14f9a3c08e5621b94f7c3e02da81b495c317",
    blockchain_tx: "0x3c1f8a72d90e4b52...",
    blockchain_block: "14,291,102",
    estado: "inconsistencia",
    timestamp_registro: "2024-06-02 20:31:17",
    timestamp_blockchain: "2024-06-02 20:31:44",
    custodios: [
      { nombre: "Jorge Medina Soto", rol: "Presidente de Casilla", ts: "20:28:05" },
      { nombre: "Ana Lucía Vega", rol: "CAPTURISTA", ts: "20:31:17" },
      { nombre: "Lic. Ramón Castillo", rol: "SUPERVISOR", ts: "20:32:01" },
    ],
  },
  {
    id: "ACT-CHH-02-0013-2024",
    casilla: "2013-C",
    municipio: "Juárez",
    distrito: "Distrito 02",
    seccion: "0612",
    votos_acta: 418,
    votos_prep: null,
    hash: "f81d4fae7dec11d0a765b0a50d0eb3de5b917c5e",
    blockchain_tx: null,
    blockchain_block: null,
    estado: "pendiente",
    timestamp_registro: "2024-06-02 21:02:48",
    timestamp_blockchain: null,
    custodios: [
      { nombre: "Rosa Amelia Fuentes", rol: "Presidenta de Casilla", ts: "20:59:30" },
      { nombre: "Miguel Ángel Rojo", rol: "CAPTURISTA", ts: "21:02:48" },
    ],
  },
];

const STATS = {
  actas_total: 4821,
  actas_verificadas: 4614,
  actas_pendientes: 187,
  inconsistencias: 20,
  cobertura: "95.7%",
  hashes_en_blockchain: 4614,
};

// ─── Color tokens ─────────────────────────────────────────────────────────────
const C = {
  bg: "#09090b",
  surface: "#111113",
  panel: "#18181b",
  border: "#27272a",
  primary: "#0C5CAB",
  primaryHover: "#0a4a8a",
  success: "#10b981",
  warning: "#f59e0b",
  danger: "#ef4444",
  text: "#fafafa",
  muted: "#a1a1aa",
  subtle: "#52525b",
};

// ─── Shared components ────────────────────────────────────────────────────────
const Badge = ({ estado }) => {
  const map = {
    verificado: { bg: "#10b98120", color: "#10b981", label: "✓ VERIFICADO" },
    inconsistencia: { bg: "#ef444420", color: "#ef4444", label: "⚠ INCONSISTENCIA" },
    pendiente: { bg: "#f59e0b20", color: "#f59e0b", label: "◔ PENDIENTE" },
  };
  const s = map[estado] || map.pendiente;
  return (
    <span style={{
      background: s.bg, color: s.color,
      padding: "3px 10px", borderRadius: 4,
      fontSize: 11, fontWeight: 700, letterSpacing: 0.5,
      fontFamily: "IBM Plex Mono, monospace",
    }}>{s.label}</span>
  );
};

const HashDisplay = ({ hash }) => (
  <div style={{
    background: "#000", borderRadius: 6, padding: "8px 12px",
    fontFamily: "IBM Plex Mono, monospace", fontSize: 11,
    color: "#10b981", letterSpacing: 0.5, wordBreak: "break-all",
    border: "1px solid #10b98130",
  }}>
    SHA-256: {hash}
  </div>
);

// ─── Views ────────────────────────────────────────────────────────────────────

function Landing({ setView }) {
  return (
    <div style={{
      minHeight: "100vh", background: C.bg,
      display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center",
      padding: 32, gap: 0,
      fontFamily: "IBM Plex Sans, sans-serif",
    }}>
      {/* Header */}
      <div style={{ textAlign: "center", marginBottom: 56 }}>
        <div style={{
          display: "inline-flex", alignItems: "center", gap: 10,
          marginBottom: 20,
        }}>
          <svg width="36" height="36" viewBox="0 0 36 36">
            <rect width="36" height="36" rx="8" fill={C.primary}/>
            <path d="M10 18 L18 10 L26 18 L18 26 Z" fill="none" stroke="#fff" strokeWidth="2"/>
            <circle cx="18" cy="18" r="3" fill="#fff"/>
            <line x1="18" y1="10" x2="18" y2="26" stroke="#fff" strokeWidth="1" strokeDasharray="2,2"/>
            <line x1="10" y1="18" x2="26" y2="18" stroke="#fff" strokeWidth="1" strokeDasharray="2,2"/>
          </svg>
          <span style={{ fontSize: 28, fontWeight: 800, color: C.text, letterSpacing: -0.5 }}>
            ActaTrace
          </span>
        </div>
        <p style={{ color: C.muted, fontSize: 16, maxWidth: 480, lineHeight: 1.6 }}>
          Plataforma de <strong style={{ color: C.text }}>trazabilidad y auditoría electoral</strong>.
          Cada acta, verificable. Cada resultado, con evidencia.
        </p>
      </div>

      {/* Role cards */}
      <div style={{ display: "flex", gap: 20, flexWrap: "wrap", justifyContent: "center" }}>
        <RoleCard
          icon="🏛"
          title="Portal Ciudadano"
          subtitle="Verifica resultados electorales de tu casilla"
          desc="Consulta actas, valida hashes y sigue la cadena de custodia de forma pública e independiente."
          cta="Verificar mi casilla"
          onClick={() => setView("ciudadano")}
          accent={C.success}
        />
        <RoleCard
          icon="⚙"
          title="Dashboard Institucional"
          subtitle="Administración y auditoría del proceso"
          desc="Registro de actas, captura PREP, cadena de custodia, alertas de inconsistencias y auditoría completa."
          cta="Acceso institucional"
          onClick={() => setView("institucional")}
          accent={C.primary}
          badge="AUDITOR / SUPERVISOR"
        />
      </div>

      {/* Trust bar */}
      <div style={{
        marginTop: 56, display: "flex", gap: 32, color: C.subtle, fontSize: 12,
        flexWrap: "wrap", justifyContent: "center",
      }}>
        {["Hashes en blockchain", "Auditoría en tiempo real", "Sin confianza implícita", "Código abierto"].map(t => (
          <span key={t} style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <span style={{ color: C.success }}>✓</span> {t}
          </span>
        ))}
      </div>
    </div>
  );
}

function RoleCard({ icon, title, subtitle, desc, cta, onClick, accent, badge }) {
  const [hover, setHover] = useState(false);
  return (
    <div
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      onClick={onClick}
      style={{
        background: hover ? C.panel : C.surface,
        border: `1px solid ${hover ? accent : C.border}`,
        borderRadius: 12, padding: "28px 28px 24px",
        width: 280, cursor: "pointer",
        transition: "all 0.18s ease",
        boxShadow: hover ? `0 0 0 1px ${accent}40, 0 8px 32px #00000060` : "none",
      }}
    >
      {badge && (
        <div style={{
          fontSize: 10, fontWeight: 700, color: accent,
          letterSpacing: 1, marginBottom: 12,
          fontFamily: "IBM Plex Mono, monospace",
        }}>{badge}</div>
      )}
      <div style={{ fontSize: 32, marginBottom: 12 }}>{icon}</div>
      <div style={{ color: C.text, fontWeight: 700, fontSize: 18, marginBottom: 4 }}>{title}</div>
      <div style={{ color: accent, fontSize: 12, fontWeight: 600, marginBottom: 12 }}>{subtitle}</div>
      <div style={{ color: C.muted, fontSize: 13, lineHeight: 1.6, marginBottom: 20 }}>{desc}</div>
      <div style={{
        display: "inline-flex", alignItems: "center", gap: 6,
        background: accent, color: "#fff",
        padding: "8px 16px", borderRadius: 6,
        fontSize: 13, fontWeight: 600,
      }}>{cta} →</div>
    </div>
  );
}

// ─── Portal Ciudadano ─────────────────────────────────────────────────────────

function PortalCiudadano({ setView }) {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [searched, setSearched] = useState(false);

  const handleSearch = () => {
    const found = ACTAS.find(
      a =>
        a.casilla.toLowerCase().includes(query.toLowerCase()) ||
        a.id.toLowerCase().includes(query.toLowerCase()) ||
        a.seccion.includes(query)
    );
    setResult(found || null);
    setSearched(true);
  };

  return (
    <div style={{
      minHeight: "100vh", background: C.bg, color: C.text,
      fontFamily: "IBM Plex Sans, sans-serif",
    }}>
      {/* Header */}
      <div style={{
        background: C.surface, borderBottom: `1px solid ${C.border}`,
        padding: "12px 24px", display: "flex", alignItems: "center", gap: 16,
      }}>
        <button onClick={() => setView("landing")} style={{
          background: "none", border: "none", color: C.muted,
          cursor: "pointer", fontSize: 13, display: "flex", alignItems: "center", gap: 4,
        }}>← Inicio</button>
        <div style={{ width: 1, height: 20, background: C.border }} />
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontSize: 18 }}>🏛</span>
          <span style={{ fontWeight: 700, fontSize: 15 }}>Portal Ciudadano</span>
          <span style={{
            background: "#10b98120", color: "#10b981",
            fontSize: 10, padding: "2px 8px", borderRadius: 10, fontWeight: 700,
          }}>ACCESO PÚBLICO</span>
        </div>
      </div>

      <div style={{ maxWidth: 680, margin: "0 auto", padding: "40px 24px" }}>
        <h1 style={{ fontSize: 26, fontWeight: 800, marginBottom: 8 }}>
          Verifica el resultado de tu casilla
        </h1>
        <p style={{ color: C.muted, fontSize: 14, marginBottom: 32 }}>
          Ingresa el número de casilla, sección o folio del acta. Los resultados son públicos y verificables en blockchain.
        </p>

        {/* Search */}
        <div style={{ display: "flex", gap: 10, marginBottom: 32 }}>
          <input
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleSearch()}
            placeholder="Ej: 1042-B  ·  Sección 0394  ·  ACT-CHH-01-0042-2024"
            style={{
              flex: 1, background: C.panel, border: `1px solid ${C.border}`,
              borderRadius: 8, padding: "12px 16px",
              color: C.text, fontSize: 14, outline: "none",
              fontFamily: "IBM Plex Sans, sans-serif",
            }}
          />
          <button onClick={handleSearch} style={{
            background: C.primary, border: "none", borderRadius: 8,
            color: "#fff", padding: "12px 20px", cursor: "pointer",
            fontWeight: 700, fontSize: 14, whiteSpace: "nowrap",
          }}>Verificar →</button>
        </div>

        {/* Example queries */}
        <div style={{ display: "flex", gap: 8, marginBottom: 32, flexWrap: "wrap" }}>
          <span style={{ color: C.subtle, fontSize: 12 }}>Probar:</span>
          {["1042-B", "1087-A", "2013-C"].map(q => (
            <button key={q} onClick={() => { setQuery(q); }} style={{
              background: "none", border: `1px solid ${C.border}`,
              borderRadius: 4, padding: "2px 10px", color: C.muted,
              fontSize: 12, cursor: "pointer", fontFamily: "IBM Plex Mono, monospace",
            }}>{q}</button>
          ))}
        </div>

        {/* Result */}
        {searched && !result && (
          <div style={{
            background: C.panel, border: `1px solid ${C.border}`,
            borderRadius: 10, padding: 24, textAlign: "center",
            color: C.muted, fontSize: 14,
          }}>
            No se encontró ningún acta con ese criterio.
          </div>
        )}

        {result && <ActaCard acta={result} />}
      </div>
    </div>
  );
}

function ActaCard({ acta }) {
  const [tab, setTab] = useState("resultado");
  const tabs = [
    { id: "resultado", label: "Resultado" },
    { id: "verificacion", label: "Verificación" },
    { id: "custodia", label: "Cadena de Custodia" },
  ];

  return (
    <div style={{
      background: C.panel, border: `1px solid ${C.border}`,
      borderRadius: 12, overflow: "hidden",
    }}>
      {/* Card header */}
      <div style={{
        background: C.surface, padding: "16px 20px",
        borderBottom: `1px solid ${C.border}`,
        display: "flex", justifyContent: "space-between", alignItems: "center",
      }}>
        <div>
          <div style={{ fontFamily: "IBM Plex Mono, monospace", fontSize: 11, color: C.muted, marginBottom: 4 }}>
            {acta.id}
          </div>
          <div style={{ fontWeight: 700, fontSize: 16 }}>
            Casilla {acta.casilla} · {acta.municipio}
          </div>
          <div style={{ color: C.muted, fontSize: 12, marginTop: 2 }}>
            {acta.distrito} · Sección {acta.seccion}
          </div>
        </div>
        <Badge estado={acta.estado} />
      </div>

      {/* Tabs */}
      <div style={{
        display: "flex", borderBottom: `1px solid ${C.border}`,
        background: C.surface,
      }}>
        {tabs.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)} style={{
            background: "none", border: "none",
            borderBottom: tab === t.id ? `2px solid ${C.primary}` : "2px solid transparent",
            color: tab === t.id ? C.text : C.muted,
            padding: "10px 20px", cursor: "pointer",
            fontSize: 13, fontWeight: tab === t.id ? 600 : 400,
            fontFamily: "IBM Plex Sans, sans-serif",
            transition: "all 0.15s",
          }}>{t.label}</button>
        ))}
      </div>

      {/* Tab content */}
      <div style={{ padding: 20 }}>
        {tab === "resultado" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div style={{ display: "flex", gap: 12 }}>
              <MetricBox label="Votos en Acta" value={acta.votos_acta} color={C.text} />
              <MetricBox
                label="Votos en PREP"
                value={acta.votos_prep ?? "—"}
                color={acta.estado === "inconsistencia" ? C.danger : C.success}
                note={acta.estado === "inconsistencia" ? "⚠ Diferencia detectada" : "✓ Coincide"}
              />
            </div>
            {acta.estado === "inconsistencia" && (
              <div style={{
                background: "#ef444410", border: "1px solid #ef444430",
                borderRadius: 8, padding: "12px 16px", color: "#ef4444", fontSize: 13,
              }}>
                ⚠ <strong>Inconsistencia registrada.</strong> Los votos capturados en PREP ({acta.votos_prep}) no coinciden con el acta física ({acta.votos_acta}). Este evento fue registrado automáticamente en la bitácora de auditoría y notificado al supervisor.
              </div>
            )}
            <div style={{ color: C.muted, fontSize: 12 }}>
              Registrado el {acta.timestamp_registro}
            </div>
          </div>
        )}

        {tab === "verificacion" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div>
              <div style={{ fontSize: 12, color: C.muted, marginBottom: 8 }}>Hash del documento (SHA-256)</div>
              <HashDisplay hash={acta.hash} />
            </div>
            {acta.blockchain_tx ? (
              <div>
                <div style={{ fontSize: 12, color: C.muted, marginBottom: 8 }}>Registro en Blockchain</div>
                <div style={{
                  background: "#10b98108", border: "1px solid #10b98130",
                  borderRadius: 8, padding: 14,
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                    <span style={{ color: C.muted, fontSize: 12 }}>TX Hash</span>
                    <span style={{ fontFamily: "IBM Plex Mono, monospace", fontSize: 11, color: "#10b981" }}>
                      {acta.blockchain_tx}
                    </span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                    <span style={{ color: C.muted, fontSize: 12 }}>Bloque</span>
                    <span style={{ fontFamily: "IBM Plex Mono, monospace", fontSize: 11, color: C.text }}>
                      #{acta.blockchain_block}
                    </span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span style={{ color: C.muted, fontSize: 12 }}>Timestamp blockchain</span>
                    <span style={{ fontSize: 11, color: C.text }}>{acta.timestamp_blockchain}</span>
                  </div>
                </div>
                <div style={{
                  marginTop: 12, padding: "10px 14px",
                  background: "#10b98115", borderRadius: 6,
                  color: "#10b981", fontSize: 12, display: "flex", alignItems: "center", gap: 8,
                }}>
                  <span style={{ fontSize: 18 }}>✓</span>
                  <span>Este documento puede ser verificado de forma independiente usando el hash SHA-256 y la transacción blockchain. No requiere confiar en este sistema.</span>
                </div>
              </div>
            ) : (
              <div style={{
                background: "#f59e0b10", border: "1px solid #f59e0b30",
                borderRadius: 8, padding: 14, color: "#f59e0b", fontSize: 13,
              }}>
                ◔ Pendiente de registro en blockchain. El acta fue capturada pero aún no se ha confirmado la transacción en la red.
              </div>
            )}
          </div>
        )}

        {tab === "custodia" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 0 }}>
            <div style={{ color: C.muted, fontSize: 12, marginBottom: 16 }}>
              Registro completo de personas que interactuaron con este documento
            </div>
            {acta.custodios.map((c, i) => (
              <div key={i} style={{
                display: "flex", alignItems: "flex-start", gap: 14,
                paddingBottom: i < acta.custodios.length - 1 ? 16 : 0,
                marginBottom: i < acta.custodios.length - 1 ? 16 : 0,
                borderBottom: i < acta.custodios.length - 1 ? `1px solid ${C.border}` : "none",
              }}>
                <div style={{
                  width: 8, height: 8, borderRadius: "50%", background: C.primary,
                  marginTop: 5, flexShrink: 0,
                }} />
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: 14 }}>{c.nombre}</div>
                  <div style={{ color: C.muted, fontSize: 12 }}>{c.rol}</div>
                </div>
                <div style={{
                  fontFamily: "IBM Plex Mono, monospace", fontSize: 11,
                  color: C.subtle, background: C.surface,
                  padding: "3px 8px", borderRadius: 4,
                }}>{c.ts}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function MetricBox({ label, value, color, note }) {
  return (
    <div style={{
      flex: 1, background: C.surface, borderRadius: 8,
      padding: "14px 16px", border: `1px solid ${C.border}`,
    }}>
      <div style={{ color: C.muted, fontSize: 11, marginBottom: 6 }}>{label}</div>
      <div style={{ fontSize: 32, fontWeight: 800, color, fontFamily: "IBM Plex Mono, monospace" }}>{value}</div>
      {note && <div style={{ fontSize: 11, color, marginTop: 4 }}>{note}</div>}
    </div>
  );
}

// ─── Dashboard Institucional ──────────────────────────────────────────────────

function DashboardInstitucional({ setView }) {
  const [activeTab, setActiveTab] = useState("overview");
  const [showModal, setShowModal] = useState(false);

  const tabs = [
    { id: "overview", label: "Resumen" },
    { id: "actas", label: "Actas" },
    { id: "auditoria", label: "Bitácora" },
  ];

  return (
    <div style={{
      minHeight: "100vh", background: C.bg, color: C.text,
      fontFamily: "IBM Plex Sans, sans-serif", display: "flex",
    }}>
      {/* Sidebar */}
      <div style={{
        width: 220, background: C.surface, borderRight: `1px solid ${C.border}`,
        padding: "16px 0", flexShrink: 0,
        display: "flex", flexDirection: "column",
      }}>
        <div style={{ padding: "0 16px 16px", borderBottom: `1px solid ${C.border}`, marginBottom: 8 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
            <div style={{
              width: 28, height: 28, borderRadius: 6, background: C.primary,
              display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14,
            }}>⚙</div>
            <span style={{ fontWeight: 800, fontSize: 15 }}>ActaTrace</span>
          </div>
          <div style={{
            fontSize: 10, color: C.muted,
            fontFamily: "IBM Plex Mono, monospace",
          }}>DASHBOARD INSTITUCIONAL</div>
        </div>

        {[
          { id: "overview", icon: "◈", label: "Resumen General" },
          { id: "actas", icon: "◻", label: "Actas" },
          { id: "auditoria", icon: "≡", label: "Bitácora" },
        ].map(item => (
          <button key={item.id} onClick={() => setActiveTab(item.id)} style={{
            display: "flex", alignItems: "center", gap: 10,
            padding: "10px 16px", background: activeTab === item.id ? "#0C5CAB20" : "none",
            border: "none", borderLeft: activeTab === item.id ? `2px solid ${C.primary}` : "2px solid transparent",
            color: activeTab === item.id ? C.text : C.muted,
            cursor: "pointer", fontSize: 13, width: "100%", textAlign: "left",
            fontFamily: "IBM Plex Sans, sans-serif",
          }}>
            <span>{item.icon}</span> {item.label}
          </button>
        ))}

        <div style={{ marginTop: "auto", padding: "16px" }}>
          <div style={{
            background: "#10b98115", border: "1px solid #10b98130",
            borderRadius: 6, padding: "8px 10px", fontSize: 11,
            color: "#10b981",
          }}>
            ● Sistema activo<br />
            <span style={{ color: C.muted, fontSize: 10 }}>Proceso: 02-Jun-2024</span>
          </div>
          <button onClick={() => setView("landing")} style={{
            marginTop: 12, background: "none", border: `1px solid ${C.border}`,
            color: C.muted, borderRadius: 6, padding: "6px 12px",
            cursor: "pointer", fontSize: 12, width: "100%",
            fontFamily: "IBM Plex Sans, sans-serif",
          }}>← Inicio</button>
        </div>
      </div>

      {/* Main */}
      <div style={{ flex: 1, padding: 28, overflowY: "auto" }}>
        {activeTab === "overview" && <OverviewTab setShowModal={setShowModal} />}
        {activeTab === "actas" && <ActasTab setShowModal={setShowModal} />}
        {activeTab === "auditoria" && <AuditoriaTab />}
      </div>

      {showModal && <RegistrarActaModal onClose={() => setShowModal(false)} />}
    </div>
  );
}

function OverviewTab({ setShowModal }) {
  const stats = [
    { label: "Actas Registradas", value: STATS.actas_total.toLocaleString(), color: C.text, icon: "◻" },
    { label: "Verificadas", value: STATS.actas_verificadas.toLocaleString(), color: C.success, icon: "✓" },
    { label: "Pendientes", value: STATS.actas_pendientes.toLocaleString(), color: C.warning, icon: "◔" },
    { label: "Inconsistencias", value: STATS.inconsistencias, color: C.danger, icon: "⚠" },
  ];

  return (
    <div>
      <div style={{ marginBottom: 24, display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 800, margin: 0 }}>Resumen General</h1>
          <p style={{ color: C.muted, fontSize: 13, marginTop: 4 }}>
            Proceso Electoral 2024 · Cobertura: <strong style={{ color: C.success }}>{STATS.cobertura}</strong>
          </p>
        </div>
        <button onClick={() => setShowModal(true)} style={{
          background: C.primary, border: "none", color: "#fff",
          padding: "10px 18px", borderRadius: 8, cursor: "pointer",
          fontWeight: 700, fontSize: 13, fontFamily: "IBM Plex Sans, sans-serif",
        }}>+ Registrar Acta</button>
      </div>

      {/* Stat cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 14, marginBottom: 28 }}>
        {stats.map(s => (
          <div key={s.label} style={{
            background: C.panel, border: `1px solid ${C.border}`,
            borderRadius: 10, padding: "16px 18px",
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 10 }}>
              <span style={{ color: C.muted, fontSize: 12 }}>{s.label}</span>
              <span style={{ color: s.color, fontSize: 16 }}>{s.icon}</span>
            </div>
            <div style={{ fontSize: 28, fontWeight: 800, color: s.color, fontFamily: "IBM Plex Mono, monospace" }}>
              {s.value}
            </div>
          </div>
        ))}
      </div>

      {/* Recent actas */}
      <div style={{ background: C.panel, border: `1px solid ${C.border}`, borderRadius: 10 }}>
        <div style={{
          padding: "14px 18px", borderBottom: `1px solid ${C.border}`,
          fontWeight: 700, fontSize: 14, display: "flex", justifyContent: "space-between",
        }}>
          <span>Actas recientes</span>
          <span style={{ color: C.muted, fontSize: 12, fontWeight: 400 }}>Últimas 3</span>
        </div>
        {ACTAS.map(acta => (
          <div key={acta.id} style={{
            padding: "12px 18px", borderBottom: `1px solid ${C.border}`,
            display: "flex", justifyContent: "space-between", alignItems: "center",
          }}>
            <div>
              <div style={{ fontSize: 13, fontWeight: 600 }}>Casilla {acta.casilla}</div>
              <div style={{ fontSize: 11, color: C.muted, fontFamily: "IBM Plex Mono, monospace" }}>{acta.id}</div>
            </div>
            <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
              <span style={{ fontSize: 12, color: C.muted }}>{acta.timestamp_registro}</span>
              <Badge estado={acta.estado} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ActasTab({ setShowModal }) {
  return (
    <div>
      <div style={{ marginBottom: 20, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1 style={{ fontSize: 22, fontWeight: 800, margin: 0 }}>Gestión de Actas</h1>
        <button onClick={() => setShowModal(true)} style={{
          background: C.primary, border: "none", color: "#fff",
          padding: "10px 18px", borderRadius: 8, cursor: "pointer",
          fontWeight: 700, fontSize: 13, fontFamily: "IBM Plex Sans, sans-serif",
        }}>+ Registrar Acta</button>
      </div>
      <div style={{ background: C.panel, border: `1px solid ${C.border}`, borderRadius: 10, overflow: "hidden" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
          <thead>
            <tr style={{ background: C.surface }}>
              {["Folio / ID", "Casilla", "Municipio", "Votos Acta", "Votos PREP", "Estado", "Blockchain"].map(h => (
                <th key={h} style={{
                  padding: "10px 14px", textAlign: "left",
                  color: C.muted, fontSize: 11, fontWeight: 700,
                  borderBottom: `1px solid ${C.border}`,
                }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {ACTAS.map((acta, i) => (
              <tr key={acta.id} style={{
                background: i % 2 === 0 ? "transparent" : "#ffffff04",
                borderBottom: `1px solid ${C.border}`,
              }}>
                <td style={{ padding: "10px 14px", fontFamily: "IBM Plex Mono, monospace", fontSize: 11, color: C.muted }}>
                  {acta.id}
                </td>
                <td style={{ padding: "10px 14px", fontWeight: 600 }}>{acta.casilla}</td>
                <td style={{ padding: "10px 14px", color: C.muted }}>{acta.municipio}</td>
                <td style={{ padding: "10px 14px", fontFamily: "IBM Plex Mono, monospace" }}>{acta.votos_acta}</td>
                <td style={{
                  padding: "10px 14px",
                  fontFamily: "IBM Plex Mono, monospace",
                  color: acta.estado === "inconsistencia" ? C.danger : C.text,
                }}>{acta.votos_prep ?? "—"}</td>
                <td style={{ padding: "10px 14px" }}><Badge estado={acta.estado} /></td>
                <td style={{ padding: "10px 14px", fontSize: 11 }}>
                  {acta.blockchain_tx ? (
                    <span style={{ color: C.success }}>✓ Confirmado</span>
                  ) : (
                    <span style={{ color: C.warning }}>◔ Pendiente</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function AuditoriaTab() {
  const eventos = [
    { ts: "20:15:01", tipo: "BLOCKCHAIN", desc: "Hash registrado en blockchain · ACT-CHH-01-0042-2024", color: C.success },
    { ts: "20:14:50", tipo: "SUPERVISOR", desc: "Acta validada por Lic. Fernanda Salas · Casilla 1042-B", color: C.primary },
    { ts: "20:14:33", tipo: "REGISTRO", desc: "Acta capturada por Carlos Ibáñez · Casilla 1042-B", color: C.text },
    { ts: "20:32:01", tipo: "ALERTA", desc: "⚠ Inconsistencia detectada · Casilla 1087-A · Diferencia: 2 votos", color: C.danger },
    { ts: "20:31:44", tipo: "BLOCKCHAIN", desc: "Hash registrado en blockchain · ACT-CHH-01-0087-2024", color: C.success },
    { ts: "20:31:17", tipo: "REGISTRO", desc: "Acta capturada por Ana Lucía Vega · Casilla 1087-A", color: C.text },
    { ts: "21:02:48", tipo: "REGISTRO", desc: "Acta capturada por Miguel Ángel Rojo · Casilla 2013-C", color: C.text },
    { ts: "21:03:05", tipo: "SISTEMA", desc: "Hash SHA-256 generado · ACT-CHH-02-0013-2024 · Pendiente blockchain", color: C.warning },
  ];

  return (
    <div>
      <h1 style={{ fontSize: 22, fontWeight: 800, marginBottom: 4 }}>Bitácora de Auditoría</h1>
      <p style={{ color: C.muted, fontSize: 13, marginBottom: 24 }}>
        Registro inmutable de todos los eventos del sistema. No editable.
      </p>
      <div style={{ background: C.panel, border: `1px solid ${C.border}`, borderRadius: 10 }}>
        {eventos.map((e, i) => (
          <div key={i} style={{
            display: "flex", gap: 14, padding: "12px 16px",
            borderBottom: i < eventos.length - 1 ? `1px solid ${C.border}` : "none",
            alignItems: "flex-start",
          }}>
            <div style={{ fontFamily: "IBM Plex Mono, monospace", fontSize: 11, color: C.subtle, width: 60, flexShrink: 0, paddingTop: 2 }}>
              {e.ts}
            </div>
            <div style={{
              fontSize: 10, fontWeight: 700, letterSpacing: 0.5,
              color: e.color, width: 80, flexShrink: 0, paddingTop: 3,
              fontFamily: "IBM Plex Mono, monospace",
            }}>{e.tipo}</div>
            <div style={{ fontSize: 13, color: C.text }}>{e.desc}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function RegistrarActaModal({ onClose }) {
  const [step, setStep] = useState(1);
  const [form, setForm] = useState({ casilla: "", seccion: "", votos: "" });

  return (
    <div style={{
      position: "fixed", inset: 0, background: "#000000a0",
      display: "flex", alignItems: "center", justifyContent: "center",
      zIndex: 100,
    }}>
      <div style={{
        background: C.panel, border: `1px solid ${C.border}`,
        borderRadius: 12, width: 480, padding: 28,
        fontFamily: "IBM Plex Sans, sans-serif", color: C.text,
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 20 }}>
          <div>
            <div style={{ fontWeight: 800, fontSize: 17 }}>Registrar Acta Electoral</div>
            <div style={{ color: C.muted, fontSize: 12, marginTop: 2 }}>
              Paso {step} de 3 · {["Datos de casilla", "Resultados", "Confirmar"][step - 1]}
            </div>
          </div>
          <button onClick={onClose} style={{
            background: "none", border: "none", color: C.muted,
            cursor: "pointer", fontSize: 18,
          }}>✕</button>
        </div>

        {/* Steps */}
        <div style={{ display: "flex", gap: 4, marginBottom: 24 }}>
          {[1, 2, 3].map(s => (
            <div key={s} style={{
              flex: 1, height: 3, borderRadius: 2,
              background: s <= step ? C.primary : C.border,
              transition: "background 0.2s",
            }} />
          ))}
        </div>

        {step === 1 && (
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <FormField label="Número de Casilla" placeholder="Ej: 1042-B"
              value={form.casilla} onChange={v => setForm(p => ({ ...p, casilla: v }))} />
            <FormField label="Sección Electoral" placeholder="Ej: 0394"
              value={form.seccion} onChange={v => setForm(p => ({ ...p, seccion: v }))} />
          </div>
        )}
        {step === 2 && (
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <FormField label="Total de votos en acta" placeholder="Ej: 342"
              value={form.votos} onChange={v => setForm(p => ({ ...p, votos: v }))} />
            <div style={{
              background: C.surface, borderRadius: 6, padding: "10px 12px",
              fontSize: 12, color: C.muted,
            }}>
              El hash SHA-256 del documento se generará automáticamente al confirmar.
            </div>
          </div>
        )}
        {step === 3 && (
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <div style={{ background: C.surface, borderRadius: 8, padding: 14, fontSize: 13 }}>
              <div style={{ marginBottom: 8, color: C.muted, fontSize: 11, fontWeight: 700 }}>RESUMEN DEL ACTA</div>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                <span style={{ color: C.muted }}>Casilla</span>
                <span style={{ fontWeight: 600 }}>{form.casilla || "—"}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                <span style={{ color: C.muted }}>Sección</span>
                <span>{form.seccion || "—"}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: C.muted }}>Votos en acta</span>
                <span style={{ fontFamily: "IBM Plex Mono, monospace" }}>{form.votos || "—"}</span>
              </div>
            </div>
            <div style={{
              background: "#0C5CAB10", border: "1px solid #0C5CAB30",
              borderRadius: 6, padding: "10px 12px", fontSize: 12, color: C.muted,
            }}>
              Al confirmar: se generará el hash SHA-256, se registrará en la bitácora de auditoría y se encolará para registro en blockchain.
            </div>
          </div>
        )}

        <div style={{ display: "flex", justifyContent: "flex-end", gap: 10, marginTop: 24 }}>
          {step > 1 && (
            <button onClick={() => setStep(s => s - 1)} style={{
              background: "none", border: `1px solid ${C.border}`,
              color: C.muted, padding: "10px 18px", borderRadius: 8,
              cursor: "pointer", fontSize: 13, fontFamily: "IBM Plex Sans, sans-serif",
            }}>← Atrás</button>
          )}
          <button onClick={() => {
            if (step < 3) setStep(s => s + 1);
            else { alert("✓ Acta registrada. Hash generado y encolado para blockchain."); onClose(); }
          }} style={{
            background: C.primary, border: "none", color: "#fff",
            padding: "10px 18px", borderRadius: 8, cursor: "pointer",
            fontWeight: 700, fontSize: 13, fontFamily: "IBM Plex Sans, sans-serif",
          }}>{step < 3 ? "Siguiente →" : "✓ Confirmar y Registrar"}</button>
        </div>
      </div>
    </div>
  );
}

function FormField({ label, placeholder, value, onChange }) {
  return (
    <div>
      <label style={{ display: "block", fontSize: 12, color: C.muted, marginBottom: 6, fontWeight: 600 }}>
        {label}
      </label>
      <input
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        style={{
          width: "100%", background: C.surface, border: `1px solid ${C.border}`,
          borderRadius: 6, padding: "10px 12px", color: C.text,
          fontSize: 13, outline: "none", fontFamily: "IBM Plex Sans, sans-serif",
          boxSizing: "border-box",
        }}
      />
    </div>
  );
}

// ─── Root ─────────────────────────────────────────────────────────────────────

export default function App() {
  const [view, setView] = useState("landing");
  return (
    <>
      <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;700&display=swap" rel="stylesheet" />
      {view === "landing" && <Landing setView={setView} />}
      {view === "ciudadano" && <PortalCiudadano setView={setView} />}
      {view === "institucional" && <DashboardInstitucional setView={setView} />}
    </>
  );
}
