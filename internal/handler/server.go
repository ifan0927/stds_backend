package handler

import (
	"net/http"

	"github.com/ifan0927/stds-backend/internal/apperr"
)

// Server 是目前 API handler 的總入口。
//
// 在 bootstrap 階段，它先提供一個完整但尚未接上業務邏輯的實作，
// 讓 cmd/server 可以透過 generated StrictServerInterface 完成 wiring。
// 後續各模組實作完成後，會逐步把對應 method 改成呼叫真正的 service。
type Server struct{}

// NewServer 建立 handler 總入口。
func NewServer() *Server {
	return &Server{}
}

// notImplemented 回傳目前尚未接上業務邏輯的預設錯誤。
func (s *Server) notImplemented() error {
	return apperr.New(http.StatusNotImplemented, apperr.NotImplemented, "API 尚未實作")
}
