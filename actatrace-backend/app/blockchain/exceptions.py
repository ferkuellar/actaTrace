class BlockchainProviderError(Exception):
    code = "BLOCKCHAIN_PROVIDER_UNAVAILABLE"

    def __init__(self, message: str, code: str | None = None) -> None:
        self.message = message
        if code:
            self.code = code
        super().__init__(message)


class BlockchainAnchorFailed(BlockchainProviderError):
    code = "BLOCKCHAIN_ANCHOR_FAILED"


class BlockchainHashAlreadyAnchored(BlockchainProviderError):
    code = "BLOCKCHAIN_HASH_ALREADY_ANCHORED"


class BlockchainHashNotFound(BlockchainProviderError):
    code = "BLOCKCHAIN_HASH_NOT_FOUND"


class InvalidHashFormat(BlockchainProviderError):
    code = "INVALID_HASH_FORMAT"


class FabricTransactionFailed(BlockchainProviderError):
    code = "FABRIC_TRANSACTION_FAILED"
