"use client";

import L from "leaflet";
import { useEffect, useMemo } from "react";
import { MapContainer, Marker, Popup, TileLayer, useMap } from "react-leaflet";
import type { PollingStation, VerificationStatus } from "@/types/pollingStation";
import { PollingStationPopup } from "./PollingStationPopup";

type PollingStationMapProps = {
  stations: PollingStation[];
  selectedStationId?: string;
  onSelectStation?: (station: PollingStation) => void;
};

const defaultCenter: [number, number] = [28.6353, -106.0889];

const markerColors: Record<VerificationStatus, string> = {
  counted: "#1d4ed8",
  verified: "#047857",
  mismatch: "#b91c1c",
  pending: "#64748b",
  review: "#b45309",
};

export default function PollingStationMap({
  stations,
  selectedStationId,
  onSelectStation,
}: PollingStationMapProps) {
  const mappedStations = stations.filter(hasCoordinates);
  const center = mappedStations[0]
    ? ([mappedStations[0].latitude, mappedStations[0].longitude] as [number, number])
    : defaultCenter;

  return (
    <div className="overflow-hidden rounded-2xl bg-white">
      <MapContainer center={center} zoom={12} scrollWheelZoom className="z-0">
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <FitMapToStations stations={mappedStations} selectedStationId={selectedStationId} />
        {mappedStations.map((station) => (
          <Marker
            key={station.publicId ?? station.id}
            position={[station.latitude, station.longitude]}
            icon={createStationIcon(station.verificationStatus)}
            eventHandlers={{
              click: () => onSelectStation?.(station),
            }}
          >
            <Popup closeButton={false} minWidth={320}>
              <PollingStationPopup station={station} />
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}

function FitMapToStations({
  stations,
  selectedStationId,
}: {
  stations: Array<PollingStation & { latitude: number; longitude: number }>;
  selectedStationId?: string;
}) {
  const map = useMap();
  const bounds = useMemo(() => {
    if (stations.length === 0) return null;
    return L.latLngBounds(stations.map((station) => [station.latitude, station.longitude]));
  }, [stations]);

  useEffect(() => {
    if (selectedStationId) {
      const selected = stations.find((station) => station.id === selectedStationId);
      if (selected) {
        map.setView([selected.latitude, selected.longitude], 15, { animate: true });
        return;
      }
    }

    if (bounds) {
      map.fitBounds(bounds, { padding: [32, 32], maxZoom: 14 });
    }
  }, [bounds, map, selectedStationId, stations]);

  return null;
}

function createStationIcon(status: VerificationStatus) {
  return L.divIcon({
    className: "",
    html: `<span class="actatrace-marker" style="background:${markerColors[status]}"></span>`,
    iconSize: [18, 18],
    iconAnchor: [9, 9],
  });
}

function hasCoordinates(
  station: PollingStation,
): station is PollingStation & { latitude: number; longitude: number } {
  return typeof station.latitude === "number" && typeof station.longitude === "number";
}
