import type { GeocodingStatus } from "@/types/pollingStation";

type GeocodingBadgeProps = {
  status: GeocodingStatus;
  confidence?: number;
};

const geocodingConfig: Record<GeocodingStatus, { label: string; className: string }> = {
  not_geocoded: {
    label: "Requiere geocodificacion",
    className: "geo-not_geocoded",
  },
  geocoded: {
    label: "Geocodificada",
    className: "geo-geocoded",
  },
  approximate: {
    label: "Aproximada",
    className: "geo-approximate",
  },
  requires_review: {
    label: "Requiere revision",
    className: "geo-requires_review",
  },
  failed: {
    label: "No localizada",
    className: "geo-failed",
  },
};

export function GeocodingBadge({ status, confidence }: GeocodingBadgeProps) {
  const config = geocodingConfig[status];
  const confidenceLabel =
    typeof confidence === "number" ? ` · ${Math.round(confidence * 100)}%` : "";

  return (
    <span
      className={`act-geocoding-badge ${config.className}`}
      title="Las coordenadas son dato operativo derivado; la direccion oficial se conserva como evidencia."
    >
      {config.label}
      {confidenceLabel}
    </span>
  );
}
