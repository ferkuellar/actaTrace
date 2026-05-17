import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.blockchain.exceptions import BlockchainAnchorFailed, BlockchainHashAlreadyAnchored, BlockchainHashNotFound
from app.blockchain.provider import BlockchainProvider
from app.blockchain.schemas import (
    BlockchainAnchorResult,
    BlockchainTransactionResult,
    BlockchainVerificationResult,
    DocumentHashAnchorPayload,
    EventHashAnchorPayload,
)


class MockBlockchainProvider(BlockchainProvider):
    _global_anchors: dict[str, dict] = {}
    _global_transactions: dict[str, dict] = {}

    def __init__(self, storage_path: str | None = None, network_name: str = "local-mock") -> None:
        self.storage_path = Path(storage_path) if storage_path else None
        self.network_name = network_name
        self._anchors = self._global_anchors
        self._transactions = self._global_transactions
        if self.storage_path and self.storage_path.exists():
            data = json.loads(self.storage_path.read_text(encoding="utf-8"))
            self._anchors = data.get("anchors", {})
            self._transactions = data.get("transactions", {})

    def anchor_document_hash(self, payload: DocumentHashAnchorPayload) -> BlockchainAnchorResult:
        return self._anchor_hash(payload.sha256_hash, payload.model_dump(mode="json"))

    def anchor_event_hash(self, payload: EventHashAnchorPayload) -> BlockchainAnchorResult:
        return self._anchor_hash(payload.event_hash, payload.model_dump(mode="json"))

    def verify_hash(self, hash_value: str) -> BlockchainVerificationResult:
        anchor = self._anchors.get(hash_value)
        if not anchor:
            return BlockchainVerificationResult(exists=False, hash_value=hash_value)
        return BlockchainVerificationResult(
            exists=True,
            hash_value=hash_value,
            anchor_id=anchor["anchor_id"],
            entity_type=anchor["entity_type"],
            entity_id=anchor["entity_id"],
            transaction_id=anchor["transaction_id"],
            anchored_at=datetime.fromisoformat(anchor["anchored_at"]),
            proof=anchor,
        )

    def get_transaction(self, transaction_id: str) -> BlockchainTransactionResult:
        transaction = self._transactions.get(transaction_id)
        if not transaction:
            raise BlockchainHashNotFound("Transaction not found", code="BLOCKCHAIN_HASH_NOT_FOUND")
        return BlockchainTransactionResult(transaction_id=transaction_id, found=True, payload=transaction)

    def _anchor_hash(self, hash_value: str, payload: dict) -> BlockchainAnchorResult:
        if hash_value in self._anchors:
            raise BlockchainHashAlreadyAnchored("Hash is already anchored")
        if hash_value == "f" * 64:
            raise BlockchainAnchorFailed("Mock provider forced failure")
        anchored_at = datetime.now(timezone.utc)
        transaction_id = f"mock-{uuid.uuid5(uuid.NAMESPACE_URL, hash_value)}"
        anchor = {
            "anchor_id": payload["anchor_id"],
            "entity_type": payload["entity_type"],
            "entity_id": payload["entity_id"],
            "hash_value": hash_value,
            "transaction_id": transaction_id,
            "anchored_at": anchored_at.isoformat(),
            "payload": payload,
        }
        self._anchors[hash_value] = anchor
        self._transactions[transaction_id] = anchor
        self._persist()
        return BlockchainAnchorResult(
            provider="MOCK",
            blockchain_network=self.network_name,
            transaction_id=transaction_id,
            anchored_at=anchored_at,
            status="ANCHORED",
            raw_response=anchor,
        )

    def _persist(self) -> None:
        if not self.storage_path:
            return
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.storage_path.write_text(
            json.dumps({"anchors": self._anchors, "transactions": self._transactions}, indent=2, sort_keys=True),
            encoding="utf-8",
        )
