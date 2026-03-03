package main

import (
	"encoding/json"
	"errors"
	"net/http"
	"os"
	"sort"
	"strconv"
	"strings"
	"time"
)

const (
	moduleName    = "sort"
	moduleVersion = "1.0.0"
)

var (
	ErrEmptyInput   = errors.New("input array is empty")
	ErrMixedTypes   = errors.New("mixed types in array")
	ErrInvalidOrder = errors.New("invalid order value, must be 'asc' or 'desc'")
	ErrUnsupported  = errors.New("unsupported type in array, must be string or number")
)

// RequestEnvelope represents the incoming JSON contract request.
type RequestEnvelope struct {
	RequestID string      `json:"request_id"`
	Module    string      `json:"module"`
	Version   string      `json:"version"`
	Payload   SortPayload `json:"payload"`
}

// SortPayload contains the sorting request data.
type SortPayload struct {
	Items []interface{} `json:"items"`
	Order string        `json:"order"`
}

// ResponseEnvelope represents the outgoing JSON contract response.
type ResponseEnvelope struct {
	RequestID string            `json:"request_id"`
	Module    string            `json:"module"`
	Version   string            `json:"version"`
	Status    string            `json:"status"`
	Data      *SortResponseData `json:"data"`
	Error     *ResponseError    `json:"error"`
}

// SortResponseData contains the sorting result.
type SortResponseData struct {
	Sorted   []interface{} `json:"sorted"`
	ItemType string        `json:"item_type"`
	Count    int           `json:"count"`
}

// ResponseError represents an error in the contract format.
type ResponseError struct {
	Code    string      `json:"code"`
	Message string      `json:"message"`
	Details interface{} `json:"details"`
}

// HealthResponse represents the health check response.
type HealthResponse struct {
	Status  string `json:"status"`
	Module  string `json:"module"`
	Version string `json:"version"`
}

// generateRequestID generates a simple request ID if not provided.
func generateRequestID() string {
	return "req-" + strconv.FormatInt(int64(os.Getpid()), 10) + "-" + strconv.FormatInt(time.Now().UnixNano(), 10)
}

// validatePayload validates the sorting payload and returns the item type.
func validatePayload(payload SortPayload) (string, error) {
	if len(payload.Items) == 0 {
		return "", ErrEmptyInput
	}

	order := strings.ToLower(payload.Order)
	if order != "" && order != "asc" && order != "desc" {
		return "", ErrInvalidOrder
	}

	// Determine the type of the first item
	firstItem := payload.Items[0]
	var itemType string

	switch firstItem.(type) {
	case string:
		itemType = "string"
	case float64:
		itemType = "number"
	default:
		return "", ErrUnsupported
	}

	// Validate all items are of the same type
	for _, item := range payload.Items[1:] {
		switch item.(type) {
		case string:
			if itemType != "string" {
				return "", ErrMixedTypes
			}
		case float64:
			if itemType != "number" {
				return "", ErrMixedTypes
			}
		default:
			return "", ErrUnsupported
		}
	}

	return itemType, nil
}

// sortItems performs the actual sorting based on item type and order.
func sortItems(items []interface{}, itemType, order string) []interface{} {
	result := make([]interface{}, len(items))
	copy(result, items)

	// Default order is ascending
	desc := order == "desc"

	switch itemType {
	case "string":
		sortedStrings := make([]string, len(items))
		for i, item := range items {
			sortedStrings[i] = item.(string)
		}
		if desc {
			sort.Sort(sort.Reverse(sort.StringSlice(sortedStrings)))
		} else {
			sort.Strings(sortedStrings)
		}
		for i, s := range sortedStrings {
			result[i] = s
		}
	case "number":
		sortedNumbers := make([]float64, len(items))
		for i, item := range items {
			sortedNumbers[i] = item.(float64)
		}
		if desc {
			sort.Slice(sortedNumbers, func(i, j int) bool {
				return sortedNumbers[i] > sortedNumbers[j]
			})
		} else {
			sort.Slice(sortedNumbers, func(i, j int) bool {
				return sortedNumbers[i] < sortedNumbers[j]
			})
		}
		for i, n := range sortedNumbers {
			result[i] = n
		}
	}

	return result
}

// HandleSort processes the sort request.
func HandleSort(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	// Only accept POST requests
	if r.Method != http.MethodPost {
		resp := ResponseEnvelope{
			RequestID: generateRequestID(),
			Module:    moduleName,
			Version:   moduleVersion,
			Status:    "error",
			Data:      nil,
			Error: &ResponseError{
				Code:    "INVALID_METHOD",
				Message: "Only POST method is allowed",
				Details: nil,
			},
		}
		w.WriteHeader(http.StatusMethodNotAllowed)
		json.NewEncoder(w).Encode(resp)
		return
	}

	// Decode the request
	var req RequestEnvelope
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		resp := ResponseEnvelope{
			RequestID: generateRequestID(),
			Module:    moduleName,
			Version:   moduleVersion,
			Status:    "error",
			Data:      nil,
			Error: &ResponseError{
				Code:    "INVALID_JSON",
				Message: "Invalid JSON format: " + err.Error(),
				Details: nil,
			},
		}
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(resp)
		return
	}

	// Generate request ID if not provided
	requestID := req.RequestID
	if requestID == "" {
		requestID = generateRequestID()
	}

	// Set defaults
	if req.Module == "" {
		req.Module = moduleName
	}
	if req.Version == "" {
		req.Version = moduleVersion
	}

	// Validate payload
	itemType, err := validatePayload(req.Payload)
	if err != nil {
		var code string
		switch err {
		case ErrEmptyInput:
			code = "EMPTY_INPUT"
		case ErrMixedTypes:
			code = "MIXED_TYPES"
		case ErrInvalidOrder:
			code = "INVALID_ORDER"
		case ErrUnsupported:
			code = "UNSUPPORTED_TYPE"
		default:
			code = "VALIDATION_ERROR"
		}

		resp := ResponseEnvelope{
			RequestID: requestID,
			Module:    moduleName,
			Version:   moduleVersion,
			Status:    "error",
			Data:      nil,
			Error: &ResponseError{
				Code:    code,
				Message: err.Error(),
				Details: nil,
			},
		}
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(resp)
		return
	}

	// Perform sorting
	sorted := sortItems(req.Payload.Items, itemType, req.Payload.Order)

	// Build success response
	resp := ResponseEnvelope{
		RequestID: requestID,
		Module:    moduleName,
		Version:   moduleVersion,
		Status:    "success",
		Data: &SortResponseData{
			Sorted:   sorted,
			ItemType: itemType,
			Count:    len(sorted),
		},
		Error: nil,
	}

	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(resp)
}

// HandleHealth returns the health status of the module.
func HandleHealth(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	resp := HealthResponse{
		Status:  "ok",
		Module:  moduleName,
		Version: moduleVersion,
	}
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(resp)
}
