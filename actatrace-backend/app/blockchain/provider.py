from abc import ABC, abstractmethod

from app.blockchain.schemas import (
    BlockchainAnchorResult,
    BlockchainTransactionResult,
    BlockchainVerificationResult,
    DocumentHashAnchorPayload,
    EventHashAnchorPayload,
)


class BlockchainProvider(ABC):
    @abstractmethod
    def anchor_document_hash(self, payload: DocumentHashAnchorPayload) -> BlockchainAnchorResult:
        raise NotImplementedError

    @abstractmethod
    def anchor_event_hash(self, payload: EventHashAnchorPayload) -> BlockchainAnchorResult:
        raise NotImplementedError

    @abstractmethod
    def verify_hash(self, hash_value: str) -> BlockchainVerificationResult:
        raise NotImplementedError

    @abstractmethod
    def get_transaction(self, transaction_id: str) -> BlockchainTransactionResult:
        raise NotImplementedError
