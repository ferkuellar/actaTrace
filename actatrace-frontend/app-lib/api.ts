import { z } from "zod";
import type { PollingStation, PublicMetrics } from "@/types/pollingStation";

const apiBaseUrl = getApiBaseUrl();

const pollingStationSchema = z.object({
  id: z.string(),
  publicId: z.string().optional(),
  code: z.string(),
  section: z.string(),
  state: z.string(),
  municipality: z.string(),
  originalAddress: z.string(),
  normalizedAddress: z.string().optional(),
  latitude: z.number().optional(),
  longitude: z.number().optional(),
  geocodingSource: z
    .enum(["manual", "nominatim", "google", "mapbox", "unknown"])
    .optional(),
  geocodingStatus: z.enum([
    "not_geocoded",
    "geocoded",
    "approximate",
    "requires_review",
    "failed",
  ]),
  geocodingConfidence: z.number().min(0).max(1).optional(),
  geocodedAt: z.string().optional(),
  actaVotes: z.number().optional(),
  prepVotes: z.number().optional(),
  lastUpdate: z.string().optional(),
  verificationStatus: z.enum(["counted", "verified", "mismatch", "pending", "review"]),
});

const pollingStationListSchema = z.array(pollingStationSchema);

const fallbackPollingStations: PollingStation[] = [
  {
    id: "internal-hidden-001",
    publicId: "PS-CHIH-0528-C",
    code: "528-C",
    section: "626",
    state: "Chihuahua",
    municipality: "Chihuahua",
    originalAddress:
      "Escuela Primaria Estatal, Calle 24 y Privada de Juarez, Chihuahua, Chihuahua",
    normalizedAddress:
      "Calle 24 y Privada de Juarez, Zona Centro, Chihuahua, Chihuahua",
    latitude: 28.63236,
    longitude: -106.08102,
    geocodingSource: "manual",
    geocodingStatus: "geocoded",
    geocodingConfidence: 0.94,
    geocodedAt: "2026-05-17T14:10:00-06:00",
    actaVotes: 149,
    prepVotes: 149,
    lastUpdate: "2026-05-17T14:16:00-06:00",
    verificationStatus: "counted",
  },
  {
    id: "internal-hidden-002",
    publicId: "PS-CHIH-0631-B",
    code: "631-B",
    section: "631",
    state: "Chihuahua",
    municipality: "Chihuahua",
    originalAddress:
      "Centro Comunitario Colonia Obrera, Avenida Independencia, Chihuahua, Chihuahua",
    normalizedAddress: "Avenida Independencia, Chihuahua, Chihuahua",
    latitude: 28.64172,
    longitude: -106.07391,
    geocodingSource: "nominatim",
    geocodingStatus: "approximate",
    geocodingConfidence: 0.72,
    geocodedAt: "2026-05-17T14:12:00-06:00",
    actaVotes: 181,
    prepVotes: 181,
    lastUpdate: "2026-05-17T14:22:00-06:00",
    verificationStatus: "verified",
  },
  {
    id: "internal-hidden-003",
    publicId: "PS-CHIH-0718-C1",
    code: "718-C1",
    section: "718",
    state: "Chihuahua",
    municipality: "Chihuahua",
    originalAddress:
      "Secundaria Tecnica 2, Avenida Universidad, Chihuahua, Chihuahua",
    normalizedAddress: "Avenida Universidad, Chihuahua, Chihuahua",
    latitude: 28.66104,
    longitude: -106.10129,
    geocodingSource: "manual",
    geocodingStatus: "geocoded",
    geocodingConfidence: 0.91,
    geocodedAt: "2026-05-17T14:15:00-06:00",
    actaVotes: 205,
    prepVotes: 198,
    lastUpdate: "2026-05-17T14:31:00-06:00",
    verificationStatus: "mismatch",
  },
  {
    id: "internal-hidden-004",
    publicId: "PS-CHIH-0820-B",
    code: "820-B",
    section: "820",
    state: "Chihuahua",
    municipality: "Chihuahua",
    originalAddress:
      "Salon Ejidal, domicilio conocido, zona rural del municipio de Chihuahua",
    geocodingSource: "unknown",
    geocodingStatus: "requires_review",
    actaVotes: 97,
    prepVotes: 97,
    lastUpdate: "2026-05-17T14:39:00-06:00",
    verificationStatus: "review",
  },
];

export async function getPublicPollingStations(): Promise<PollingStation[]> {
  const controller = new AbortController();
  const timeout = globalThis.setTimeout(() => controller.abort(), 900);

  try {
    const response = await fetch(`${apiBaseUrl}/public/polling-stations`, {
      signal: controller.signal,
    });

    if (!response.ok) return fallbackPollingStations;

    const payload = await response.json();
    const data = Array.isArray(payload) ? payload : payload.data;
    return pollingStationListSchema.parse(data);
  } catch {
    return fallbackPollingStations;
  } finally {
    globalThis.clearTimeout(timeout);
  }
}

export function getPublicMetrics(stations: PollingStation[]): PublicMetrics {
  return {
    processedActas: stations.filter((station) => typeof station.actaVotes === "number")
      .length,
    verifiedPollingStations: stations.filter((station) =>
      ["counted", "verified"].includes(station.verificationStatus),
    ).length,
    prepMatches: stations.filter(
      (station) =>
        typeof station.actaVotes === "number" &&
        typeof station.prepVotes === "number" &&
        station.actaVotes === station.prepVotes,
    ).length,
    inconsistencies: stations.filter((station) => station.verificationStatus === "mismatch")
      .length,
  };
}

function getApiBaseUrl() {
  const viteEnv = import.meta.env?.VITE_API_BASE_URL ?? import.meta.env?.NEXT_PUBLIC_API_BASE_URL;
  const nextEnv =
    typeof process !== "undefined"
      ? process.env.NEXT_PUBLIC_API_BASE_URL ?? process.env.VITE_API_BASE_URL
      : undefined;

  return viteEnv ?? nextEnv ?? "http://localhost:8000/api/v1";
}
