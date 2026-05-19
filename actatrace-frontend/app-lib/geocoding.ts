import type { GeocodingResult, ReverseGeocodingResult } from "@/types/pollingStation";

const apiBaseUrl = getApiBaseUrl();

const geocodeCache = new Map<string, GeocodingResult>();
const reverseGeocodeCache = new Map<string, ReverseGeocodingResult>();

export async function geocodeAddress(address: string): Promise<GeocodingResult> {
  const normalizedAddress = address.replace(/[<>]/g, "").replace(/\s+/g, " ").trim();

  if (!normalizedAddress) {
    return {
      geocodingSource: "unknown",
      geocodingStatus: "failed",
    };
  }

  const cached = geocodeCache.get(normalizedAddress.toLowerCase());
  if (cached) return cached;

  try {
    const response = await fetch(
      `${apiBaseUrl}/public/geocode?address=${encodeURIComponent(normalizedAddress)}`,
    );

    if (!response.ok) {
      return { geocodingSource: "unknown", geocodingStatus: "failed" };
    }

    const payload = await response.json();
    const data = payload.data ?? payload;
    const confidence = normalizeConfidence(data.geocodingConfidence ?? data.confidence);
    const result: GeocodingResult = {
      latitude: numberOrUndefined(data.latitude),
      longitude: numberOrUndefined(data.longitude),
      normalizedAddress: data.normalizedAddress,
      geocodingSource: data.geocodingSource ?? "unknown",
      geocodingStatus:
        confidence !== undefined && confidence < 0.7
          ? "requires_review"
          : data.geocodingStatus ?? "geocoded",
      geocodingConfidence: confidence,
      geocodedAt: data.geocodedAt ?? new Date().toISOString(),
    };

    geocodeCache.set(normalizedAddress.toLowerCase(), result);
    return result;
  } catch {
    return {
      geocodingSource: "unknown",
      geocodingStatus: "failed",
    };
  }
}

export async function reverseGeocode(
  lat: number,
  lng: number,
): Promise<ReverseGeocodingResult> {
  const cacheKey = `${lat.toFixed(5)},${lng.toFixed(5)}`;
  const cached = reverseGeocodeCache.get(cacheKey);
  if (cached) return cached;

  try {
    const response = await fetch(
      `${apiBaseUrl}/public/reverse-geocode?lat=${encodeURIComponent(
        String(lat),
      )}&lng=${encodeURIComponent(String(lng))}`,
    );

    if (!response.ok) {
      return { geocodingSource: "unknown", geocodingStatus: "failed" };
    }

    const payload = await response.json();
    const data = payload.data ?? payload;
    const result: ReverseGeocodingResult = {
      address: data.address,
      normalizedAddress: data.normalizedAddress,
      geocodingSource: data.geocodingSource ?? "unknown",
      geocodingStatus: data.geocodingStatus ?? "geocoded",
      confidence: normalizeConfidence(data.confidence),
    };

    reverseGeocodeCache.set(cacheKey, result);
    return result;
  } catch {
    return { geocodingSource: "unknown", geocodingStatus: "failed" };
  }
}

export function addressDisagreesWithReverseGeocode(
  originalAddress: string,
  reverseAddress?: string,
) {
  if (!reverseAddress) return false;

  const originalTokens = meaningfulTokens(originalAddress);
  const reverseTokens = meaningfulTokens(reverseAddress);

  if (originalTokens.size === 0 || reverseTokens.size === 0) return false;

  const overlap = [...originalTokens].filter((token) => reverseTokens.has(token)).length;
  return overlap / originalTokens.size < 0.35;
}

function numberOrUndefined(value: unknown) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : undefined;
}

function normalizeConfidence(value: unknown) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return undefined;
  return Math.max(0, Math.min(parsed, 1));
}

function meaningfulTokens(value: string) {
  return new Set(
    value
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-z0-9\s]/g, " ")
      .split(/\s+/)
      .filter((token) => token.length > 3),
  );
}

function getApiBaseUrl() {
  const viteEnv = import.meta.env?.VITE_API_BASE_URL ?? import.meta.env?.NEXT_PUBLIC_API_BASE_URL;
  const nextEnv =
    typeof process !== "undefined"
      ? process.env.NEXT_PUBLIC_API_BASE_URL ?? process.env.VITE_API_BASE_URL
      : undefined;

  return viteEnv ?? nextEnv ?? "http://localhost:8000/api/v1";
}
