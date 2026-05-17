# Phase 3 — Blockchain Integration Layer

## 1. Phase Objective

Phase 3 integrates blockchain into ActaTrace without turning blockchain into the primary database.

The blockchain layer supports:

- Anchoring document hashes.
- Anchoring critical custody events.
- Verifying whether a hash was registered.
- Producing auditable proof metadata.
- Supporting future external audit.

Phase 3 does not store files on blockchain, does not store full acta documents on blockchain, and does not implement electronic voting.

## 2. Blockchain Design Principles

- PostgreSQL is the system of record.
- Blockchain stores only proofs, not operational data.
- Store hashes, timestamps, entity references, and event types.
- Never store private voter data.
- Never store complete documents.
- Every blockchain transaction must be linked to an `AuditLog`.
- Blockchain failures must not corrupt database state.
- Verification must be independently possible by recomputing hashes and comparing proof metadata.

## 3. Blockchain Choice Comparison

### 3.1 Hyperledger Fabric

Hyperledger Fabric is a permissioned distributed ledger platform designed for enterprise and institutional contexts. Fabric supports known identities, membership control, chaincode, channels, private data collections, configurable endorsement policies, and modular consensus.

Evaluation:

- **Permissioned network model:** Strong fit for electoral institutions, auditors, observers, and authorized public-sector participants.
- **Identity and membership control:** Fabric Membership Service Provider concepts fit institutional accountability better than anonymous public wallet participation.
- **Chaincode:** Chaincode can enforce deterministic validation for document-hash and event-hash anchors.
- **Channels/private data:** Useful for separating institutional visibility domains. ActaTrace should still avoid putting sensitive data on-chain.
- **Suitability for public-sector audit systems:** High. Fabric supports known parties, governance, endorsement, and controlled operational participation.
- **Operational complexity:** Higher than a simple public-chain smart contract. Requires certificate authorities, peers, orderers, channel governance, chaincode lifecycle, monitoring, and key management.
- **Governance model:** Strong fit when electoral authorities, auditors, and observers need formal participation rules.

### 3.2 Ethereum

Ethereum provides broad public verifiability and a mature smart contract ecosystem.

Evaluation:

- **Public verifiability:** Strong. Anyone can verify transactions on public infrastructure.
- **Gas costs:** Variable and operationally risky for high-volume anchoring.
- **Transparency:** Strong, but this can create privacy and metadata exposure concerns.
- **Smart contract simplicity:** Hash anchoring can be implemented with a simple Solidity contract.
- **Privacy concerns:** Public transaction data is visible to all participants.
- **Regulatory concerns:** Public-chain dependency and cryptocurrency mechanics may be difficult in electoral institutional environments.

### 3.3 Polygon

Polygon offers Ethereum-compatible tooling with lower costs and faster confirmation characteristics than Ethereum mainnet.

Evaluation:

- **Lower transaction cost:** Better for proof anchoring than Ethereum mainnet.
- **Public verifiability:** Strong, depending on the chosen Polygon network.
- **Faster confirmation:** Operationally useful for public checkpoint publication.
- **Dependency on public network:** Still depends on external public-chain availability and governance.
- **Suitability for proof anchoring:** Good for optional future public checkpoints, not as the initial institutional ledger.

## 4. Final Recommendation

Use **Hyperledger Fabric** for ActaTrace Phase 3 in institutional and private electoral environments.

Recommended direction:

- Use Hyperledger Fabric as the primary institutional verification network.
- Keep PostgreSQL as the operational source of truth.
- Anchor only hashes and critical event digests.
- Add optional future public anchoring to Polygon or Ethereum for citizen-verifiable checkpoint batches.

Justification:

Fabric better matches electoral governance because participants are known, permissions are explicit, transaction endorsement can reflect institutional policy, and the network can be operated without cryptocurrency mechanics. Public-chain anchoring remains useful later for transparency checkpoints, but it should not be the first operational dependency.

This aligns with Fabric 2.5 concepts documented by Hyperledger: Fabric is permissioned, supports known identities, uses chaincode for business logic, and Fabric Gateway provides simplified transaction submission and evaluation APIs.

References:

- Hyperledger Fabric 2.5 Introduction: https://hyperledger-fabric.readthedocs.io/en/release-2.5/whatis.html
- Fabric Gateway: https://hyperledger-fabric.readthedocs.io/en/release-2.5/gateway.html
- Chaincode: https://hyperledger-fabric.readthedocs.io/en/release-2.5/chaincode.html
- Private Data: https://hyperledger-fabric.readthedocs.io/en/release-2.5/private-data/private-data.html

## 5. Blockchain Data Model

### 5.1 Document Hash Anchor

Anchored fields:

- `anchor_id`
- `entity_type`
- `entity_id`
- `document_id`
- `sha256_hash`
- `acta_code`
- `polling_station_code`
- `anchored_by`
- `anchored_at`
- `source_system`
- `metadata_hash`

The `sha256_hash` proves file integrity. The `metadata_hash` proves that selected metadata was canonicalized and hashed without storing complete operational metadata on-chain.

### 5.2 Critical Event Anchor

Anchored fields:

- `anchor_id`
- `entity_type`
- `entity_id`
- `event_type`
- `event_hash`
- `acta_id`
- `performed_by`
- `occurred_at`
- `metadata_hash`

Critical event anchors are used for custody actions or later audit events where tamper evidence is important.

### 5.3 What Must Not Be Anchored

Never anchor:

- File contents.
- Full PDF/Image actas.
- Personal sensitive data.
- Passwords.
- JWT tokens.
- Internal database dumps.
- Private notes.
- Any vote secrecy information.

## 6. Backend Architecture

Implemented modules:

```text
app/
├── blockchain/
│   ├── __init__.py
│   ├── provider.py
│   ├── fabric_provider.py
│   ├── mock_provider.py
│   ├── schemas.py
│   └── exceptions.py
├── services/
│   ├── blockchain_service.py
│   └── blockchain_verification_service.py
├── api/
│   └── v1/
│       └── blockchain.py
```

`BlockchainService` is the application facade. It owns database writes, audit logging, status transitions, duplicate detection, failure handling, and provider selection. Providers only know how to submit or evaluate blockchain operations.

## 7. Design Patterns Required

### Facade Pattern

`BlockchainService` hides provider complexity from the rest of the application. API routes do not call Fabric or mock provider methods directly.

### Strategy Pattern

`BlockchainProvider` allows provider switching between:

- `MockBlockchainProvider`
- `FabricProvider`
- Future Ethereum/Polygon providers

### Adapter Pattern

`FabricProvider` adapts Fabric Gateway concepts to the internal `BlockchainProvider` interface.

## 8. Provider Interface

The abstract provider is `app/blockchain/provider.py`.

Required methods:

- `anchor_document_hash(payload: DocumentHashAnchorPayload) -> BlockchainAnchorResult`
- `anchor_event_hash(payload: EventHashAnchorPayload) -> BlockchainAnchorResult`
- `verify_hash(hash_value: str) -> BlockchainVerificationResult`
- `get_transaction(transaction_id: str) -> BlockchainTransactionResult`

## 9. Mock Blockchain Provider

`MockBlockchainProvider` supports local development and tests.

Rules implemented:

- Stores anchored hashes in memory by default.
- Can persist to local JSON if a path is provided.
- Generates deterministic fake transaction IDs.
- Returns deterministic verification results.
- Rejects duplicate hashes.
- Does not require a Fabric network for local API tests.

## 10. Hyperledger Fabric Provider

`FabricProvider` is structured around Fabric 2.5 concepts:

- Connection profile path.
- Wallet path.
- Identity name.
- Channel name.
- Chaincode name.
- Submit transaction.
- Evaluate transaction.

Mapped operations:

- Submit `AnchorDocumentHash`.
- Submit `AnchorCriticalEvent`.
- Evaluate `VerifyHash`.
- Evaluate `GetAnchorByHash`.
- Evaluate `GetTransaction`.

The local implementation intentionally keeps the SDK call site isolated and raises a structured `FABRIC_TRANSACTION_FAILED` error until a target Fabric network and Gateway client are configured.

## 11. Chaincode Design

Implemented example chaincode:

```text
actatrace-backend/chaincode/actatrace-chaincode/
├── go.mod
└── chaincode.go
```

### AnchorDocumentHash

Input:

- `anchor_id`
- `entity_type`
- `entity_id`
- `document_id`
- `sha256_hash`
- `acta_code`
- `polling_station_code`
- `anchored_by`
- `anchored_at`
- `metadata_hash`

Validation:

- `sha256_hash` must be valid SHA-256.
- Hash must not already exist.
- `entity_id` required.
- `acta_code` required.
- `polling_station_code` required.

### AnchorCriticalEvent

Input:

- `anchor_id`
- `entity_type`
- `entity_id`
- `event_type`
- `event_hash`
- `acta_id`
- `performed_by`
- `occurred_at`
- `metadata_hash`

Validation:

- `event_hash` must be valid SHA-256.
- `event_type` required.
- `acta_id` required.
- `performed_by` required.

### VerifyHash

Input:

- `hash_value`

Output:

- `exists`
- `anchor_id`
- `entity_type`
- `entity_id`
- `transaction_id`
- `anchored_at`

### GetAnchorByHash

Input:

- `hash_value`

Output:

- Full anchor metadata.

### GetAnchorHistory

Input:

- `entity_id`

Output:

- All anchors related to the entity.

## 12. Chaincode Storage Model

World state keys:

- `DOC_HASH::{sha256_hash}`: direct lookup for document proof verification.
- `EVENT_HASH::{event_hash}`: direct lookup for custody or audit event proof verification.
- `ENTITY::{entity_type}::{entity_id}`: entity-level anchor history.
- `ACTA::{acta_id}`: acta-centered anchor history for document and event traceability.

These keys support constant-time hash verification and entity reconstruction without storing full operational data on-chain.

## 13. Backend Database Changes

The `blockchain_anchors` model now includes:

- `id`
- `entity_type`
- `entity_id`
- `anchor_type`
- `hash_value`
- `blockchain_network`
- `provider`
- `transaction_hash`
- `block_number`
- `channel_name`
- `chaincode_name`
- `verification_status`
- `request_payload`
- `response_payload`
- `anchored_by`
- `anchored_at`
- `created_at`
- `updated_at`

Enums added:

- `BlockchainAnchorType`: `DOCUMENT_HASH`, `CRITICAL_EVENT`
- `BlockchainProviderType`: `MOCK`, `HYPERLEDGER_FABRIC`, `ETHEREUM`, `POLYGON`
- `BlockchainVerificationStatus`: `PENDING`, `ANCHORED`, `VERIFIED`, `FAILED`

## 14. API Endpoints

Base path:

```text
/api/v1/blockchain
```

### POST `/blockchain/anchor/document/{document_id}`

Anchors a document SHA-256 hash.

Rules:

- Requires `ADMIN_ELECTORAL`, `SUPERVISOR`, or `AUDITOR`.
- Document must exist.
- Document must have `sha256_hash`.
- Duplicate hash anchoring is rejected.
- Creates `BlockchainAnchor`.
- Creates `AuditLog`.

### POST `/blockchain/anchor/acta/{acta_id}`

Anchors the acta document hash.

Rules:

- Acta must exist.
- Acta must have linked document.
- Document must have valid hash.
- Updates acta status to `ANCHORED` after successful anchoring.

### POST `/blockchain/anchor/custody-event/{event_id}`

Anchors a critical custody event hash.

Rules:

- Custody event must exist.
- Generates event hash from canonical event payload.
- Creates `BlockchainAnchor`.
- Creates `AuditLog`.

### GET `/blockchain/verify/hash/{hash_value}`

Verifies whether a hash exists on the configured blockchain provider.

Rules:

- Public-readable in Phase 3.
- Does not expose sensitive metadata.
- Returns verification status and proof.

### GET `/blockchain/anchors/{anchor_id}`

Returns blockchain anchor details for authorized institutional roles.

### GET `/blockchain/anchors/entity/{entity_type}/{entity_id}`

Returns all anchors for an entity for authorized institutional roles.

## 15. Canonical Hashing

Implemented:

```python
generate_canonical_event_hash(payload: dict) -> str
```

Rules:

- Sort keys.
- Remove volatile fields.
- Use UTF-8 encoding.
- Use compact JSON separators.
- Generate lowercase SHA-256 hex.
- Same input produces the same hash.

Volatile fields removed:

- `created_at`
- `updated_at`
- `request_id`
- `ip_address`
- `user_agent`

## 16. Security Considerations

Implemented and documented controls:

- Provider configuration through environment variables.
- No sensitive data on-chain.
- No file contents on-chain.
- Hash-only anchoring.
- Audit log creation for successful and failed anchoring.
- Structured blockchain errors.
- Duplicate anchor prevention.
- RBAC on anchoring endpoints.
- Public verification endpoint exposes only proof-safe fields.
- Fabric identity configuration isolated to `FabricProvider`.

Future Fabric deployment controls:

- Use Fabric CA or approved MSP process for identities.
- Separate identities for API submitter, auditors, and admin operations.
- Enforce chaincode endorsement policy by institution.
- Store private keys in secure wallet/KMS-backed storage.
- Rotate identities according to institutional policy.
- Monitor failed endorsement, submit, and commit status events.

## 17. Environment Variables

Added to `.env.example`:

```env
BLOCKCHAIN_PROVIDER=mock
FABRIC_CONNECTION_PROFILE=
FABRIC_WALLET_PATH=
FABRIC_IDENTITY=
FABRIC_CHANNEL_NAME=actatrace-channel
FABRIC_CHAINCODE_NAME=actatrace-chaincode
FABRIC_ORG_NAME=
BLOCKCHAIN_NETWORK_NAME=local-fabric
```

## 18. Testing Requirements

Implemented tests cover:

- Mock provider anchors document hash.
- Mock provider verifies existing hash.
- Mock provider rejects duplicate hash.
- Canonical event hash is deterministic.
- `BlockchainService` creates anchor record.
- API endpoint rejects unauthorized role.
- API endpoint anchors document hash successfully.
- Blockchain failure creates `FAILED` anchor status and audit log.

Run:

```bash
cd actatrace-backend
pytest
```

## 19. Error Handling

Structured blockchain errors:

- `BLOCKCHAIN_PROVIDER_UNAVAILABLE`
- `BLOCKCHAIN_ANCHOR_FAILED`
- `BLOCKCHAIN_HASH_ALREADY_ANCHORED`
- `BLOCKCHAIN_HASH_NOT_FOUND`
- `INVALID_HASH_FORMAT`
- `FABRIC_TRANSACTION_FAILED`

Errors use the existing API format:

```json
{
  "error": {
    "code": "BLOCKCHAIN_ANCHOR_FAILED",
    "message": "Anchor submission failed",
    "request_id": "..."
  }
}
```

## 20. Documentation Required

### Why Blockchain Is Used

Blockchain is used to provide tamper-evident proof that a document hash or critical event hash existed at a given time and was submitted by an authorized identity.

### Why Files Are Not Stored On Blockchain

Files are large, sensitive, operationally expensive, and may contain information that should not be permanently replicated across ledger participants. ActaTrace stores files in controlled storage and anchors only hashes.

### Why PostgreSQL Remains the System of Record

PostgreSQL stores relational state, permissions, operational workflow, audit logs, dashboard queries, and reconciliation data. Blockchain only adds external proof.

### How Verification Works

1. Retrieve the file or event payload from the system of record.
2. Recompute SHA-256 or canonical event hash.
3. Query `/api/v1/blockchain/verify/hash/{hash_value}`.
4. Compare returned proof metadata against PostgreSQL `BlockchainAnchor`.
5. For Fabric, evaluate `VerifyHash` or `GetAnchorByHash` on chaincode.

### How Fabric Would Be Deployed Later

Future deployment requires:

- Fabric CA/MSP setup.
- Peer and ordering service deployment.
- Channel creation.
- Chaincode packaging, installation, approval, and commit.
- Gateway client configuration.
- Wallet identity provisioning.
- Monitoring, backup, and governance processes.

### How Public Verification Could Be Added Later

Public verification can expose safe fields:

- Hash exists.
- Anchor ID.
- Entity type.
- Transaction ID.
- Anchored timestamp.
- Network/provider.

It must not expose internal notes, private actor details, documents, or sensitive operational metadata.

### Known Limitations of Phase 3

- Fabric provider is an adapter scaffold until a real network and SDK are configured.
- Mock provider is for local development only.
- No production blockchain identities are included.
- No public-chain provider is implemented.
- Existing database instances require an Alembic migration before using new blockchain fields.

## 21. Anti-Overengineering Guardrails

Do not add:

- Electronic voting.
- Tokenomics.
- Cryptocurrency payments.
- NFT certificates.
- Public wallet login.
- Complex smart contracts.
- Multi-chain production support.
- Kafka.
- Event sourcing.
- Kubernetes.
- AI fraud detection.

## 22. Phase 4 Recommendation

The next phase should be:

**Phase 4 — Document Storage and Integrity Pipeline**

Phase 4 should build:

- Real file upload.
- S3-compatible object storage.
- Document integrity verification.
- File re-hashing.
- Storage adapter.
- Public-safe document retrieval.
- Tamper-evidence workflow.

Phase 4 should keep blockchain limited to verification and anchoring. PostgreSQL remains the system of record.
