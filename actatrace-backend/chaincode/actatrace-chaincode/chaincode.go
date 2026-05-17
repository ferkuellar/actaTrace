package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"regexp"
	"time"

	"github.com/hyperledger/fabric-contract-api-go/v2/contractapi"
)

var sha256Pattern = regexp.MustCompile(`^[a-f0-9]{64}$`)

type SmartContract struct {
	contractapi.Contract
}

type Anchor struct {
	AnchorID           string `json:"anchor_id"`
	EntityType         string `json:"entity_type"`
	EntityID           string `json:"entity_id"`
	DocumentID         string `json:"document_id,omitempty"`
	SHA256Hash         string `json:"sha256_hash,omitempty"`
	ActaCode           string `json:"acta_code,omitempty"`
	PollingStationCode string `json:"polling_station_code,omitempty"`
	AnchoredBy         string `json:"anchored_by,omitempty"`
	AnchoredAt         string `json:"anchored_at,omitempty"`
	SourceSystem       string `json:"source_system,omitempty"`
	MetadataHash       string `json:"metadata_hash"`
	EventType          string `json:"event_type,omitempty"`
	EventHash          string `json:"event_hash,omitempty"`
	ActaID             string `json:"acta_id,omitempty"`
	PerformedBy        string `json:"performed_by,omitempty"`
	OccurredAt         string `json:"occurred_at,omitempty"`
	TransactionID      string `json:"transaction_id"`
}

type VerificationResult struct {
	Exists        bool   `json:"exists"`
	AnchorID      string `json:"anchor_id,omitempty"`
	EntityType    string `json:"entity_type,omitempty"`
	EntityID      string `json:"entity_id,omitempty"`
	TransactionID string `json:"transaction_id,omitempty"`
	AnchoredAt    string `json:"anchored_at,omitempty"`
}

func (s *SmartContract) AnchorDocumentHash(ctx contractapi.TransactionContextInterface, anchorJSON string) error {
	var anchor Anchor
	if err := json.Unmarshal([]byte(anchorJSON), &anchor); err != nil {
		return fmt.Errorf("invalid document anchor payload: %w", err)
	}
	if !sha256Pattern.MatchString(anchor.SHA256Hash) {
		return fmt.Errorf("sha256_hash must be a lowercase SHA-256 hash")
	}
	if anchor.EntityID == "" || anchor.ActaCode == "" || anchor.PollingStationCode == "" {
		return fmt.Errorf("entity_id, acta_code, and polling_station_code are required")
	}
	if exists, err := s.hashExists(ctx, docHashKey(anchor.SHA256Hash)); err != nil || exists {
		if err != nil {
			return err
		}
		return fmt.Errorf("hash already exists")
	}
	anchor.TransactionID = ctx.GetStub().GetTxID()
	if anchor.AnchoredAt == "" {
		anchor.AnchoredAt = time.Now().UTC().Format(time.RFC3339)
	}
	return s.putAnchor(ctx, docHashKey(anchor.SHA256Hash), anchor)
}

func (s *SmartContract) AnchorCriticalEvent(ctx contractapi.TransactionContextInterface, anchorJSON string) error {
	var anchor Anchor
	if err := json.Unmarshal([]byte(anchorJSON), &anchor); err != nil {
		return fmt.Errorf("invalid event anchor payload: %w", err)
	}
	if !sha256Pattern.MatchString(anchor.EventHash) {
		return fmt.Errorf("event_hash must be a lowercase SHA-256 hash")
	}
	if anchor.EventType == "" || anchor.ActaID == "" || anchor.PerformedBy == "" {
		return fmt.Errorf("event_type, acta_id, and performed_by are required")
	}
	if exists, err := s.hashExists(ctx, eventHashKey(anchor.EventHash)); err != nil || exists {
		if err != nil {
			return err
		}
		return fmt.Errorf("hash already exists")
	}
	anchor.TransactionID = ctx.GetStub().GetTxID()
	return s.putAnchor(ctx, eventHashKey(anchor.EventHash), anchor)
}

func (s *SmartContract) VerifyHash(ctx contractapi.TransactionContextInterface, hashValue string) (*VerificationResult, error) {
	anchor, err := s.GetAnchorByHash(ctx, hashValue)
	if err != nil {
		return &VerificationResult{Exists: false}, nil
	}
	return &VerificationResult{
		Exists:        true,
		AnchorID:      anchor.AnchorID,
		EntityType:    anchor.EntityType,
		EntityID:      anchor.EntityID,
		TransactionID: anchor.TransactionID,
		AnchoredAt:    anchor.AnchoredAt,
	}, nil
}

func (s *SmartContract) GetAnchorByHash(ctx contractapi.TransactionContextInterface, hashValue string) (*Anchor, error) {
	if !sha256Pattern.MatchString(hashValue) {
		return nil, fmt.Errorf("hash_value must be a lowercase SHA-256 hash")
	}
	for _, key := range []string{docHashKey(hashValue), eventHashKey(hashValue)} {
		data, err := ctx.GetStub().GetState(key)
		if err != nil {
			return nil, err
		}
		if data != nil {
			var anchor Anchor
			if err := json.Unmarshal(data, &anchor); err != nil {
				return nil, err
			}
			return &anchor, nil
		}
	}
	return nil, fmt.Errorf("anchor not found")
}

func (s *SmartContract) GetAnchorHistory(ctx contractapi.TransactionContextInterface, entityID string) ([]*Anchor, error) {
	key := entityKey("ENTITY", entityID)
	data, err := ctx.GetStub().GetState(key)
	if err != nil {
		return nil, err
	}
	if data == nil {
		return []*Anchor{}, nil
	}
	var anchors []*Anchor
	if err := json.Unmarshal(data, &anchors); err != nil {
		return nil, err
	}
	return anchors, nil
}

func (s *SmartContract) putAnchor(ctx contractapi.TransactionContextInterface, hashKey string, anchor Anchor) error {
	data, err := json.Marshal(anchor)
	if err != nil {
		return err
	}
	if err := ctx.GetStub().PutState(hashKey, data); err != nil {
		return err
	}
	if err := s.appendEntityAnchor(ctx, entityKey(anchor.EntityType, anchor.EntityID), anchor); err != nil {
		return err
	}
	if anchor.ActaID != "" {
		if err := s.appendEntityAnchor(ctx, entityKey("ACTA", anchor.ActaID), anchor); err != nil {
			return err
		}
	}
	return nil
}

func (s *SmartContract) appendEntityAnchor(ctx contractapi.TransactionContextInterface, key string, anchor Anchor) error {
	data, err := ctx.GetStub().GetState(key)
	if err != nil {
		return err
	}
	anchors := []*Anchor{}
	if data != nil {
		if err := json.Unmarshal(data, &anchors); err != nil {
			return err
		}
	}
	anchors = append(anchors, &anchor)
	encoded, err := json.Marshal(anchors)
	if err != nil {
		return err
	}
	return ctx.GetStub().PutState(key, encoded)
}

func (s *SmartContract) hashExists(ctx contractapi.TransactionContextInterface, key string) (bool, error) {
	data, err := ctx.GetStub().GetState(key)
	return data != nil, err
}

func docHashKey(hash string) string {
	return "DOC_HASH::" + hash
}

func eventHashKey(hash string) string {
	return "EVENT_HASH::" + hash
}

func entityKey(entityType string, entityID string) string {
	sum := sha256.Sum256([]byte(entityType + "::" + entityID))
	return "ENTITY::" + entityType + "::" + hex.EncodeToString(sum[:])
}

func main() {
	chaincode, err := contractapi.NewChaincode(&SmartContract{})
	if err != nil {
		panic(err)
	}
	if err := chaincode.Start(); err != nil {
		panic(err)
	}
}
