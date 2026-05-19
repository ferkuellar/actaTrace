import type { PollingStation } from "@/types/pollingStation";

export function formatNumber(value?: number) {
  if (typeof value !== "number") return "No disponible";
  return new Intl.NumberFormat("es-MX").format(value);
}

export function formatDateTime(value?: string) {
  if (!value) return "No disponible";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "No disponible";

  return new Intl.DateTimeFormat("es-MX", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

export function stationPublicReference(station: PollingStation) {
  return station.publicId ?? station.code;
}

export function formatCoordinates(station: PollingStation) {
  if (typeof station.latitude !== "number" || typeof station.longitude !== "number") {
    return "Sin coordenadas";
  }

  return `${station.latitude.toFixed(5)}, ${station.longitude.toFixed(5)}`;
}

export function sanitizeSearchInput(value: string) {
  return value.replace(/[<>]/g, "").replace(/\s+/g, " ").trim().slice(0, 120);
}

export function parseCoordinateSearch(value: string) {
  const match = value.match(/(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)/);
  if (!match) return null;

  const latitude = Number(match[1]);
  const longitude = Number(match[2]);

  if (
    Number.isNaN(latitude) ||
    Number.isNaN(longitude) ||
    latitude < -90 ||
    latitude > 90 ||
    longitude < -180 ||
    longitude > 180
  ) {
    return null;
  }

  return { latitude, longitude };
}

export function distanceInKm(
  first: { latitude: number; longitude: number },
  second: { latitude: number; longitude: number },
) {
  const radiusKm = 6371;
  const deltaLat = toRadians(second.latitude - first.latitude);
  const deltaLng = toRadians(second.longitude - first.longitude);
  const firstLat = toRadians(first.latitude);
  const secondLat = toRadians(second.latitude);

  const a =
    Math.sin(deltaLat / 2) * Math.sin(deltaLat / 2) +
    Math.cos(firstLat) *
      Math.cos(secondLat) *
      Math.sin(deltaLng / 2) *
      Math.sin(deltaLng / 2);

  return radiusKm * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function toRadians(value: number) {
  return (value * Math.PI) / 180;
}
