import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Papa from "papaparse";

// Design tokens
const C = {
  bg: "#07080a",
  surface: "#0f1015",
  panel: "#14161c",
  card: "#1a1d27",
  cardHi: "#202432",
  border: "#1e2133",
  borderHi: "#2a2f47",
  primary: "#1a6eff",
  primaryDim: "#1a6eff20",
  success: "#00d68f",
  successDim: "#00d68f20",
  warning: "#ffb938",
  warningDim: "#ffb93820",
  danger: "#ff3d5a",
  dangerDim: "#ff3d5a20",
  info: "#7c6aff",
  infoDim: "#7c6aff20",
  neutral: "#4b5572",
  neutralDim: "#4b557220",
  text: "#f0f2ff",
  muted: "#7880a0",
  subtle: "#3d4460",
};

const STATUS = {
  abierta: { color: C.success, dim: C.successDim, label: "Abierta", pulse: true },
  cerrada: { color: C.neutral, dim: C.neutralDim, label: "Cerrada", pulse: false },
  contada: { color: C.primary, dim: C.primaryDim, label: "Contada", pulse: false },
  pendiente: { color: C.warning, dim: C.warningDim, label: "Pendiente", pulse: false },
  inconsistencia: { color: C.danger, dim: C.dangerDim, label: "Inconsistencia", pulse: true },
};

const GEOCODING = {
  geocoded: { color: C.success, dim: C.successDim, label: "Geocodificada" },
  not_geocoded: { color: C.warning, dim: C.warningDim, label: "Requiere geocodificación" },
  requires_review: { color: C.warning, dim: C.warningDim, label: "Requiere geocodificación" },
  failed: { color: C.danger, dim: C.dangerDim, label: "Geocodificación fallida" },
};

const MUNS = [
  { name: "Cd. Juárez", lat: 31.73, lng: 106.49, r: 0.28, n: 26, abbr: "Juárez" },
  { name: "Chihuahua", lat: 28.63, lng: 106.07, r: 0.22, n: 18, abbr: "Chih." },
  { name: "Delicias", lat: 28.19, lng: 105.47, r: 0.13, n: 7, abbr: "Delicias" },
  { name: "Cuauhtémoc", lat: 28.41, lng: 106.86, r: 0.14, n: 7, abbr: "Cuauhtémoc" },
  { name: "Parral", lat: 26.93, lng: 105.67, r: 0.13, n: 6, abbr: "Parral" },
  { name: "Nuevo Casas Grandes", lat: 30.41, lng: 107.91, r: 0.18, n: 5, abbr: "NCG" },
  { name: "Ojinaga", lat: 29.56, lng: 104.41, r: 0.10, n: 4, abbr: "Ojinaga" },
  { name: "Camargo", lat: 27.68, lng: 105.17, r: 0.10, n: 4, abbr: "Camargo" },
  { name: "Creel", lat: 27.75, lng: 107.63, r: 0.08, n: 3, abbr: "Creel" },
  { name: "Jiménez", lat: 27.13, lng: 104.92, r: 0.08, n: 2, abbr: "Jiménez" },
];

const STATUS_ORDER = ["abierta", "cerrada", "contada", "pendiente", "inconsistencia"];
const DEFAULT_IMPORT_RESULT = { imported: 0, skipped: 0, failed: 0, requiringGeocoding: 0 };

function mkCasillas() {
  let s = 99991;
  const r = () => {
    s = (s * 16807) % 2147483647;
    return (s - 1) / 2147483646;
  };
  const hex = (n = 8) => [...Array(n)].map(() => (~~(r() * 16)).toString(16)).join("");
  const out = [];
  let id = 1;

  for (const m of MUNS) {
    for (let i = 0; i < m.n; i++) {
      const lat = m.lat + (r() - 0.5) * m.r * 2;
      const lng = m.lng + (r() - 0.5) * m.r * 2;
      const status = STATUS_ORDER[Math.floor(r() * STATUS_ORDER.length)];
      const votosActa = Math.floor(r() * 340) + 60;
      const inc = status === "inconsistencia" ? Math.floor(r() * 5) + 1 : 0;

      out.push({
        id: `CHH-${String(id).padStart(4, "0")}`,
        municipio: m.name,
        seccion: Math.floor(r() * 900) + 100,
        numero: `${Math.floor(r() * 2000) + 500}-${["A", "B", "C"][Math.floor(r() * 3)]}`,
        direccion_original: `Domicilio oficial de referencia, ${m.name}, Chihuahua`,
        direccion_normalizada: null,
        lat,
        lng,
        geocoding_status: "geocoded",
        geocoding_source: "csv",
        status,
        votos_acta: votosActa,
        votos_prep: status === "inconsistencia" ? votosActa + inc : ["contada", "cerrada"].includes(status) ? votosActa : null,
        hash: ["contada", "inconsistencia"].includes(status) ? hex(20) : null,
        hora: `${String(7 + Math.floor(r() * 11)).padStart(2, "0")}:${String(Math.floor(r() * 60)).padStart(2, "0")}`,
      });
      id++;
    }
  }

  return out;
}

const fmtTime = (d) => d.toLocaleTimeString("es-MX", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
const fmtCd = (s) => `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;
const fmtNum = (n) => Number(n || 0).toLocaleString("es-MX");
const hasCoords = (c) => Number.isFinite(c.lat) && Number.isFinite(c.lng);
const safeStatus = (value) => (STATUS[value] ? value : "pendiente");
const normalizeKey = (key) => String(key || "").trim().toLowerCase();
const cleanValue = (value) => {
  if (value === undefined || value === null) return "";
  return String(value).trim();
};
const parseNullableNumber = (value) => {
  const cleaned = cleanValue(value).replace(",", ".");
  if (!cleaned) return null;
  const n = Number(cleaned);
  return Number.isFinite(n) ? n : null;
};
const toMapLon = (lng) => (Number(lng) > 0 ? -Number(lng) : Number(lng));
const normalizeCsvRow = (row) => {
  const normalized = {};
  Object.entries(row || {}).forEach(([key, value]) => {
    normalized[normalizeKey(key)] = value;
  });

  return {
    id_casilla: normalized.id_casilla || normalized.id || normalized.identificador,
    municipio: normalized.municipio,
    seccion: normalized.seccion,
    numero: normalized.numero || normalized.casilla,
    latitud: normalized.latitud || normalized.lat,
    longitud: normalized.longitud || normalized.lng,
    direccion: normalized.direccion || normalized.direccion_original,
    votos_acta: normalized.votos_acta || normalized.acta,
    votos_prep: normalized.votos_prep || normalized.prep,
    hora: normalized.hora,
    estatus: normalized.estatus || normalized.status,
    hash: normalized.hash,
  };
};

const buttonBase = {
  borderRadius: 6,
  padding: "7px 9px",
  fontSize: 10,
  cursor: "pointer",
  fontFamily: "IBM Plex Sans, sans-serif",
  fontWeight: 700,
  lineHeight: 1.15,
};

function StatusBadge({ status, tone }) {
  const cfg = tone === "geocoding" ? GEOCODING[status] || GEOCODING.not_geocoded : STATUS[status] || STATUS.pendiente;
  return (
    <span
      className="status-badge"
      style={{
        background: cfg.dim,
        color: cfg.color,
        border: `1px solid ${cfg.color}40`,
        borderRadius: 4,
        padding: "2px 7px",
        fontSize: 10,
        fontWeight: 800,
        letterSpacing: 0.2,
        fontFamily: "IBM Plex Mono, monospace",
        whiteSpace: "nowrap",
      }}
    >
      {cfg.label}
    </span>
  );
}

function MiniBar({ pct, color }) {
  return (
    <div style={{ background: C.border, borderRadius: 3, height: 4, marginTop: 5 }}>
      <div style={{ background: color, borderRadius: 3, height: 4, width: `${pct}%`, transition: "width 0.6s ease" }} />
    </div>
  );
}

function StatCard({ label, value, color, sub }) {
  return (
    <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 8, padding: "11px 12px" }}>
      <div style={{ fontSize: 9, color: C.muted, marginBottom: 6, letterSpacing: 0.4 }}>{label}</div>
      <div style={{ fontSize: 22, fontWeight: 800, color, fontFamily: "IBM Plex Mono, monospace", lineHeight: 1 }}>{value}</div>
      {sub && <div style={{ fontSize: 10, color: C.muted, marginTop: 4 }}>{sub}</div>}
    </div>
  );
}

function SelectField({ value, onChange, options, style = {}, label }) {
  return (
    <label style={{ display: "flex", flexDirection: "column", gap: 5, minWidth: 0, ...style }}>
      {label && <span style={{ fontSize: 10, color: C.muted }}>{label}</span>}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        style={{
          background: C.card,
          border: `1px solid ${C.border}`,
          color: C.text,
          borderRadius: 6,
          padding: "7px 9px",
          fontSize: 12,
          fontFamily: "IBM Plex Sans, sans-serif",
          outline: "none",
          cursor: "pointer",
          minWidth: 0,
        }}
      >
        {options.map((o) => (
          <option key={o.v || o} value={o.v || o}>
            {o.l || o}
          </option>
        ))}
      </select>
    </label>
  );
}

function Header({ metrics, lastUpd, updating, autoRef, setAutoRef, intervalSec, setIntervalSec, cd, onManualRefresh }) {
  return (
    <header className="app-header">
      <div style={{ display: "flex", alignItems: "center", gap: 10, flexShrink: 0 }}>
        <svg width="30" height="30" viewBox="0 0 30 30" aria-hidden="true">
          <rect width="30" height="30" rx="7" fill={C.primary} />
          <path d="M7 15 L15 7 L23 15 L15 23 Z" fill="none" stroke="#fff" strokeWidth="2" />
          <circle cx="15" cy="15" r="3.5" fill="#fff" />
        </svg>
        <div>
          <div style={{ fontWeight: 800, fontSize: 14, letterSpacing: -0.3, lineHeight: 1.1 }}>ActaTrace</div>
          <div style={{ fontSize: 9, color: C.muted, letterSpacing: 1, fontFamily: "IBM Plex Mono, monospace" }}>
            MAPA ELECTORAL · IEE CHIHUAHUA
          </div>
        </div>
      </div>

      <div className="header-status">
        <span style={{ color: C.muted }}>
          <strong style={{ color: C.primary, fontFamily: "IBM Plex Mono, monospace" }}>{metrics.pctCo}%</strong> contadas
        </span>
        <span style={{ color: C.muted }}>{metrics.coordsCount} con coordenadas</span>
        {metrics.missingCoords > 0 && (
          <span style={{ color: C.warning, background: C.warningDim, border: `1px solid ${C.warning}40`, borderRadius: 4, padding: "2px 7px" }}>
            {metrics.missingCoords} requieren geocodificación
          </span>
        )}
      </div>

      <div className="header-controls">
        <span style={{ fontSize: 11, color: C.muted }}>
          {updating ? <span style={{ color: C.warning }}>Actualizando...</span> : `Actualizado ${fmtTime(lastUpd)}`}
        </span>
        {autoRef && !updating && (
          <span style={{ fontSize: 11, color: C.subtle, fontFamily: "IBM Plex Mono, monospace", background: C.panel, border: `1px solid ${C.border}`, padding: "3px 8px", borderRadius: 4 }}>
            {fmtCd(cd)}
          </span>
        )}
        <SelectField
          value={intervalSec}
          onChange={(v) => setIntervalSec(+v)}
          options={[{ v: 30, l: "30s" }, { v: 60, l: "1 min" }, { v: 120, l: "2 min" }, { v: 300, l: "5 min" }]}
        />
        <button
          onClick={() => setAutoRef((a) => !a)}
          style={{
            ...buttonBase,
            background: autoRef ? C.successDim : C.panel,
            border: `1px solid ${autoRef ? `${C.success}50` : C.border}`,
            color: autoRef ? C.success : C.muted,
          }}
        >
          {autoRef ? "Pausar auto" : "Activar auto"}
        </button>
        <button
          onClick={() => {
            onManualRefresh();
          }}
          style={{ ...buttonBase, background: C.primary, border: "none", color: "#fff" }}
        >
          Actualizar
        </button>
      </div>
    </header>
  );
}

function IeeCsvUploadPanel({ fileName, importResult, importError, onSelectClick, onLoad, onClear, hasPendingFile }) {
  return (
    <section className="csv-panel" aria-label="Archivo oficial IEE Chihuahua">
      <div style={{ fontWeight: 800, color: C.text, fontSize: 12, marginBottom: 4 }}>Archivo oficial IEE Chihuahua</div>
      <p style={{ color: C.muted, fontSize: 10, lineHeight: 1.35, marginBottom: 8 }}>
        Carga el CSV oficial para importar casillas, secciones, direcciones y datos preliminares.
      </p>
      <div className="csv-columns-hint" style={{ fontSize: 9, color: C.subtle, fontFamily: "IBM Plex Mono, monospace", marginBottom: 8, lineHeight: 1.35 }}>
        id_casilla, municipio, seccion, numero, latitud, longitud, direccion, votos_acta, votos_prep, hora, estatus
      </div>
      {fileName && (
        <div style={{ color: C.success, background: C.successDim, border: `1px solid ${C.success}35`, borderRadius: 6, padding: "6px 8px", fontSize: 10, marginBottom: 8, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
          {fileName}
        </div>
      )}
      {importError && (
        <div style={{ color: C.danger, background: C.dangerDim, border: `1px solid ${C.danger}35`, borderRadius: 6, padding: "6px 8px", fontSize: 10, marginBottom: 8 }}>
          {importError}
        </div>
      )}
      {(importResult.imported > 0 || importResult.failed > 0 || importResult.skipped > 0) && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6, marginBottom: 8 }}>
          <ImportMetric label="Importadas" value={importResult.imported} color={C.success} />
          <ImportMetric label="Omitidas" value={importResult.skipped} color={C.neutral} />
          <ImportMetric label="Fallidas" value={importResult.failed} color={C.danger} />
          <ImportMetric label="Sin coords" value={importResult.requiringGeocoding} color={C.warning} />
        </div>
      )}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 6 }}>
        <button onClick={onSelectClick} style={{ ...buttonBase, background: C.cardHi, border: `1px solid ${C.borderHi}`, color: C.text }}>
          Seleccionar
        </button>
        <button
          onClick={onLoad}
          disabled={!hasPendingFile}
          style={{
            ...buttonBase,
            background: hasPendingFile ? C.primary : C.card,
            border: `1px solid ${hasPendingFile ? C.primary : C.border}`,
            color: hasPendingFile ? "#fff" : C.subtle,
            cursor: hasPendingFile ? "pointer" : "not-allowed",
          }}
        >
          Cargar
        </button>
        <button onClick={onClear} style={{ ...buttonBase, background: C.panel, border: `1px solid ${C.border}`, color: C.muted }}>
          Limpiar
        </button>
      </div>
    </section>
  );
}

function ImportMetric({ label, value, color }) {
  return (
    <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 6, padding: "6px 8px" }}>
      <div style={{ color: C.muted, fontSize: 9 }}>{label}</div>
      <div style={{ color, fontFamily: "IBM Plex Mono, monospace", fontWeight: 800, fontSize: 13 }}>{value}</div>
    </div>
  );
}

function FooterCasillaSummary({ selected }) {
  return (
    <section className="footer-casilla-summary" aria-label="Resumen de casilla seleccionada">
      <div style={{ color: C.muted, fontSize: 9, fontWeight: 800, letterSpacing: 0.8, fontFamily: "IBM Plex Mono, monospace", marginBottom: 6 }}>
        CASILLA EN CAPTURA
      </div>
      {selected ? (
        <>
          <div style={{ display: "flex", justifyContent: "space-between", gap: 8, alignItems: "center", marginBottom: 5 }}>
            <strong style={{ color: C.text, fontFamily: "IBM Plex Mono, monospace", fontSize: 12 }}>Casilla {selected.numero}</strong>
            <StatusBadge status={selected.status} />
          </div>
          <div style={{ color: C.muted, fontSize: 11, lineHeight: 1.45 }}>
            Sección {selected.seccion} · {selected.municipio}
          </div>
          <div style={{ color: C.text, fontSize: 11, marginTop: 5 }}>
            Acta: <strong style={{ fontFamily: "IBM Plex Mono, monospace" }}>{selected.votos_acta ?? "-"}</strong>
            <span style={{ color: C.subtle }}> · </span>
            PREP: <strong style={{ fontFamily: "IBM Plex Mono, monospace" }}>{selected.votos_prep ?? "-"}</strong>
          </div>
          <div style={{ display: "flex", gap: 6, marginTop: 7, flexWrap: "wrap" }}>
            <StatusBadge status={selected.geocoding_status || (hasCoords(selected) ? "geocoded" : "not_geocoded")} tone="geocoding" />
          </div>
        </>
      ) : (
        <div style={{ color: C.muted, fontSize: 11, lineHeight: 1.5 }}>
          Selecciona una casilla para revisar votos, estado y evidencia de geocodificación junto al archivo oficial.
        </div>
      )}
    </section>
  );
}

function CapturedCasillasSidebar({
  records,
  selected,
  onSelect,
  search,
  setSearch,
  filterStatus,
  setFilterStatus,
  children,
}) {
  return (
    <aside className="left-sidebar">
      <div style={{ padding: 16, borderBottom: `1px solid ${C.border}` }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "baseline", marginBottom: 12 }}>
          <div>
            <h2 style={{ fontSize: 17, lineHeight: 1, margin: 0 }}>Casillas capturadas</h2>
            <div style={{ color: C.muted, fontSize: 11, marginTop: 5 }}>{records.length} registros en flujo operativo</div>
          </div>
        </div>
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Buscar casilla, sección o municipio"
          aria-label="Buscar casillas capturadas"
          style={{
            width: "100%",
            background: C.card,
            border: `1px solid ${C.border}`,
            color: C.text,
            borderRadius: 7,
            padding: "9px 10px",
            fontSize: 12,
            outline: "none",
            marginBottom: 9,
          }}
        />
        <SelectField
          label="Estado"
          value={filterStatus}
          onChange={setFilterStatus}
          options={[{ v: "Todos", l: "Todos los estados" }, ...Object.entries(STATUS).map(([k, v]) => ({ v: k, l: v.label }))]}
        />
      </div>

      <div className="captured-list">
        {records.length === 0 ? (
          <div style={{ color: C.muted, fontSize: 12, padding: 16, lineHeight: 1.5 }}>
            No hay casillas para los filtros actuales.
          </div>
        ) : (
          records.map((c) => <CapturedCasillaItem key={c.id} record={c} selected={selected?.id === c.id} onSelect={() => onSelect(c)} />)
        )}
      </div>

      <div className="csv-dock">
        <FooterCasillaSummary selected={selected} />
        {children}
      </div>
    </aside>
  );
}

function CapturedCasillaItem({ record, selected, onSelect }) {
  const coordStatus = record.geocoding_status || (hasCoords(record) ? "geocoded" : "not_geocoded");
  return (
    <button
      className="captured-item"
      onClick={onSelect}
      style={{
        background: selected ? "#1a6eff18" : C.card,
        border: `1px solid ${selected ? `${C.primary}60` : C.border}`,
        borderLeft: `3px solid ${selected ? C.primary : STATUS[record.status]?.color || C.neutral}`,
        color: C.text,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: 10, marginBottom: 7 }}>
        <strong style={{ fontSize: 13, fontFamily: "IBM Plex Mono, monospace" }}>Casilla {record.numero}</strong>
        <span style={{ color: C.muted, fontSize: 11 }}>Hora: {record.hora || "-"}</span>
      </div>
      <div style={{ color: C.muted, fontSize: 12, marginBottom: 7 }}>
        Sección {record.seccion || "-"} · {record.municipio || "Sin municipio"}
      </div>
      <div style={{ color: C.text, fontSize: 12, marginBottom: 8 }}>
        Acta: <strong style={{ fontFamily: "IBM Plex Mono, monospace" }}>{record.votos_acta ?? "-"}</strong>
        <span style={{ color: C.subtle }}> · </span>
        PREP: <strong style={{ fontFamily: "IBM Plex Mono, monospace" }}>{record.votos_prep ?? "-"}</strong>
      </div>
      {record.direccion_original && (
        <div className="official-address" style={{ color: C.subtle, fontSize: 10, lineHeight: 1.35, marginBottom: 8 }}>
          Dirección oficial: {record.direccion_original}
        </div>
      )}
      <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
        <StatusBadge status={record.status} />
        <StatusBadge status={coordStatus} tone="geocoding" />
      </div>
    </button>
  );
}

function ChihuahuaSvgMap({ records, visibleRecords, selected, onSelect, filterStatus, setFilterStatus, metrics }) {
  const mapRef = useRef(null);
  const mapViewRef = useRef({ center: { lat: 28.8, lon: -106.45 }, zoom: 5.7 });
  const plottedRecords = useMemo(() => visibleRecords.filter(hasCoords), [visibleRecords]);

  useEffect(() => () => {
    if (mapRef.current && window.Plotly) window.Plotly.purge(mapRef.current);
  }, []);

  useEffect(() => {
    if (!mapRef.current) return undefined;

    const currentMapView = mapViewRef.current;

    const traces = Object.entries(STATUS)
      .map(([status, cfg]) => {
        const rows = plottedRecords.filter((c) => c.status === status);
        return {
          type: "scattermap",
          mode: "markers",
          name: cfg.label,
          lat: rows.map((c) => c.lat),
          lon: rows.map((c) => toMapLon(c.lng)),
          text: rows.map((c) => `Casilla ${c.numero}`),
          customdata: rows.map((c) => c.id),
          hovertemplate: rows.map((c) => (
            `Casilla ${c.numero}<br>` +
            `Sección ${c.seccion} · ${c.municipio}<br>` +
            `Estado: ${STATUS[c.status]?.label || "Pendiente"}<br>` +
            `Acta: ${c.votos_acta ?? "-"} · PREP: ${c.votos_prep ?? "-"}<br>` +
            `Hora: ${c.hora || "-"}<extra></extra>`
          )),
          marker: {
            size: rows.map((c) => selected?.id === c.id ? 17 : 11),
            color: cfg.color,
            opacity: rows.map((c) => selected?.id === c.id ? 1 : 0.84),
            line: {
              color: rows.map((c) => selected?.id === c.id ? "#ffffff" : "#0f1015"),
              width: rows.map((c) => selected?.id === c.id ? 2 : 1),
            },
          },
        };
      })
      .filter((trace) => trace.lat.length > 0);

    const layout = {
      autosize: true,
      dragmode: "zoom",
      hovermode: "closest",
      showlegend: false,
      paper_bgcolor: C.panel,
      plot_bgcolor: C.panel,
      margin: { l: 0, r: 0, t: 0, b: 0, pad: 0 },
      map: {
        style: "carto-darkmatter",
        center: currentMapView.center,
        zoom: currentMapView.zoom,
        bearing: 0,
        pitch: 0,
      },
      uirevision: "actatrace-chihuahua-map",
    };

    const config = {
      responsive: true,
      scrollZoom: true,
      displaylogo: false,
      displayModeBar: true,
      modeBarButtonsToRemove: ["lasso2d", "select2d"],
    };

    let mounted = true;
    let activeMapNode = mapRef.current;

    import("plotly.js-dist-min").then((module) => {
      if (!mounted || !activeMapNode) return;
      const PlotlyModule = module.default || module;
      window.Plotly = PlotlyModule;
      PlotlyModule.react(activeMapNode, traces, layout, config);

      const handleClick = (event) => {
        const point = event?.points?.[0];
        const clicked = records.find((c) => c.id === point?.customdata);
        if (clicked) onSelect(clicked);
      };
      const handleRelayout = (event) => {
        const nextCenter = event?.["map.center"] || (
          event?.["map.center.lat"] !== undefined || event?.["map.center.lon"] !== undefined
            ? {
                lat: event?.["map.center.lat"] ?? mapViewRef.current.center.lat,
                lon: event?.["map.center.lon"] ?? mapViewRef.current.center.lon,
              }
            : null
        );
        const nextZoom = event?.["map.zoom"];

        if (nextCenter || nextZoom !== undefined) {
          mapViewRef.current = {
            center: nextCenter || mapViewRef.current.center,
            zoom: nextZoom ?? mapViewRef.current.zoom,
          };
        }
      };

      activeMapNode.on("plotly_click", handleClick);
      activeMapNode.on("plotly_relayout", handleRelayout);
    });

    return () => {
      mounted = false;
      activeMapNode?.removeAllListeners?.("plotly_click");
      activeMapNode?.removeAllListeners?.("plotly_relayout");
    };
  }, [onSelect, plottedRecords, records, selected]);

  return (
    <div className="map-panel">
      <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse at 40% 45%, #1a6eff08, transparent 70%)", pointerEvents: "none" }} />
      <div ref={mapRef} className="plotly-map" aria-label="Mapa interactivo Plotly de casillas en Chihuahua" />

      <div className="map-counter">
        {metrics.coordsCount} con coordenadas · {metrics.missingCoords} requieren geocodificación
      </div>

      <div className="map-legend">
        {Object.entries(STATUS).map(([k, v]) => {
          const count = records.filter((c) => c.status === k).length;
          return (
            <button key={k} onClick={() => setFilterStatus(filterStatus === k ? "Todos" : k)} className="legend-button">
              <span style={{ width: 8, height: 8, borderRadius: "50%", background: v.color, flexShrink: 0 }} />
              <span>{v.label}</span>
              <strong style={{ color: v.color, fontFamily: "IBM Plex Mono, monospace" }}>{count}</strong>
            </button>
          );
        })}
      </div>

      <div style={{ position: "absolute", top: 12, left: 12, color: C.subtle, fontSize: 10, fontFamily: "IBM Plex Mono, monospace" }}>N</div>
      <div style={{ position: "absolute", top: 12, right: 12, color: C.subtle, fontSize: 9, fontFamily: "IBM Plex Mono, monospace" }}>IEE Chihuahua · 2026</div>
    </div>
  );
}

function SelectedCasillaDetail({ selected, warning, onClose }) {
  if (!selected) return null;
  const status = STATUS[selected.status] || STATUS.pendiente;

  return (
    <section style={{ background: C.card, border: `1px solid ${status.color}50`, borderRadius: 10, padding: "14px 16px", flexShrink: 0 }}>
      <div style={{ display: "flex", gap: 14, alignItems: "flex-start" }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 9, flexWrap: "wrap", marginBottom: 8 }}>
            <strong style={{ fontFamily: "IBM Plex Mono, monospace", fontSize: 15 }}>Casilla {selected.numero}</strong>
            <StatusBadge status={selected.status} />
            <StatusBadge status={selected.geocoding_status || (hasCoords(selected) ? "geocoded" : "not_geocoded")} tone="geocoding" />
          </div>
          <div style={{ display: "flex", gap: 18, fontSize: 12, color: C.muted, marginBottom: 9, flexWrap: "wrap" }}>
            <span>{selected.municipio}</span>
            <span>Sección {selected.seccion}</span>
            <span>ID: {selected.id}</span>
            <span>Hora: {selected.hora || "-"}</span>
          </div>
          {warning && (
            <div style={{ background: C.warningDim, border: `1px solid ${C.warning}40`, color: C.warning, borderRadius: 7, padding: "8px 10px", fontSize: 12, marginBottom: 9 }}>
              {warning}
            </div>
          )}
          <div style={{ display: "flex", gap: 22, fontSize: 13, flexWrap: "wrap" }}>
            <span>Votos acta: <strong style={{ fontFamily: "IBM Plex Mono, monospace", color: C.text }}>{selected.votos_acta ?? "-"}</strong></span>
            <span>Votos PREP: <strong style={{ fontFamily: "IBM Plex Mono, monospace", color: selected.status === "inconsistencia" ? C.danger : C.text }}>{selected.votos_prep ?? "-"}</strong></span>
            {selected.status === "inconsistencia" && (
              <span style={{ color: C.danger }}>Diferencia {Math.abs((selected.votos_prep || 0) - (selected.votos_acta || 0))} votos</span>
            )}
          </div>
          {selected.direccion_original && (
            <div style={{ marginTop: 9, color: C.muted, fontSize: 12 }}>
              Dirección oficial: <span style={{ color: C.text }}>{selected.direccion_original}</span>
            </div>
          )}
          {selected.hash && (
            <div style={{ marginTop: 9, fontFamily: "IBM Plex Mono, monospace", fontSize: 10, color: C.success }}>
              SHA-256: {selected.hash}...
            </div>
          )}
        </div>
        <button onClick={onClose} aria-label="Cerrar detalle" style={{ background: "none", border: "none", color: C.subtle, cursor: "pointer", fontSize: 18, flexShrink: 0 }}>
          x
        </button>
      </div>
    </section>
  );
}

function MetricsPanel({ metrics, lastUpd }) {
  return (
    <aside className="right-panel">
      <div style={{ fontSize: 10, fontWeight: 800, color: C.muted, letterSpacing: 1.3, fontFamily: "IBM Plex Mono, monospace" }}>
        METRICAS EN TIEMPO REAL
      </div>
      <div style={{ background: "linear-gradient(135deg, #1a1d27, #0d1528)", border: `1px solid ${C.primary}30`, borderRadius: 10, padding: 14 }}>
        <div style={{ fontSize: 10, color: C.muted, marginBottom: 4 }}>Actas contadas</div>
        <div style={{ fontSize: 38, fontWeight: 800, color: C.primary, fontFamily: "IBM Plex Mono, monospace", lineHeight: 1 }}>
          {metrics.pctCo}<span style={{ fontSize: 18 }}>%</span>
        </div>
        <MiniBar pct={metrics.pctCo} color={C.primary} />
        <div style={{ fontSize: 11, color: C.muted, marginTop: 7 }}>
          {metrics.nCo} de {metrics.total} casillas
        </div>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
        <StatCard label="TOTAL" value={metrics.total} color={C.text} />
        <StatCard label="ABIERTAS" value={metrics.nAb} color={C.success} />
        <StatCard label="CERRADAS" value={metrics.nCe} color={C.neutral} />
        <StatCard label="PENDIENTES" value={metrics.nPe} color={C.warning} />
        <StatCard label="INCONSIST." value={metrics.nIn} color={C.danger} />
        <StatCard label="SIN COORDS" value={metrics.missingCoords} color={C.warning} />
      </div>
      <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 10, padding: 13 }}>
        <div style={{ fontSize: 10, fontWeight: 800, color: C.muted, letterSpacing: 1, marginBottom: 10, fontFamily: "IBM Plex Mono, monospace" }}>DISTRIBUCION</div>
        {Object.entries(STATUS).map(([k, v]) => {
          const n = metrics.byStatus[k] || 0;
          const p = metrics.total ? Math.round((n / metrics.total) * 100) : 0;
          return (
            <div key={k} style={{ marginBottom: 10 }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
                <span style={{ fontSize: 11, color: C.muted }}>{v.label}</span>
                <span style={{ fontSize: 11, color: v.color, fontFamily: "IBM Plex Mono, monospace" }}>{n} <span style={{ color: C.subtle }}>({p}%)</span></span>
              </div>
              <MiniBar pct={p} color={v.color} />
            </div>
          );
        })}
      </div>
      <div className="operational-summary-card" style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 10, padding: 13, fontSize: 12, color: C.muted, lineHeight: 1.6 }}>
        <div style={{ color: C.text, fontWeight: 800, marginBottom: 5 }}>Resumen operativo</div>
        <div>{metrics.coordsCount} registros pueden mostrarse en mapa.</div>
        <div>{metrics.missingCoords} conservan dirección oficial y requieren geocodificación.</div>
        <div>Votos registrados: <strong style={{ color: C.primary, fontFamily: "IBM Plex Mono, monospace" }}>{fmtNum(metrics.totalV)}</strong></div>
        <div>Ultima actualizacion: <strong style={{ color: C.text }}>{fmtTime(lastUpd)}</strong></div>
      </div>
    </aside>
  );
}

function ActaTraceDashboardLayout({ header, left, map, detail, right }) {
  return (
    <div className="dashboard-root" style={{ height: "100vh", background: C.bg, color: C.text, fontFamily: "IBM Plex Sans, sans-serif", display: "flex", flexDirection: "column", overflow: "hidden" }}>
      {header}
      <main className="dashboard-shell">
        {left}
        <section className="map-column">
          {map}
          {detail}
        </section>
        {right}
      </main>
    </div>
  );
}

export default function ActaTraceMapaDashboard() {
  const [casillas, setCasillas] = useState(mkCasillas);
  const [selected, setSelected] = useState(null);
  const [selectionWarning, setSelectionWarning] = useState("");
  const [search, setSearch] = useState("");
  const [filterStatus, setFilterStatus] = useState("Todos");
  const [intervalSec, setIntervalSec] = useState(60);
  const [cd, setCd] = useState(60);
  const [lastUpd, setLastUpd] = useState(new Date());
  const [updating, setUpdating] = useState(false);
  const [autoRef, setAutoRef] = useState(true);
  const [fileName, setFileName] = useState(null);
  const [pendingFile, setPendingFile] = useState(null);
  const [importResult, setImportResult] = useState(DEFAULT_IMPORT_RESULT);
  const [importError, setImportError] = useState("");
  const fileRef = useRef();
  const timerRef = useRef();

  const doRefresh = useCallback(() => {
    setUpdating(true);
    setTimeout(() => {
      setCasillas((prev) => prev.map((c) => {
        const r = Math.random();
        if (c.status === "abierta" && r < 0.14) return { ...c, status: "cerrada" };
        if (c.status === "cerrada" && r < 0.28) {
          const h = [...Array(20)].map(() => (~~(Math.random() * 16)).toString(16)).join("");
          return { ...c, status: "contada", votos_prep: c.votos_acta, hash: h };
        }
        if (c.status === "pendiente" && r < 0.15) return { ...c, status: "abierta" };
        return c;
      }));
      setLastUpd(new Date());
      setUpdating(false);
    }, 650);
  }, []);

  useEffect(() => {
    setCd(intervalSec);
  }, [intervalSec]);

  useEffect(() => {
    clearInterval(timerRef.current);
    if (!autoRef) return undefined;
    timerRef.current = setInterval(() => {
      setCd((prev) => {
        if (prev <= 1) {
          doRefresh();
          return intervalSec;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timerRef.current);
  }, [autoRef, intervalSec, doRefresh]);

  const handleFileSelection = (file) => {
    setImportError("");
    setImportResult(DEFAULT_IMPORT_RESULT);
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".csv")) {
      setPendingFile(null);
      setFileName(null);
      setImportError("Tipo de archivo invalido. Selecciona un archivo .csv.");
      return;
    }
    setPendingFile(file);
    setFileName(file.name);
  };

  const parsePendingCsv = () => {
    if (!pendingFile) return;

    Papa.parse(pendingFile, {
      header: true,
      skipEmptyLines: true,
      complete: ({ data, errors }) => {
        let failed = errors?.length || 0;
        let skipped = 0;
        let requiringGeocoding = 0;

        const parsed = data.reduce((acc, raw, i) => {
          const r = normalizeCsvRow(raw);
          const numero = cleanValue(r.numero);
          const municipio = cleanValue(r.municipio) || "Sin municipio";
          const direccion = cleanValue(r.direccion);
          const lat = parseNullableNumber(r.latitud);
          const lng = parseNullableNumber(r.longitud);
          const coordsOk = Number.isFinite(lat) && Number.isFinite(lng);

          if (!numero && !direccion && !cleanValue(r.id_casilla)) {
            skipped += 1;
            return acc;
          }

          const geocodingStatus = coordsOk ? "geocoded" : direccion ? "requires_review" : "not_geocoded";
          if (!coordsOk) requiringGeocoding += 1;

          acc.push({
            id: cleanValue(r.id_casilla) || `IEE-${String(i + 1).padStart(4, "0")}`,
            municipio,
            seccion: cleanValue(r.seccion) || "-",
            numero: numero || `${i + 1}`,
            direccion_original: direccion || undefined,
            direccion_normalizada: undefined,
            lat: coordsOk ? lat : null,
            lng: coordsOk ? lng : null,
            geocoding_status: geocodingStatus,
            geocoding_source: coordsOk ? "csv" : "unknown",
            status: safeStatus(cleanValue(r.estatus).toLowerCase()),
            votos_acta: parseNullableNumber(r.votos_acta),
            votos_prep: parseNullableNumber(r.votos_prep),
            hash: cleanValue(r.hash) || null,
            hora: cleanValue(r.hora) || "-",
          });
          return acc;
        }, []);

        if (parsed.length === 0) {
          failed += 1;
          setImportError("No se encontraron registros validos en el CSV.");
          setImportResult({ imported: 0, skipped, failed, requiringGeocoding });
          return;
        }

        setCasillas(parsed);
        setSelected(null);
        setSelectionWarning("");
        setImportResult({ imported: parsed.length, skipped, failed, requiringGeocoding });
        setLastUpd(new Date());
      },
      error: (error) => {
        setImportError(error?.message || "No fue posible leer el CSV.");
        setImportResult({ imported: 0, skipped: 0, failed: 1, requiringGeocoding: 0 });
      },
    });
  };

  const clearImport = () => {
    setPendingFile(null);
    setFileName(null);
    setImportError("");
    setImportResult(DEFAULT_IMPORT_RESULT);
    if (fileRef.current) fileRef.current.value = "";
  };

  const selectCasilla = (casilla) => {
    setSelected((current) => current?.id === casilla.id ? null : casilla);
    setSelectionWarning(hasCoords(casilla) ? "" : "Esta casilla aún no tiene coordenadas. Usa dirección oficial para geocodificar.");
  };

  const visible = useMemo(() => {
    const q = search.trim().toLowerCase();
    return casillas.filter((c) => {
      const statusOk = filterStatus === "Todos" || c.status === filterStatus;
      const searchOk = !q || [c.numero, c.seccion, c.municipio, c.id, c.direccion_original].some((v) => String(v || "").toLowerCase().includes(q));
      return statusOk && searchOk;
    });
  }, [casillas, filterStatus, search]);

  const metrics = useMemo(() => {
    const total = casillas.length;
    const byStatus = Object.fromEntries(Object.keys(STATUS).map((k) => [k, casillas.filter((c) => c.status === k).length]));
    const coordsCount = casillas.filter(hasCoords).length;
    const missingCoords = total - coordsCount;
    const nCo = byStatus.contada || 0;
    return {
      total,
      byStatus,
      nAb: byStatus.abierta || 0,
      nCe: byStatus.cerrada || 0,
      nCo,
      nPe: byStatus.pendiente || 0,
      nIn: byStatus.inconsistencia || 0,
      pctCo: total ? Math.round((nCo / total) * 100) : 0,
      coordsCount,
      missingCoords,
      totalV: casillas.filter((c) => c.votos_acta && c.status !== "pendiente").reduce((sum, c) => sum + (c.votos_acta || 0), 0),
    };
  }, [casillas]);

  return (
    <>
      <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;600;700;800&family=IBM+Plex+Mono:wght@400;500;700&display=swap" rel="stylesheet" />
      <style>{`
        * { box-sizing: border-box; margin: 0; padding: 0; }
        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #2a2f47; border-radius: 2px; }
        @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.32} }
        .pulse-dot { animation: blink 1.4s ease-in-out infinite; }
        select option { background: #14161c; }
        .app-header {
          background: ${C.surface};
          border-bottom: 1px solid ${C.border};
          padding: 0 20px;
          min-height: 56px;
          display: flex;
          align-items: center;
          gap: 16px;
          flex-shrink: 0;
        }
        .header-status {
          display: flex;
          gap: 12px;
          align-items: center;
          font-size: 11px;
          flex-wrap: wrap;
        }
        .header-controls {
          display: flex;
          gap: 9px;
          align-items: center;
          margin-left: auto;
          flex-wrap: wrap;
        }
        .dashboard-shell {
          flex: 1;
          min-height: 0;
          display: grid;
          grid-template-columns: minmax(380px, 440px) minmax(420px, 1fr) minmax(280px, 320px);
          overflow: hidden;
        }
        .left-sidebar {
          background: ${C.surface};
          border-right: 1px solid ${C.border};
          min-width: 0;
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }
        .captured-list {
          flex: 0 0 auto;
          max-height: calc((108px * 3) + (9px * 2) + 24px);
          min-height: 0;
          overflow-y: auto;
          padding: 12px;
          display: flex;
          flex-direction: column;
          gap: 9px;
        }
        .captured-item {
          width: 100%;
          text-align: left;
          border-radius: 8px;
          padding: 9px 11px;
          cursor: pointer;
          font-family: IBM Plex Sans, sans-serif;
          min-height: 108px;
          max-height: 108px;
          overflow: hidden;
          transition: background 0.15s, border 0.15s;
        }
        .captured-item:hover { background: #1a6eff12 !important; }
        .official-address {
          display: -webkit-box;
          -webkit-line-clamp: 1;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
        .csv-dock {
          border-top: 1px solid ${C.border};
          padding: 12px;
          flex-shrink: 0;
          background: ${C.surface};
          display: grid;
          grid-template-columns: 0.9fr 1.1fr;
          gap: 10px;
          align-items: stretch;
        }
        .footer-casilla-summary {
          background: ${C.card};
          border: 1px solid ${C.border};
          border-radius: 10px;
          padding: 11px 12px;
          min-width: 0;
        }
        .footer-casilla-summary .status-badge,
        .csv-panel .status-badge {
          max-width: 100%;
        }
        .csv-panel {
          background: #0d1528;
          border: 1px solid ${C.primary}30;
          border-radius: 10px;
          padding: 11px 12px;
          min-width: 0;
        }
        .csv-columns-hint {
          max-height: 38px;
          overflow: hidden;
        }
        .map-column {
          min-width: 0;
          min-height: 0;
          display: flex;
          flex-direction: column;
          gap: 12px;
          padding: 16px;
          overflow: hidden;
        }
        .map-panel {
          flex: 1;
          min-height: 380px;
          background: ${C.panel};
          border: 1px solid ${C.border};
          border-radius: 12px;
          position: relative;
          overflow: hidden;
        }
        .plotly-map {
          position: absolute;
          inset: 0;
          width: 100%;
          height: 100%;
        }
        .plotly-map .maplibregl-ctrl-bottom-left,
        .plotly-map .maplibregl-ctrl-bottom-right {
          opacity: 0.55;
        }
        .map-counter {
          position: absolute;
          top: 12px;
          left: 34px;
          background: #0f1015cc;
          border: 1px solid ${C.border};
          border-radius: 7px;
          padding: 5px 9px;
          color: ${C.muted};
          font-size: 10px;
          font-family: IBM Plex Mono, monospace;
        }
        .map-legend {
          position: absolute;
          bottom: 12px;
          left: 12px;
          right: 12px;
          background: #0f1015cc;
          border: 1px solid ${C.border};
          border-radius: 8px;
          padding: 8px 10px;
          display: flex;
          gap: 10px;
          flex-wrap: wrap;
          backdrop-filter: blur(4px);
        }
        .legend-button {
          display: flex;
          align-items: center;
          gap: 5px;
          font-size: 10px;
          color: ${C.muted};
          cursor: pointer;
          background: transparent;
          border: 0;
          font-family: IBM Plex Sans, sans-serif;
        }
        .right-panel {
          background: ${C.surface};
          border-left: 1px solid ${C.border};
          padding: 14px;
          overflow-y: auto;
          display: flex;
          flex-direction: column;
          gap: 12px;
          min-width: 0;
        }
        .operational-summary-card {
          margin-top: auto;
        }
        @media (max-width: 1120px) {
          .dashboard-shell {
            grid-template-columns: minmax(320px, 380px) minmax(420px, 1fr);
          }
          .right-panel {
            display: none;
          }
        }
        @media (max-width: 820px) {
          .dashboard-root {
            height: auto !important;
            min-height: 100vh !important;
            overflow: visible !important;
          }
          .app-header {
            align-items: flex-start;
            padding: 12px;
            flex-direction: column;
          }
          .header-controls {
            margin-left: 0;
            width: 100%;
          }
          .dashboard-shell {
            display: flex;
            flex-direction: column;
            overflow: visible;
          }
          .left-sidebar {
            order: 1;
            border-right: 0;
            border-bottom: 1px solid ${C.border};
            max-height: none;
          }
          .captured-list {
            max-height: calc((108px * 3) + (9px * 2) + 24px);
          }
          .csv-dock {
            border-top: 1px solid ${C.border};
            grid-template-columns: 1fr;
          }
          .map-column {
            order: 2;
            overflow: visible;
            padding: 12px;
          }
          .map-panel {
            min-height: 420px;
          }
          .right-panel {
            order: 3;
            display: flex;
            border-left: 0;
            border-top: 1px solid ${C.border};
          }
          .operational-summary-card {
            margin-top: 0;
          }
          .map-counter {
            top: 38px;
            left: 12px;
            right: 12px;
          }
        }
      `}</style>
      <input ref={fileRef} type="file" accept=".csv" style={{ display: "none" }} onChange={(e) => handleFileSelection(e.target.files?.[0])} />
      <ActaTraceDashboardLayout
        header={
          <Header
            metrics={metrics}
            lastUpd={lastUpd}
            updating={updating}
            autoRef={autoRef}
            setAutoRef={setAutoRef}
            intervalSec={intervalSec}
            setIntervalSec={setIntervalSec}
            cd={cd}
            onManualRefresh={() => {
              doRefresh();
              setCd(intervalSec);
            }}
          />
        }
        left={
          <CapturedCasillasSidebar
            records={visible}
            selected={selected}
            onSelect={selectCasilla}
            search={search}
            setSearch={setSearch}
            filterStatus={filterStatus}
            setFilterStatus={setFilterStatus}
          >
            <IeeCsvUploadPanel
              fileName={fileName}
              importResult={importResult}
              importError={importError}
              hasPendingFile={Boolean(pendingFile)}
              onSelectClick={() => fileRef.current?.click()}
              onLoad={parsePendingCsv}
              onClear={clearImport}
            />
          </CapturedCasillasSidebar>
        }
        map={
          <ChihuahuaSvgMap
            records={casillas}
            visibleRecords={visible}
            selected={selected}
            onSelect={selectCasilla}
            filterStatus={filterStatus}
            setFilterStatus={setFilterStatus}
            metrics={metrics}
          />
        }
        detail={<SelectedCasillaDetail selected={selected} warning={selectionWarning} onClose={() => { setSelected(null); setSelectionWarning(""); }} />}
        right={<MetricsPanel metrics={metrics} lastUpd={lastUpd} />}
      />
    </>
  );
}
