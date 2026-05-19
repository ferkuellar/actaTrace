"use client";

import { AlertCircle, LocateFixed, Search } from "lucide-react";
import type { ComponentType } from "react";
import { useEffect, useMemo, useState } from "react";
import {
  distanceInKm,
  formatCoordinates,
  sanitizeSearchInput,
  parseCoordinateSearch,
  stationPublicReference,
} from "@/lib/formatters";
import type { PollingStation } from "@/types/pollingStation";
import { GeocodingBadge } from "@/components/map/GeocodingBadge";
import { StatusBadge } from "@/components/map/StatusBadge";

type PollingStationSearchProps = {
  pollingStations: PollingStation[];
};

type PollingStationMapComponent = ComponentType<{
  stations: PollingStation[];
  selectedStationId?: string;
  onSelectStation?: (station: PollingStation) => void;
}>;

export function PollingStationSearch({ pollingStations }: PollingStationSearchProps) {
  const [query, setQuery] = useState("");
  const [selectedStationId, setSelectedStationId] = useState<string | undefined>();
  const [PollingStationMap, setPollingStationMap] =
    useState<PollingStationMapComponent | null>(null);

  useEffect(() => {
    let mounted = true;

    import("@/components/map/PollingStationMap").then((module) => {
      if (mounted) setPollingStationMap(() => module.default);
    });

    return () => {
      mounted = false;
    };
  }, []);

  const sanitizedQuery = sanitizeSearchInput(query);
  const filteredStations = useMemo(
    () => filterStations(pollingStations, sanitizedQuery),
    [pollingStations, sanitizedQuery],
  );

  const mappedStations = filteredStations.filter(
    (station) => typeof station.latitude === "number" && typeof station.longitude === "number",
  );
  const missingCoordinateStations = filteredStations.filter(
    (station) => typeof station.latitude !== "number" || typeof station.longitude !== "number",
  );

  return (
    <section className="act-search-card">
      <div className="act-search-header">
        <div>
          <p className="act-eyebrow act-eyebrow-compact">
            Busqueda publica
          </p>
          <h2 className="act-section-title">
            Consulta casillas y evidencia visible
          </h2>
        </div>
        <label className="act-search-input-wrap">
          <span className="sr-only">Buscar casilla, seccion, direccion o coordenadas</span>
          <Search className="act-search-input-icon" />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            className="act-search-input"
            placeholder="Buscar por casilla, seccion, direccion o coordenadas"
            type="search"
          />
        </label>
      </div>

      <div className="act-map-layout">
        <div>
          {PollingStationMap ? (
            <PollingStationMap
              stations={filteredStations}
              selectedStationId={selectedStationId}
              onSelectStation={(station) => setSelectedStationId(station.id)}
            />
          ) : (
            <div className="act-map-loading">
              Cargando mapa publico...
            </div>
          )}
          <p className="act-map-note">
            <LocateFixed className="act-note-icon" aria-hidden="true" />
            Se muestran marcadores solo para casillas con coordenadas derivadas o
            revisadas.
          </p>
        </div>

        <aside className="act-results-panel">
          <div className="act-results-summary">
            <p className="act-results-title">Resultados</p>
            <p className="act-results-copy">
              {filteredStations.length} casillas coinciden con la busqueda.
            </p>
          </div>

          <div className="act-results-list">
            {filteredStations.map((station) => (
              <button
                key={station.publicId ?? station.id}
                type="button"
                onClick={() => setSelectedStationId(station.id)}
                className="act-station-card"
              >
                <div className="act-station-header">
                  <div>
                    <p className="act-station-code">
                      {stationPublicReference(station)}
                    </p>
                    <p className="act-station-meta">
                      {station.municipality} · Seccion {station.section}
                    </p>
                  </div>
                  <StatusBadge status={station.verificationStatus} />
                </div>
                <p className="act-station-address">
                  {station.originalAddress}
                </p>
                <div className="act-station-badges">
                  <GeocodingBadge
                    status={station.geocodingStatus}
                    confidence={station.geocodingConfidence}
                  />
                  <span className="act-coordinates-pill">
                    {formatCoordinates(station)}
                  </span>
                </div>
              </button>
            ))}
          </div>

          {missingCoordinateStations.length > 0 ? (
            <div className="act-warning-card">
              <div className="act-warning-layout">
                <AlertCircle
                  className="act-warning-icon"
                  aria-hidden="true"
                />
                <div>
                  <p className="act-warning-title">
                    Casillas pendientes de geocodificacion
                  </p>
                  <p className="act-warning-copy">
                    {missingCoordinateStations.length} casillas conservan direccion oficial,
                    pero no tienen coordenadas confiables para mostrarse en el mapa.
                  </p>
                </div>
              </div>
            </div>
          ) : null}

          {mappedStations.length === 0 ? (
            <div className="act-empty-card">
              No hay casillas con coordenadas para esta busqueda.
            </div>
          ) : null}
        </aside>
      </div>
    </section>
  );
}

function filterStations(stations: PollingStation[], query: string) {
  if (!query) return stations;

  const coordinate = parseCoordinateSearch(query);
  if (coordinate) {
    return stations.filter((station) => {
      if (typeof station.latitude !== "number" || typeof station.longitude !== "number") {
        return false;
      }

      return (
        distanceInKm(coordinate, {
          latitude: station.latitude,
          longitude: station.longitude,
        }) <= 10
      );
    });
  }

  const normalized = query.toLowerCase();
  return stations.filter((station) =>
    [
      station.code,
      station.publicId,
      station.section,
      station.state,
      station.municipality,
      station.originalAddress,
      station.normalizedAddress,
    ]
      .filter(Boolean)
      .some((value) => value!.toLowerCase().includes(normalized)),
  );
}
