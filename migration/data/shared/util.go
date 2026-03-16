package shared

import (
	"encoding/json"
	"os"
	"strconv"
	"strings"
)

// NullableString converts an empty string to nil (for nullable DB columns).
func NullableString(s string) *string {
	s = strings.TrimSpace(s)
	if s == "" {
		return nil
	}
	return &s
}

// ReadJSONL reads a file in the format {"xx_table": [...records...]}.
// It extracts the first (and only) top-level key's array as the record list.
func ReadJSONL(path string) ([]map[string]any, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	var wrapper map[string][]map[string]any
	if err := json.Unmarshal(data, &wrapper); err != nil {
		return nil, err
	}
	for _, records := range wrapper {
		return records, nil
	}
	return nil, nil
}

// StringVal returns a string from a map value, or "" if missing/nil.
func StringVal(m map[string]any, key string) string {
	v, ok := m[key]
	if !ok || v == nil {
		return ""
	}
	s, _ := v.(string)
	return s
}

// Int64Val returns an int64 from a map value.
// Handles both JSON numbers (float64) and numeric strings (e.g. "42").
func Int64Val(m map[string]any, key string) int64 {
	v, ok := m[key]
	if !ok || v == nil {
		return 0
	}
	switch t := v.(type) {
	case float64:
		return int64(t)
	case int64:
		return t
	case string:
		if t == "" {
			return 0
		}
		n, err := strconv.ParseInt(t, 10, 64)
		if err != nil {
			return 0
		}
		return n
	}
	return 0
}

// Summary holds migration result counters for logging.
type Summary struct {
	Table   string
	Total   int
	Inserted int
	Skipped  int
	Errors   int
}

func (s *Summary) Log() {
	Logger.Info("migration summary",
		"table", s.Table,
		"total", s.Total,
		"inserted", s.Inserted,
		"skipped", s.Skipped,
		"errors", s.Errors,
	)
}
