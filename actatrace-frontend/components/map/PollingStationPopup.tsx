import { MapPin } from "lucide-react";
import { formatDateTime, formatNumber, stationPublicReference } from "@/lib/formatters";
import type { PollingStation } from "@/types/pollingStation";
import { GeocodingBadge } from "./GeocodingBadge";
import { StatusBadge } from "./StatusBadge";

type PollingStationPopupProps = {
  station: PollingStation;
};

export function PollingStationPopup({ station }: PollingStationPopupProps) {
  return (
    <article className="act-popup">
      <header className="act-popup-header">
        <p className="act-popup-label">
          Casilla
        </p>
        <h3 className="act-popup-title">
          {stationPublicReference(station)}
        </h3>
        <p className="act-popup-subtitle">
          {station.municipality} · Seccion {station.section}
        </p>
      </header>

      <div className="act-popup-body">
        <div className="act-popup-address">
          <MapPin className="act-popup-pin" aria-hidden="true" />
          <div>
            <p className="act-popup-field-title">Direccion oficial</p>
            <p className="act-popup-copy">{station.originalAddress}</p>
            <p className="act-popup-note">
              Direccion conservada como evidencia; coordenadas derivadas para operacion.
            </p>
          </div>
        </div>

        <dl className="act-popup-votes">
          <div className="act-popup-stat">
            <dt>Votos acta</dt>
            <dd>
              {formatNumber(station.actaVotes)}
            </dd>
          </div>
          <div className="act-popup-stat">
            <dt>PREP</dt>
            <dd>
              {formatNumber(station.prepVotes)}
            </dd>
          </div>
        </dl>

        <div>
          <p className="act-popup-field-title">Hora</p>
          <p className="act-popup-copy">{formatDateTime(station.lastUpdate)}</p>
        </div>

        <div className="act-popup-badges">
          <StatusBadge status={station.verificationStatus} />
          <GeocodingBadge
            status={station.geocodingStatus}
            confidence={station.geocodingConfidence}
          />
        </div>
      </div>
    </article>
  );
}
