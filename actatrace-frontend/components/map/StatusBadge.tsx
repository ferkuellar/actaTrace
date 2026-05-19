import type { VerificationStatus } from "@/types/pollingStation";

type StatusBadgeProps = {
  status: VerificationStatus;
  label?: string;
};

const statusConfig: Record<VerificationStatus, { label: string; className: string }> = {
  counted: {
    label: "Contada",
    className: "status-counted",
  },
  verified: {
    label: "Verificada",
    className: "status-verified",
  },
  mismatch: {
    label: "Inconsistencia",
    className: "status-mismatch",
  },
  pending: {
    label: "Pendiente",
    className: "status-pending",
  },
  review: {
    label: "Revision",
    className: "status-review",
  },
};

export function StatusBadge({ status, label }: StatusBadgeProps) {
  const config = statusConfig[status];

  return (
    <span className={`act-status-badge ${config.className}`}>
      {label ?? config.label}
    </span>
  );
}
