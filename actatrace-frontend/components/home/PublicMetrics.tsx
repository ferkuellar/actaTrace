import type { PublicMetrics as PublicMetricsData } from "@/types/pollingStation";

type PublicMetricsProps = {
  metrics: PublicMetricsData;
};

const metricItems = [
  ["processedActas", "Actas procesadas"],
  ["verifiedPollingStations", "Casillas verificadas"],
  ["prepMatches", "Coincidencias PREP"],
  ["inconsistencies", "Inconsistencias detectadas"],
] as const;

export function PublicMetrics({ metrics }: PublicMetricsProps) {
  return (
    <section aria-label="Metricas publicas" className="act-metrics-grid">
      {metricItems.map(([key, label]) => (
        <article
          key={key}
          className="act-metric-card"
        >
          <p className="act-metric-value">{metrics[key]}</p>
          <p className="act-metric-label">{label}</p>
        </article>
      ))}
    </section>
  );
}
