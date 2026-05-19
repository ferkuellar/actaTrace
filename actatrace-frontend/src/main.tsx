import React from "react";
import ReactDOM from "react-dom/client";
import "leaflet/dist/leaflet.css";
import { HeroSection } from "@/components/home/HeroSection";
import { PublicMetrics } from "@/components/home/PublicMetrics";
import { VerificationDisclaimer } from "@/components/home/VerificationDisclaimer";
import { PollingStationSearch } from "@/components/search/PollingStationSearch";
import { getPublicMetrics, getPublicPollingStations } from "@/lib/api";
import type { PollingStation } from "@/types/pollingStation";
// Prototype dashboard lives at repo root until it is promoted into the frontend component tree.
// @ts-expect-error The prototype is a JSX file outside the TypeScript include set.
import ActaTraceMapaDashboard from "../../actatrace-mapa-chihuahua_1.jsx";
import "./styles.css";

function HomeApp() {
  const [stations, setStations] = React.useState<PollingStation[]>([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    getPublicPollingStations()
      .then(setStations)
      .finally(() => setLoading(false));
  }, []);

  const metrics = getPublicMetrics(stations);

  return (
    <main className="act-page">
      <HeroSection />
      <section className="act-main-shell">
        {loading ? (
          <div className="act-loading-card">
            Preparando registros publicos y mapa...
          </div>
        ) : (
          <>
            <PublicMetrics metrics={metrics} />
            <PollingStationSearch pollingStations={stations} />
          </>
        )}
        <VerificationDisclaimer />
      </section>
    </main>
  );
}

const isDashboardRoute = window.location.pathname === "/mapa-chihuahua";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    {isDashboardRoute ? <ActaTraceMapaDashboard /> : <HomeApp />}
  </React.StrictMode>,
);
