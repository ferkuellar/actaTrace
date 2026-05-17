import json
from datetime import datetime, timezone

from app.blockchain.exceptions import FabricTransactionFailed
from app.blockchain.provider import BlockchainProvider
from app.blockchain.schemas import (
    BlockchainAnchorResult,
    BlockchainTransactionResult,
    BlockchainVerificationResult,
    DocumentHashAnchorPayload,
    EventHashAnchorPayload,
)


class FabricProvider(BlockchainProvider):
    """Adapter for Hyperledger Fabric Gateway.

    This class intentionally keeps Fabric SDK wiring isolated from ActaTrace domain
    services. A production deployment should install and configure the selected
    Fabric Gateway client library, connection profile, wallet identity, channel,
    and chaincode according to the target network.
    """

    def __init__(
        self,
        *,
        connection_profile_path: str,
        wallet_path: str,
        identity_name: str,
        channel_name: str,
        chaincode_name: str,
        network_name: str,
    ) -> None:
        self.connection_profile_path = connection_profile_path
        self.wallet_path = wallet_path
        self.identity_name = identity_name
        self.channel_name = channel_name
        self.chaincode_name = chaincode_name
        self.network_name = network_name

    def anchor_document_hash(self, payload: DocumentHashAnchorPayload) -> BlockchainAnchorResult:
        result = self._submit_transaction("AnchorDocumentHash", payload.model_dump(mode="json"))
        return self._to_anchor_result(result)

    def anchor_event_hash(self, payload: EventHashAnchorPayload) -> BlockchainAnchorResult:
        result = self._submit_transaction("AnchorCriticalEvent", payload.model_dump(mode="json"))
        return self._to_anchor_result(result)

    def verify_hash(self, hash_value: str) -> BlockchainVerificationResult:
        result = self._evaluate_transaction("VerifyHash", {"hash_value": hash_value})
        return BlockchainVerificationResult(**result)

    def get_transaction(self, transaction_id: str) -> BlockchainTransactionResult:
        result = self._evaluate_transaction("GetTransaction", {"transaction_id": transaction_id})
        return BlockchainTransactionResult(**result)

    def _submit_transaction(self, function_name: str, payload: dict) -> dict:
        raise FabricTransactionFailed(
            "Fabric Gateway client is not configured in this local build. "
            f"Configure connection profile, wallet, identity, channel {self.channel_name}, "
            f"and chaincode {self.chaincode_name} before calling {function_name}.",
        )

    def _evaluate_transaction(self, function_name: str, payload: dict) -> dict:
        raise FabricTransactionFailed(
            "Fabric Gateway client is not configured in this local build. "
            f"Configure Fabric before evaluating {function_name} with payload {json.dumps(payload, sort_keys=True)}.",
        )

    def _to_anchor_result(self, result: dict) -> BlockchainAnchorResult:
        return BlockchainAnchorResult(
            provider="HYPERLEDGER_FABRIC",
            blockchain_network=self.network_name,
            transaction_id=result["transaction_id"],
            block_number=result.get("block_number"),
            anchored_at=result.get("anchored_at", datetime.now(timezone.utc)),
            status=result.get("status", "ANCHORED"),
            raw_response=result,
        )
