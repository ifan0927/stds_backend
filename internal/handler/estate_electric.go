package handler

import (
	"context"

	"github.com/ifan0927/stds-backend/internal/api"
)

func (s *Server) ListElectricReadings(ctx context.Context, request api.ListElectricReadingsRequestObject) (api.ListElectricReadingsResponseObject, error) {
	panic("not implemented")
}

func (s *Server) UpsertElectricReadings(ctx context.Context, request api.UpsertElectricReadingsRequestObject) (api.UpsertElectricReadingsResponseObject, error) {
	panic("not implemented")
}

func (s *Server) DownloadElectricReceipt(ctx context.Context, request api.DownloadElectricReceiptRequestObject) (api.DownloadElectricReceiptResponseObject, error) {
	panic("not implemented")
}

func (s *Server) DownloadElectricReport(ctx context.Context, request api.DownloadElectricReportRequestObject) (api.DownloadElectricReportResponseObject, error) {
	panic("not implemented")
}
