import re
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.blockchain.exceptions import BlockchainProviderError
from app.blockchain.fabric_provider import FabricProvider
from app.blockchain.mock_provider import MockBlockchainProvider
from app.blockchain.provider import BlockchainProvider
from app.blockchain.schemas import DocumentHashAnchorPayload, EventHashAnchorPayload
from app.core.config import settings
from app.core.errors import AppError, ConflictError, NotFoundError
from app.models.acta import Acta
from app.models.blockchain_anchor import BlockchainAnchor
from app.models.custody_event import CustodyEvent
from app.models.document import Document
from app.models.enums import (
    ActaStatus,
    BlockchainAnchorType,
    BlockchainProviderType,
    BlockchainVerificationStatus,
)
from app.services.audit_service import AuditService
from app.services.blockchain_verification_service import generate_canonical_event_hash

SHA256_RE = re.compile(r"^[a-f0-9]{64}$")


class BlockchainService:
    def __init__(self, db: Session, provider: BlockchainProvider | None = None) -> None:
        self.db = db
        self.provider = provider or self._build_provider()
        self.audit = AuditService(db)

    def anchor_document_hash(self, document_id: str, user_id: str, request_id: str) -> BlockchainAnchor:
        document = self.db.get(Document, document_id)
        if not document:
            raise NotFoundError("Document not found", code="DOCUMENT_NOT_FOUND")
        self._ensure_valid_hash(document.sha256_hash)
        self._ensure_hash_not_anchored(document.sha256_hash)
        acta = self.db.scalar(select(Acta).where(Acta.document_id == document.id))
        payload = self._document_payload(document, user_id, entity_type="DOCUMENT", entity_id=document.id, acta=acta)
        return self._create_anchor(
            anchor_type=BlockchainAnchorType.DOCUMENT_HASH,
            entity_type="DOCUMENT",
            entity_id=document.id,
            hash_value=document.sha256_hash,
            payload=payload.model_dump(mode="json"),
            user_id=user_id,
            request_id=request_id,
            submit=lambda: self.provider.anchor_document_hash(payload),
        )

    def anchor_acta_document_hash(self, acta_id: str, user_id: str, request_id: str) -> BlockchainAnchor:
        acta = self.db.get(Acta, acta_id)
        if not acta:
            raise NotFoundError("Acta not found", code="ACTA_NOT_FOUND")
        if not acta.document:
            raise ConflictError("Acta must have a linked document before anchoring", code="ACTA_DOCUMENT_REQUIRED")
        self._ensure_valid_hash(acta.document.sha256_hash)
        self._ensure_hash_not_anchored(acta.document.sha256_hash)
        payload = self._document_payload(acta.document, user_id, entity_type="ACTA", entity_id=acta.id, acta=acta)
        anchor = self._create_anchor(
            anchor_type=BlockchainAnchorType.DOCUMENT_HASH,
            entity_type="ACTA",
            entity_id=acta.id,
            hash_value=acta.document.sha256_hash,
            payload=payload.model_dump(mode="json"),
            user_id=user_id,
            request_id=request_id,
            submit=lambda: self.provider.anchor_document_hash(payload),
        )
        if anchor.verification_status == BlockchainVerificationStatus.ANCHORED:
            acta.status = ActaStatus.ANCHORED
            acta.blockchain_anchor_id = anchor.id
            self.audit.record(
                action="ACTA_BLOCKCHAIN_ANCHORED",
                entity_type="ACTA",
                entity_id=acta.id,
                actor_user_id=user_id,
                request_id=request_id,
                after_state={"status": acta.status.value, "blockchain_anchor_id": anchor.id},
            )
        return anchor

    def anchor_custody_event_hash(self, event_id: str, user_id: str, request_id: str) -> BlockchainAnchor:
        event = self.db.get(CustodyEvent, event_id)
        if not event:
            raise NotFoundError("Custody event not found", code="CUSTODY_EVENT_NOT_FOUND")
        event_payload = {
            "id": event.id,
            "acta_id": event.acta_id,
            "event_type": event.event_type.value,
            "from_user_id": event.from_user_id,
            "to_user_id": event.to_user_id,
            "performed_by": event.performed_by,
            "location": event.location,
            "notes": event.notes,
            "evidence_document_id": event.evidence_document_id,
            "occurred_at": event.occurred_at,
        }
        event_hash = generate_canonical_event_hash(event_payload)
        self._ensure_hash_not_anchored(event_hash)
        metadata_hash = generate_canonical_event_hash({"event_hash": event_hash, "event_id": event.id})
        payload = EventHashAnchorPayload(
            anchor_id=str(uuid.uuid4()),
            entity_type="CUSTODY_EVENT",
            entity_id=event.id,
            event_type=event.event_type.value,
            event_hash=event_hash,
            acta_id=event.acta_id,
            performed_by=event.performed_by,
            occurred_at=event.occurred_at,
            metadata_hash=metadata_hash,
        )
        return self._create_anchor(
            anchor_type=BlockchainAnchorType.CRITICAL_EVENT,
            entity_type="CUSTODY_EVENT",
            entity_id=event.id,
            hash_value=event_hash,
            payload=payload.model_dump(mode="json"),
            user_id=user_id,
            request_id=request_id,
            submit=lambda: self.provider.anchor_event_hash(payload),
        )

    def verify_hash(self, hash_value: str):
        self._ensure_valid_hash(hash_value)
        return self.provider.verify_hash(hash_value)

    def get_anchor(self, anchor_id: str) -> BlockchainAnchor:
        anchor = self.db.get(BlockchainAnchor, anchor_id)
        if not anchor:
            raise NotFoundError("Blockchain anchor not found", code="BLOCKCHAIN_ANCHOR_NOT_FOUND")
        return anchor

    def list_entity_anchors(self, entity_type: str, entity_id: str) -> list[BlockchainAnchor]:
        return list(
            self.db.scalars(
                select(BlockchainAnchor)
                .where(BlockchainAnchor.entity_type == entity_type.upper(), BlockchainAnchor.entity_id == entity_id)
                .order_by(BlockchainAnchor.created_at.desc())
            ).all()
        )

    def _document_payload(self, document: Document, user_id: str, entity_type: str, entity_id: str, acta: Acta | None) -> DocumentHashAnchorPayload:
        metadata_hash = generate_canonical_event_hash(
            {
                "document_id": document.id,
                "sha256_hash": document.sha256_hash,
                "storage_provider": document.storage_provider,
                "storage_path": document.storage_path,
                "entity_type": entity_type,
                "entity_id": entity_id,
            }
        )
        return DocumentHashAnchorPayload(
            anchor_id=str(uuid.uuid4()),
            entity_type=entity_type,
            entity_id=entity_id,
            document_id=document.id,
            sha256_hash=document.sha256_hash,
            acta_code=acta.acta_code if acta else None,
            polling_station_code=acta.polling_station.polling_station_code if acta and acta.polling_station else None,
            anchored_by=user_id,
            anchored_at=datetime.now(timezone.utc),
            metadata_hash=metadata_hash,
        )

    def _create_anchor(self, *, anchor_type, entity_type, entity_id, hash_value, payload, user_id, request_id, submit) -> BlockchainAnchor:
        provider_type = self._provider_type()
        anchor = BlockchainAnchor(
            entity_type=entity_type,
            entity_id=entity_id,
            anchor_type=anchor_type,
            hash_value=hash_value,
            blockchain_network=settings.blockchain_network_name,
            provider=provider_type,
            verification_status=BlockchainVerificationStatus.PENDING,
            request_payload=payload,
            anchored_by=user_id,
            channel_name=settings.fabric_channel_name if provider_type == BlockchainProviderType.HYPERLEDGER_FABRIC else None,
            chaincode_name=settings.fabric_chaincode_name if provider_type == BlockchainProviderType.HYPERLEDGER_FABRIC else None,
        )
        self.db.add(anchor)
        self.db.flush()
        try:
            result = submit()
        except BlockchainProviderError as exc:
            anchor.verification_status = BlockchainVerificationStatus.FAILED
            anchor.response_payload = {"error_code": exc.code, "message": exc.message}
            self.audit.record(
                action="BLOCKCHAIN_ANCHOR_FAILED",
                entity_type=entity_type,
                entity_id=entity_id,
                actor_user_id=user_id,
                request_id=request_id,
                after_state={"anchor_id": anchor.id, "error_code": exc.code},
            )
            self.db.flush()
            raise AppError(exc.message, code=exc.code, status_code=502) from exc
        anchor.transaction_hash = result.transaction_id
        anchor.block_number = result.block_number
        anchor.anchored_at = result.anchored_at
        anchor.blockchain_network = result.blockchain_network
        anchor.provider = BlockchainProviderType(result.provider)
        anchor.verification_status = BlockchainVerificationStatus.ANCHORED
        anchor.response_payload = result.raw_response
        self.audit.record(
            action="BLOCKCHAIN_ANCHOR_CREATED",
            entity_type=entity_type,
            entity_id=entity_id,
            actor_user_id=user_id,
            request_id=request_id,
            after_state={"anchor_id": anchor.id, "transaction_hash": anchor.transaction_hash, "hash_value": hash_value},
        )
        self.db.flush()
        return anchor

    def _ensure_hash_not_anchored(self, hash_value: str) -> None:
        existing = self.db.scalar(select(BlockchainAnchor).where(BlockchainAnchor.hash_value == hash_value, BlockchainAnchor.verification_status != BlockchainVerificationStatus.FAILED))
        if existing:
            raise ConflictError("Hash is already anchored", code="BLOCKCHAIN_HASH_ALREADY_ANCHORED")

    def _ensure_valid_hash(self, hash_value: str) -> None:
        if not SHA256_RE.match(hash_value):
            raise AppError("Hash must be a lowercase SHA-256 hex digest", code="INVALID_HASH_FORMAT", status_code=400)

    def _build_provider(self) -> BlockchainProvider:
        provider = settings.blockchain_provider.lower()
        if provider == "mock":
            return MockBlockchainProvider(network_name=settings.blockchain_network_name)
        if provider in {"fabric", "hyperledger_fabric"}:
            return FabricProvider(
                connection_profile_path=settings.fabric_connection_profile,
                wallet_path=settings.fabric_wallet_path,
                identity_name=settings.fabric_identity,
                channel_name=settings.fabric_channel_name,
                chaincode_name=settings.fabric_chaincode_name,
                network_name=settings.blockchain_network_name,
            )
        raise AppError("Configured blockchain provider is not supported", code="BLOCKCHAIN_PROVIDER_UNAVAILABLE", status_code=500)

    def _provider_type(self) -> BlockchainProviderType:
        if isinstance(self.provider, MockBlockchainProvider):
            return BlockchainProviderType.MOCK
        if isinstance(self.provider, FabricProvider):
            return BlockchainProviderType.HYPERLEDGER_FABRIC
        return BlockchainProviderType.MOCK
