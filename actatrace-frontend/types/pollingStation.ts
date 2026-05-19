export type GeocodingSource = "manual" | "nominatim" | "google" | "mapbox" | "unknown";

export type GeocodingStatus = "not_geocoded" | "geocoded" | "approximate" | "requires_review" | "failed";

export type VerificationStatus = "counted" | "verified" | "mismatch" | "pending" | "review";

export type PollingStation = {
  id: string;
  publicId?: string;
  code: string;
  section: string;
  state: string;
  municipality: string;
  originalAddress: string;
  normalizedAddress?: string;
  latitude?: number;
  longitude?: number;
  geocodingSource?: GeocodingSource;
  geocodingStatus: GeocodingStatus;
  geocodingConfidence?: number;
  geocodedAt?: string;
  actaVotes?: number;
  prepVotes?: number;
  lastUpdate?: string;
  verificationStatus: VerificationStatus;
};

export type PublicMetrics = {
  processedActas: number;
  verifiedPollingStations: number;
  prepMatches: number;
  inconsistencies: number;
};

export type GeocodingResult = {
  latitude?: number;
  longitude?: number;
  normalizedAddress?: string;
  geocodingSource: GeocodingSource;
  geocodingStatus: GeocodingStatus;
  geocodingConfidence?: number;
  geocodedAt?: string;
};

export type ReverseGeocodingResult = {
  address?: string;
  normalizedAddress?: string;
  geocodingSource: GeocodingSource;
  geocodingStatus: GeocodingStatus;
  confidence?: number;
};

