
import { useState, useEffect, useCallback, useRef } from "react";
import Papa from "papaparse";

// ─── Design tokens ────────────────────────────────────────────────────────────
const C = {
  bg: "#07080a", surface: "#0f1015", panel: "#14161c", card: "#1a1d27",
  border: "#1e2133", borderHi: "#2a2f47",
  primary: "#1a6eff", primaryDim: "#1a6eff20",
  success: "#00d68f", successDim: "#00d68f20",
  warning: "#ffb938", warningDim: "#ffb93820",
  danger: "#ff3d5a", dangerDim: "#ff3d5a20",
  info: "#7c6aff", infoDim: "#7c6aff20",
  neutral: "#4b5572", neutralDim: "#4b557220",
  text: "#f0f2ff", muted: "#7880a0", subtle: "#3d4460",
};

const STATUS = {
  abierta:        { color: C.success,  dim: C.successDim,  label: "Abierta",         pulse: true  },
  cerrada:        { color: C.neutral,  dim: C.neutralDim,  label: "Cerrada",          pulse: false },
  contada:        { color: C.primary,  dim: C.primaryDim,  label: "Contada",          pulse: false },
  pendiente:      { color: C.warning,  dim: C.warningDim,  label: "Pendiente",        pulse: false },
  inconsistencia: { color: C.danger,   dim: C.dangerDim,   label: "Inconsistencia",   pulse: true  },
};

// ─── Chihuahua SVG map ────────────────────────────────────────────────────────
// Coordinate system: lng 103°–109°W, lat 25°–32°N → 380×500 px
const W = 380, H = 500;
const project = (lng, lat) => [
  Math.round((109 - lng) / 6 * W),
  Math.round((32  - lat) / 7 * H),
];

// Simplified Chihuahua state outline
const STATE_PTS = [
  [0,16],[34,13],[68,11],[102,11],[136,12],[168,16],[198,20],
  [228,26],[256,33],[280,52],[304,70],[326,88],[344,114],
  [356,144],[364,176],[367,210],[368,246],[368,280],[362,310],
  [350,340],[338,364],[332,390],[318,410],[300,428],[278,448],
  [256,462],[232,466],[208,466],[186,462],[164,453],[142,444],
  [120,432],[100,416],[84,398],[68,378],[50,356],[34,334],
  [18,314],[6,296],[0,280],[0,246],[0,212],[0,178],
  [0,144],[0,110],[0,76],[0,42],[0,16],
].map(p => p.join(",")).join(" ");

// Latitude grid labels
const LAT_LINES = [26, 27, 28, 29, 30, 31];
const LNG_LINES = [104, 105, 106, 107, 108];

// Municipality anchor points
const MUNS = [
  { name: "Cd. Juárez",          lat: 31.73, lng: 106.49, r: 0.28, n: 26, abbr: "Juárez"     },
  { name: "Chihuahua",           lat: 28.63, lng: 106.07, r: 0.22, n: 18, abbr: "Chih."      },
  { name: "Delicias",            lat: 28.19, lng: 105.47, r: 0.13, n:  7, abbr: "Delicias"   },
  { name: "Cuauhtémoc",          lat: 28.41, lng: 106.86, r: 0.14, n:  7, abbr: "Cuauhtémoc" },
  { name: "Parral",              lat: 26.93, lng: 105.67, r: 0.13, n:  6, abbr: "Parral"     },
  { name: "Nuevo Casas Grandes", lat: 30.41, lng: 107.91, r: 0.18, n:  5, abbr: "NCG"        },
  { name: "Ojinaga",             lat: 29.56, lng: 104.41, r: 0.10, n:  4, abbr: "Ojinaga"    },
  { name: "Camargo",             lat: 27.68, lng: 105.17, r: 0.10, n:  4, abbr: "Camargo"    },
  { name: "Creel",               lat: 27.75, lng: 107.63, r: 0.08, n:  3, abbr: "Creel"      },
  { name: "Jiménez",             lat: 27.13, lng: 104.92, r: 0.08, n:  2, abbr: "Jiménez"    },
];

// ─── Mock data generator (seeded RNG for stability) ───────────────────────────
const SEQ = ["abierta","abierta","abierta","cerrada","cerrada","contada",
             "contada","contada","pendiente","inconsistencia"];

function mkCasillas() {
  let s = 99991;
  const r = () => { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646; };
  const hex = (n=8) => [...Array(n)].map(()=>(~~(r()*16)).toString(16)).join("");
  const out = [];
  let id = 1;
  for (const m of MUNS) {
    for (let i = 0; i < m.n; i++) {
      const lat = m.lat + (r() - 0.5) * m.r * 2;
      const lng = m.lng + (r() - 0.5) * m.r * 2;
      const st  = SEQ[Math.floor(r() * SEQ.length)];
      const va  = Math.floor(r() * 340) + 60;
      const inc = st === "inconsistencia" ? Math.floor(r() * 5) + 1 : 0;
      out.push({
        id: `CHH-${String(id).padStart(4, "0")}`,
        municipio: m.name,
        seccion: Math.floor(r() * 900) + 100,
        numero: `${Math.floor(r() * 2000) + 500}-${["A","B","C"][Math.floor(r()*3)]}`,
        lat, lng,
        status: st,
        votos_acta: va,
        votos_prep: st === "inconsistencia" ? va + inc
                  : ["contada","cerrada"].includes(st) ? va : null,
        hash: ["contada","inconsistencia"].includes(st) ? hex(20) : null,
        hora: `${String(7+Math.floor(r()*11)).padStart(2,"0")}:${String(Math.floor(r()*60)).padStart(2,"0")}`,
      });
      id++;
    }
  }
  return out;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────
const fmtTime = d => d.toLocaleTimeString("es-MX",{hour:"2-digit",minute:"2-digit",second:"2-digit"});
const fmtCd   = s => `${String(Math.floor(s/60)).padStart(2,"0")}:${String(s%60).padStart(2,"0")}`;
const fmtNum  = n => Number(n).toLocaleString("es-MX");

// ─── Sub-components ───────────────────────────────────────────────────────────
const Chip = ({ color, children }) => (
  <span style={{
    background: color + "25", color, border: `1px solid ${color}40`,
    borderRadius: 4, padding: "2px 8px",
    fontSize: 10, fontWeight: 700, letterSpacing: 0.5,
    fontFamily: "IBM Plex Mono, monospace",
  }}>{children}</span>
);

const MiniBar = ({ pct, color }) => (
  <div style={{ background: C.border, borderRadius: 3, height: 4, marginTop: 5 }}>
    <div style={{ background: color, borderRadius: 3, height: 4, width: `${pct}%`, transition: "width 0.6s ease" }} />
  </div>
);

const StatCard = ({ label, value, color, sub }) => (
  <div style={{
    background: C.card, border: `1px solid ${C.border}`,
    borderRadius: 10, padding: "12px 14px",
  }}>
    <div style={{ fontSize: 10, color: C.muted, marginBottom: 6, letterSpacing: 0.5 }}>{label}</div>
    <div style={{ fontSize: 26, fontWeight: 800, color, fontFamily: "IBM Plex Mono, monospace", lineHeight: 1 }}>{value}</div>
    {sub && <div style={{ fontSize: 10, color: C.muted, marginTop: 4 }}>{sub}</div>}
  </div>
);

const Sel = ({ value, onChange, options, style = {} }) => (
  <select value={value} onChange={e => onChange(e.target.value)} style={{
    background: C.card, border: `1px solid ${C.border}`, color: C.text,
    borderRadius: 6, padding: "5px 10px", fontSize: 12,
    fontFamily: "IBM Plex Sans, sans-serif", outline: "none",
    cursor: "pointer", ...style,
  }}>
    {options.map(o => <option key={o.v || o} value={o.v || o}>{o.l || o}</option>)}
  </select>
);

// ─── Main Component ───────────────────────────────────────────────────────────
export default function ActaTraceMapaDashboard() {
  const [casillas,    setCasillas]    = useState(mkCasillas);
  const [hovered,     setHovered]     = useState(null);
  const [selected,    setSelected]    = useState(null);
  const [fMun,        setFMun]        = useState("Todos");
  const [fStat,       setFStat]       = useState("Todos");
  const [intervalSec, setIntervalSec] = useState(60);
  const [cd,          setCd]          = useState(60);
  const [lastUpd,     setLastUpd]     = useState(new Date());
  const [updating,    setUpdating]    = useState(false);
  const [autoRef,     setAutoRef]     = useState(true);
  const [fileName,    setFileName]    = useState(null);
  const [tick,        setTick]        = useState(0); // for pulsing dots
  const fileRef  = useRef();
  const timerRef = useRef();

  // Pulse animation tick
  useEffect(() => {
    const t = setInterval(() => setTick(p => p + 1), 1200);
    return () => clearInterval(t);
  }, []);

  // Simulate data refresh
  const doRefresh = useCallback(() => {
    setUpdating(true);
    setTimeout(() => {
      setCasillas(prev => prev.map(c => {
        const r = Math.random();
        if (c.status === "abierta"  && r < 0.14) return { ...c, status: "cerrada" };
        if (c.status === "cerrada"  && r < 0.28) {
          const h = [...Array(20)].map(() => (~~(Math.random()*16)).toString(16)).join("");
          return { ...c, status: "contada", votos_prep: c.votos_acta, hash: h };
        }
        if (c.status === "pendiente" && r < 0.15) return { ...c, status: "abierta" };
        return c;
      }));
      setLastUpd(new Date());
      setUpdating(false);
    }, 650);
  }, []);

  // Countdown + auto-refresh
  useEffect(() => {
    setCd(intervalSec);
  }, [intervalSec]);

  useEffect(() => {
    clearInterval(timerRef.current);
    if (!autoRef) return;
    timerRef.current = setInterval(() => {
      setCd(prev => {
        if (prev <= 1) { doRefresh(); return intervalSec; }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timerRef.current);
  }, [autoRef, intervalSec, doRefresh]);

  // CSV upload from IEE
  const handleFile = (file) => {
    if (!file) return;
    Papa.parse(file, {
      header: true, skipEmptyLines: true,
      complete: ({ data }) => {
        const parsed = data
          .filter(r => r.latitud || r.lat)
          .map((r, i) => ({
            id: r.id_casilla || r.id || `IEE-${String(i+1).padStart(4,"0")}`,
            municipio: r.municipio || "Sin municipio",
            seccion:   parseInt(r.seccion)  || 0,
            numero:    r.numero || r.casilla || `${i+1}`,
            lat:       parseFloat(r.latitud  || r.lat),
            lng:       parseFloat(r.longitud || r.lng),
            status:    "pendiente",
            votos_acta: null, votos_prep: null, hash: null,
            hora: "—",
          }));
        if (parsed.length > 0) {
          setCasillas(parsed);
          setFileName(file.name);
          setLastUpd(new Date());
          setSelected(null);
          setFMun("Todos");
        }
      },
    });
  };

  // Computed metrics
  const total   = casillas.length;
  const bySt    = k => casillas.filter(c => c.status === k).length;
  const nAb     = bySt("abierta");
  const nCe     = bySt("cerrada");
  const nCo     = bySt("contada");
  const nPe     = bySt("pendiente");
  const nIn     = bySt("inconsistencia");
  const pctCo   = total ? Math.round(nCo / total * 100) : 0;
  const pctCov  = total ? Math.round((nCo + nCe + nIn) / total * 100) : 0;
  const totalV  = casillas.filter(c => c.votos_acta && c.status !== "pendiente")
                          .reduce((s, c) => s + (c.votos_acta || 0), 0);

  // Filters
  const munList = ["Todos", ...MUNS.map(m => m.name)];
  const stList  = [{ v:"Todos", l:"Todos los estados" }, ...Object.entries(STATUS).map(([k,v])=>({v:k,l:v.label}))];
  const visible = casillas.filter(c =>
    (fMun  === "Todos" || c.municipio === fMun) &&
    (fStat === "Todos" || c.status    === fStat)
  );

  const glowing = tick % 2 === 0;

  return (
    <>
      <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;600;700;800&family=IBM+Plex+Mono:wght@400;500;700&display=swap" rel="stylesheet"/>
      <style>{`
        * { box-sizing: border-box; margin: 0; padding: 0; }
        ::-webkit-scrollbar { width: 4px; } ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #2a2f47; border-radius: 2px; }
        @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }
        @keyframes spin { to{transform:rotate(360deg)} }
        .pulse-dot { animation: blink 1.4s ease-in-out infinite; }
        .spin { animation: spin 1s linear infinite; }
        select option { background: #14161c; }
        .casilla-row:hover { background: #1a6eff12 !important; }
        .mun-row:hover { background: #1a1d27 !important; }
      `}</style>

      <div style={{ minHeight:"100vh", background:C.bg, color:C.text, fontFamily:"IBM Plex Sans, sans-serif", display:"flex", flexDirection:"column" }}>

        {/* ── Header ─────────────────────────────────────────────────────────── */}
        <header style={{ background:C.surface, borderBottom:`1px solid ${C.border}`, padding:"0 20px", height:52, display:"flex", alignItems:"center", gap:16, flexShrink:0 }}>
          <div style={{ display:"flex", alignItems:"center", gap:10, flexShrink:0 }}>
            <svg width="30" height="30" viewBox="0 0 30 30">
              <rect width="30" height="30" rx="7" fill={C.primary}/>
              <path d="M7 15 L15 7 L23 15 L15 23 Z" fill="none" stroke="#fff" strokeWidth="2"/>
              <circle cx="15" cy="15" r="3.5" fill="#fff"/>
            </svg>
            <div>
              <div style={{ fontWeight:800, fontSize:14, letterSpacing:-0.3, lineHeight:1.1 }}>ActaTrace</div>
              <div style={{ fontSize:9, color:C.muted, letterSpacing:1, fontFamily:"IBM Plex Mono, monospace" }}>MAPA ELECTORAL · IEE CHIHUAHUA</div>
            </div>
          </div>

          <div style={{ width:1, height:28, background:C.border, flexShrink:0 }}/>

          {/* Status indicators */}
          <div style={{ display:"flex", gap:14, alignItems:"center" }}>
            <div style={{ display:"flex", alignItems:"center", gap:5 }}>
              <div style={{ width:6, height:6, borderRadius:"50%", background:C.success }} className="pulse-dot"/>
              <span style={{ fontSize:11, color:C.muted }}>
                {nAb} abiertas
              </span>
            </div>
            <div style={{ fontSize:11, color:C.muted }}>
              <span style={{ color:C.primary, fontWeight:700, fontFamily:"IBM Plex Mono, monospace" }}>{pctCo}%</span> contadas
            </div>
            {nIn > 0 && (
              <div style={{ display:"flex", alignItems:"center", gap:5, background:C.dangerDim, border:`1px solid ${C.danger}40`, borderRadius:4, padding:"2px 8px" }}>
                <div style={{ width:5, height:5, borderRadius:"50%", background:C.danger }} className="pulse-dot"/>
                <span style={{ fontSize:11, color:C.danger, fontWeight:700 }}>{nIn} inconsistencias</span>
              </div>
            )}
          </div>

          {/* Right controls */}
          <div style={{ display:"flex", gap:10, alignItems:"center", marginLeft:"auto", flexWrap:"wrap" }}>
            {fileName && (
              <span style={{ fontSize:10, color:C.success, fontFamily:"IBM Plex Mono, monospace", background:C.successDim, border:`1px solid ${C.success}40`, padding:"3px 8px", borderRadius:4 }}>
                ✓ {fileName}
              </span>
            )}

            <span style={{ fontSize:11, color:C.muted }}>
              {updating
                ? <span style={{ color:C.warning }}>⟳ Actualizando…</span>
                : `Actualizado ${fmtTime(lastUpd)}`
              }
            </span>

            {autoRef && !updating && (
              <span style={{ fontSize:11, color:C.subtle, fontFamily:"IBM Plex Mono, monospace", background:C.panel, border:`1px solid ${C.border}`, padding:"3px 8px", borderRadius:4 }}>
                ⏱ {fmtCd(cd)}
              </span>
            )}

            <Sel
              value={intervalSec}
              onChange={v => setIntervalSec(+v)}
              options={[{v:30,l:"30s"},{v:60,l:"1 min"},{v:120,l:"2 min"},{v:300,l:"5 min"}]}
            />

            <button onClick={() => setAutoRef(a => !a)} style={{
              background: autoRef ? C.successDim : C.panel,
              border: `1px solid ${autoRef ? C.success + "50" : C.border}`,
              color: autoRef ? C.success : C.muted,
              borderRadius: 6, padding: "5px 12px", fontSize: 11,
              cursor: "pointer", fontFamily: "IBM Plex Sans, sans-serif", fontWeight: 600,
            }}>
              {autoRef ? "⏸ Auto" : "▶ Auto"}
            </button>

            <button onClick={() => { doRefresh(); setCd(intervalSec); }} style={{
              background: C.primary, border: "none", color: "#fff",
              borderRadius: 6, padding: "5px 14px", fontSize: 11,
              cursor: "pointer", fontWeight: 700, fontFamily: "IBM Plex Sans, sans-serif",
            }}>
              ⟳ Actualizar
            </button>
          </div>
        </header>

        {/* ── Main layout ────────────────────────────────────────────────────── */}
        <div style={{ flex:1, display:"grid", gridTemplateColumns:"1fr 320px", overflow:"hidden" }}>

          {/* ── MAP COLUMN ─────────────────────────────────────────────────── */}
          <div style={{ display:"flex", flexDirection:"column", gap:12, padding:16, overflow:"hidden" }}>

            {/* Filter bar */}
            <div style={{ display:"flex", gap:10, alignItems:"center", flexWrap:"wrap", flexShrink:0 }}>
              <span style={{ fontSize:11, color:C.muted }}>Municipio:</span>
              <Sel value={fMun}  onChange={setFMun}  options={munList} />
              <span style={{ fontSize:11, color:C.muted }}>Estado:</span>
              <Sel value={fStat} onChange={setFStat} options={stList} />

              <div style={{ marginLeft:"auto", display:"flex", gap:8, alignItems:"center" }}>
                <span style={{ fontSize:11, color:C.subtle }}>{visible.length} casillas visibles</span>
                <input ref={fileRef} type="file" accept=".csv" style={{ display:"none" }} onChange={e => handleFile(e.target.files[0])} />
                <button onClick={() => fileRef.current?.click()} style={{
                  background: C.card, border: `1px solid ${C.borderHi}`,
                  color: C.muted, borderRadius: 6, padding: "5px 12px",
                  fontSize: 11, cursor: "pointer", fontFamily: "IBM Plex Sans, sans-serif",
                  display: "flex", alignItems: "center", gap: 5,
                }}>
                  📄 Cargar CSV IEE
                </button>
              </div>
            </div>

            {/* MAP */}
            <div style={{ flex:1, background:C.panel, borderRadius:14, border:`1px solid ${C.border}`, position:"relative", overflow:"hidden", minHeight:380 }}>

              {/* Map background glow */}
              <div style={{ position:"absolute", inset:0, background:`radial-gradient(ellipse at 40% 45%, #1a6eff08, transparent 70%)`, pointerEvents:"none" }}/>

              <svg
                viewBox={`0 0 ${W} ${H}`}
                style={{ width:"100%", height:"100%", display:"block" }}
                preserveAspectRatio="xMidYMid meet"
              >
                <defs>
                  <filter id="glow">
                    <feGaussianBlur stdDeviation="2" result="blur"/>
                    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
                  </filter>
                </defs>

                {/* State fill */}
                <polygon points={STATE_PTS} fill="#111828" stroke="#1a6eff30" strokeWidth="1.5"/>

                {/* Latitude grid */}
                {LAT_LINES.map(lat => {
                  const [,y] = project(106, lat);
                  return <line key={lat} x1="0" y1={y} x2={W} y2={y} stroke="#ffffff05" strokeWidth="0.8"/>;
                })}
                {LNG_LINES.map(lng => {
                  const [x] = project(lng, 28);
                  return <line key={lng} x1={x} y1="0" x2={x} y2={H} stroke="#ffffff05" strokeWidth="0.8"/>;
                })}

                {/* Grid labels */}
                {LAT_LINES.map(lat => {
                  const [,y] = project(103.2, lat);
                  return <text key={lat} x={W-4} y={y+3} fontSize="7" fill="#3d4460" textAnchor="end" fontFamily="IBM Plex Mono, monospace">{lat}°N</text>;
                })}

                {/* Municipality name labels */}
                {MUNS.slice(0, 7).map(m => {
                  const [x, y] = project(m.lng, m.lat);
                  return (
                    <text key={m.name} x={x} y={y - 10} textAnchor="middle"
                          fontSize="8" fill="#3d4460" fontFamily="IBM Plex Sans, sans-serif">
                      {m.abbr}
                    </text>
                  );
                })}

                {/* Casilla dots */}
                {visible.map(c => {
                  const [x, y] = project(c.lng, c.lat);
                  const cfg    = STATUS[c.status];
                  const isHov  = hovered?.id  === c.id;
                  const isSel  = selected?.id  === c.id;
                  const isPulse = cfg.pulse && glowing;
                  return (
                    <g key={c.id}
                       onClick={() => setSelected(s => s?.id === c.id ? null : c)}
                       onMouseEnter={() => setHovered(c)}
                       onMouseLeave={() => setHovered(null)}
                       style={{ cursor: "pointer" }}>
                      {/* Outer ring for pulse/select */}
                      {(isHov || isSel || isPulse) && (
                        <circle cx={x} cy={y} r={isHov||isSel ? 9 : 7}
                                fill="none" stroke={cfg.color}
                                strokeWidth="1" opacity={isPulse&&!isHov&&!isSel ? 0.4 : 0.6}/>
                      )}
                      {/* Main dot */}
                      <circle cx={x} cy={y} r={isSel ? 5 : isHov ? 4.5 : 4}
                              fill={cfg.color}
                              opacity={isSel ? 1 : isHov ? 1 : 0.82}
                              filter={isSel||isHov ? "url(#glow)" : "none"}/>
                      {/* Selection indicator */}
                      {isSel && <circle cx={x} cy={y} r="2" fill="#fff"/>}
                    </g>
                  );
                })}

                {/* SVG Tooltip */}
                {hovered && (() => {
                  const [x, y] = project(hovered.lng, hovered.lat);
                  const cfg = STATUS[hovered.status];
                  const tx  = x > W * 0.65 ? x - 145 : x + 10;
                  const ty  = y > H * 0.72 ? y - 100 : y + 10;
                  return (
                    <g>
                      <rect x={tx} y={ty} width={138} height={96} rx="7"
                            fill="#0f1015" stroke={cfg.color} strokeWidth="0.8" opacity="0.98"/>
                      {/* Casilla number */}
                      <text x={tx+10} y={ty+17} fontSize="11" fill={cfg.color}
                            fontWeight="700" fontFamily="IBM Plex Mono, monospace">
                        {hovered.numero}
                      </text>
                      {/* Municipio */}
                      <text x={tx+10} y={ty+30} fontSize="9" fill="#7880a0"
                            fontFamily="IBM Plex Sans, sans-serif">
                        {hovered.municipio} · Secc. {hovered.seccion}
                      </text>
                      {/* Status chip */}
                      <rect x={tx+10} y={ty+36} width={58} height={13} rx="3" fill={cfg.color+"25"}/>
                      <text x={tx+14} y={ty+46} fontSize="8" fill={cfg.color}
                            fontWeight="700" fontFamily="IBM Plex Mono, monospace">
                        {cfg.label.toUpperCase()}
                      </text>
                      {/* Divider */}
                      <line x1={tx+10} y1={ty+55} x2={tx+128} y2={ty+55} stroke="#1e2133" strokeWidth="0.5"/>
                      {/* Votos */}
                      <text x={tx+10} y={ty+68} fontSize="9" fill="#f0f2ff"
                            fontFamily="IBM Plex Sans, sans-serif">
                        Acta: {hovered.votos_acta ?? "—"} · PREP: {hovered.votos_prep ?? "—"}
                      </text>
                      {/* Hash */}
                      <text x={tx+10} y={ty+82} fontSize="8" fill="#3d4460"
                            fontFamily="IBM Plex Mono, monospace">
                        {hovered.hash ? `${hovered.hash.substr(0,18)}…` : "Sin hash registrado"}
                      </text>
                      {/* Hora */}
                      <text x={tx+10} y={ty+93} fontSize="8" fill="#3d4460"
                            fontFamily="IBM Plex Mono, monospace">
                        Hora: {hovered.hora}
                      </text>
                    </g>
                  );
                })()}
              </svg>

              {/* Legend overlay */}
              <div style={{
                position:"absolute", bottom:12, left:12,
                background:"#0f1015cc", border:`1px solid ${C.border}`,
                borderRadius:8, padding:"8px 12px",
                display:"flex", gap:14, flexWrap:"wrap",
                backdropFilter:"blur(4px)",
              }}>
                {Object.entries(STATUS).map(([k, v]) => {
                  const count = casillas.filter(c => c.status === k).length;
                  return (
                    <div key={k} onClick={() => setFStat(fStat === k ? "Todos" : k)}
                         style={{ display:"flex", alignItems:"center", gap:5, fontSize:10, color:C.muted, cursor:"pointer" }}>
                      <div style={{ width:8, height:8, borderRadius:"50%", background:v.color, flexShrink:0 }}/>
                      <span>{v.label}</span>
                      <span style={{ color:v.color, fontWeight:700, fontFamily:"IBM Plex Mono, monospace" }}>{count}</span>
                    </div>
                  );
                })}
              </div>

              {/* North indicator */}
              <div style={{ position:"absolute", top:12, left:12, color:C.subtle, fontSize:10, fontFamily:"IBM Plex Mono, monospace" }}>
                ▲ N
              </div>

              {/* Scale label */}
              <div style={{ position:"absolute", top:12, right:12, color:C.subtle, fontSize:9, fontFamily:"IBM Plex Mono, monospace" }}>
                IEE Chihuahua · 2026
              </div>
            </div>

            {/* ── Selected casilla detail card ─────────────────────────────── */}
            {selected && (
              <div style={{
                background: C.card,
                border: `1px solid ${STATUS[selected.status].color}50`,
                borderRadius: 10, padding: "14px 16px",
                display: "flex", gap: 16, alignItems: "flex-start",
                flexShrink: 0,
              }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display:"flex", alignItems:"center", gap:10, marginBottom:8 }}>
                    <span style={{ fontFamily:"IBM Plex Mono, monospace", fontSize:15, fontWeight:700 }}>
                      Casilla {selected.numero}
                    </span>
                    <Chip color={STATUS[selected.status].color}>{STATUS[selected.status].label.toUpperCase()}</Chip>
                  </div>
                  <div style={{ display:"flex", gap:24, fontSize:12, color:C.muted, marginBottom:8 }}>
                    <span>{selected.municipio}</span>
                    <span>Sección {selected.seccion}</span>
                    <span>ID: {selected.id}</span>
                    <span>Registrada: {selected.hora}</span>
                  </div>
                  <div style={{ display:"flex", gap:24, fontSize:13 }}>
                    <span>Votos acta:
                      <strong style={{ fontFamily:"IBM Plex Mono, monospace", marginLeft:6, color:C.text }}>
                        {selected.votos_acta ?? "—"}
                      </strong>
                    </span>
                    <span>Votos PREP:
                      <strong style={{
                        fontFamily:"IBM Plex Mono, monospace", marginLeft:6,
                        color: selected.status === "inconsistencia" ? C.danger : C.text,
                      }}>
                        {selected.votos_prep ?? "—"}
                      </strong>
                    </span>
                    {selected.status === "inconsistencia" && (
                      <span style={{ color:C.danger, fontSize:11 }}>
                        ⚠ Δ{Math.abs((selected.votos_prep||0)-(selected.votos_acta||0))} votos
                      </span>
                    )}
                  </div>
                  {selected.hash && (
                    <div style={{ marginTop:8, fontFamily:"IBM Plex Mono, monospace", fontSize:10, color:C.success }}>
                      SHA-256: {selected.hash}…
                    </div>
                  )}
                </div>
                <button onClick={() => setSelected(null)} style={{
                  background:"none", border:"none", color:C.subtle, cursor:"pointer", fontSize:16, flexShrink:0,
                }}>✕</button>
              </div>
            )}
          </div>

          {/* ── DASHBOARD SIDEBAR ──────────────────────────────────────────── */}
          <aside style={{
            background: C.surface, borderLeft: `1px solid ${C.border}`,
            padding: 14, overflowY: "auto", display: "flex",
            flexDirection: "column", gap: 12,
          }}>

            {/* Header label */}
            <div style={{ fontSize:10, fontWeight:700, color:C.muted, letterSpacing:1.5, fontFamily:"IBM Plex Mono, monospace" }}>
              MÉTRICAS EN TIEMPO REAL
            </div>

            {/* Main cobertura */}
            <div style={{
              background: `linear-gradient(135deg, ${C.card}, #0d1528)`,
              border: `1px solid ${C.primary}30`,
              borderRadius: 12, padding: 16,
            }}>
              <div style={{ fontSize:10, color:C.muted, marginBottom:4 }}>Actas contadas</div>
              <div style={{ fontSize:44, fontWeight:800, color:C.primary, fontFamily:"IBM Plex Mono, monospace", lineHeight:1 }}>
                {pctCo}<span style={{ fontSize:20 }}>%</span>
              </div>
              <div style={{ background:C.border, borderRadius:4, height:6, margin:"10px 0 4px" }}>
                <div style={{ background:`linear-gradient(90deg, ${C.primary}, #60a5fa)`, borderRadius:4, height:6, width:`${pctCo}%`, transition:"width 0.6s ease" }}/>
              </div>
              <div style={{ fontSize:11, color:C.muted }}>
                {nCo} de {total} casillas · Cobertura total: <strong style={{color:C.text}}>{pctCov}%</strong>
              </div>
            </div>

            {/* Stat grid */}
            <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:8 }}>
              <StatCard label="TOTAL CASILLAS"    value={total}              color={C.text}    />
              <StatCard label="ABIERTAS"          value={nAb}                color={C.success} />
              <StatCard label="CERRADAS"          value={nCe}                color={C.neutral} />
              <StatCard label="PENDIENTES"        value={nPe}                color={C.warning} />
              <StatCard label="INCONSISTENCIAS"   value={nIn}                color={C.danger}  />
              <StatCard label="VOTOS REGISTRADOS" value={fmtNum(totalV)}     color={C.primary} />
            </div>

            {/* Progress bars por status */}
            <div style={{ background:C.card, border:`1px solid ${C.border}`, borderRadius:10, padding:14 }}>
              <div style={{ fontSize:10, fontWeight:700, color:C.muted, letterSpacing:1, marginBottom:10, fontFamily:"IBM Plex Mono, monospace" }}>
                DISTRIBUCIÓN
              </div>
              {Object.entries(STATUS).map(([k, v]) => {
                const n = casillas.filter(c => c.status === k).length;
                const p = total ? Math.round(n/total*100) : 0;
                return (
                  <div key={k} style={{ marginBottom:10 }}>
                    <div style={{ display:"flex", justifyContent:"space-between", marginBottom:3 }}>
                      <span style={{ fontSize:11, color:C.muted }}>{v.label}</span>
                      <span style={{ fontSize:11, color:v.color, fontFamily:"IBM Plex Mono, monospace" }}>
                        {n} <span style={{color:C.subtle}}>({p}%)</span>
                      </span>
                    </div>
                    <MiniBar pct={p} color={v.color} />
                  </div>
                );
              })}
            </div>

            {/* Por municipio */}
            <div style={{ background:C.card, border:`1px solid ${C.border}`, borderRadius:10, overflow:"hidden" }}>
              <div style={{ padding:"10px 12px", borderBottom:`1px solid ${C.border}`, fontSize:10, fontWeight:700, color:C.muted, letterSpacing:1, fontFamily:"IBM Plex Mono, monospace" }}>
                POR MUNICIPIO
              </div>
              {MUNS.map(m => {
                const mCs = casillas.filter(c => c.municipio === m.name);
                const mCo = mCs.filter(c => c.status === "contada").length;
                const mAb = mCs.filter(c => c.status === "abierta").length;
                const pct = mCs.length ? Math.round(mCo/mCs.length*100) : 0;
                const active = fMun === m.name;
                return (
                  <div key={m.name}
                       className="mun-row"
                       onClick={() => setFMun(active ? "Todos" : m.name)}
                       style={{
                         padding:"9px 12px",
                         borderBottom:`1px solid ${C.border}20`,
                         cursor:"pointer",
                         background: active ? "#1a6eff10" : "transparent",
                         borderLeft: active ? `2px solid ${C.primary}` : "2px solid transparent",
                         transition:"all 0.15s",
                       }}>
                    <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:3 }}>
                      <span style={{ fontSize:11, color: active ? C.primary : C.text, fontWeight: active ? 700 : 400 }}>
                        {m.name}
                      </span>
                      <div style={{ display:"flex", gap:6, alignItems:"center" }}>
                        {mAb > 0 && <div style={{ width:5, height:5, borderRadius:"50%", background:C.success }} className="pulse-dot"/>}
                        <span style={{ fontSize:10, color:C.muted, fontFamily:"IBM Plex Mono, monospace" }}>
                          {mCo}/{mCs.length}
                        </span>
                      </div>
                    </div>
                    <MiniBar pct={pct} color={pct===100 ? C.success : C.primary}/>
                  </div>
                );
              })}
            </div>

            {/* Casillas list */}
            <div style={{ background:C.card, border:`1px solid ${C.border}`, borderRadius:10, overflow:"hidden" }}>
              <div style={{ padding:"9px 12px", borderBottom:`1px solid ${C.border}`, fontSize:10, fontWeight:700, color:C.muted, letterSpacing:1, fontFamily:"IBM Plex Mono, monospace", display:"flex", justifyContent:"space-between" }}>
                <span>CASILLAS</span>
                <span style={{ color:C.subtle }}>{visible.length}</span>
              </div>
              <div style={{ maxHeight:240, overflowY:"auto" }}>
                {visible.map(c => {
                  const cfg = STATUS[c.status];
                  const isSel = selected?.id === c.id;
                  return (
                    <div key={c.id}
                         className="casilla-row"
                         onClick={() => setSelected(s => s?.id === c.id ? null : c)}
                         style={{
                           padding:"7px 12px",
                           borderBottom:`1px solid ${C.border}18`,
                           cursor:"pointer",
                           background: isSel ? "#1a6eff15" : "transparent",
                           display:"flex", alignItems:"center", gap:8,
                           borderLeft: isSel ? `2px solid ${C.primary}` : "2px solid transparent",
                           transition:"background 0.15s",
                         }}>
                      <div style={{ width:6, height:6, borderRadius:"50%", background:cfg.color, flexShrink:0 }}/>
                      <div style={{ flex:1, minWidth:0 }}>
                        <div style={{ fontSize:11, fontFamily:"IBM Plex Mono, monospace", color:C.text, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>
                          {c.numero}
                        </div>
                        <div style={{ fontSize:9, color:C.muted, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>
                          {c.municipio}
                        </div>
                      </div>
                      <div style={{ fontSize:11, fontFamily:"IBM Plex Mono, monospace", color:cfg.color, flexShrink:0 }}>
                        {c.votos_acta ?? "—"}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* CSV upload info */}
            <div style={{
              background: "#0d1528",
              border: `1px solid ${C.primary}30`,
              borderRadius: 10, padding: "12px 14px", fontSize:11, color:C.muted, lineHeight:1.7,
            }}>
              <div style={{ fontWeight:700, color:C.primary, marginBottom:6, fontSize:12 }}>
                📄 Archivo oficial IEE Chihuahua
              </div>
              {fileName
                ? <div style={{ color:C.success }}>✓ Cargado: {fileName}<br/><span style={{color:C.muted}}>Coordenadas oficiales activas.</span></div>
                : <>
                    Carga el CSV oficial del Instituto para usar ubicaciones certificadas.
                    <br/>
                    <span style={{ fontFamily:"IBM Plex Mono, monospace", fontSize:10, color:C.subtle }}>
                      id_casilla, municipio, seccion,<br/>numero, latitud, longitud
                    </span>
                    <br/>
                    <button onClick={() => fileRef.current?.click()} style={{
                      marginTop:8, background:C.primaryDim, border:`1px solid ${C.primary}50`,
                      color:C.primary, borderRadius:5, padding:"5px 12px",
                      fontSize:11, cursor:"pointer", fontFamily:"IBM Plex Sans, sans-serif", fontWeight:600,
                    }}>
                      Seleccionar CSV →
                    </button>
                  </>
              }
            </div>
          </aside>
        </div>
      </div>
    </>
  );
}
