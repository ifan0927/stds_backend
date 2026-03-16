package handler

import (
	"context"

	"github.com/ifan0927/stds-backend/internal/api"
)

// 這個檔案保留 StrictServerInterface 的 placeholder 實作。
//
// generated 的 StrictServerInterface 定義在 internal/api/api.gen.go。
// 目前每個 method 都先回傳 not implemented，目的只有兩個：
// 1. 讓 main bootstrap 可以先完成 RegisterHandlers() wiring
// 2. 讓後續模組實作時可以逐步把 method 換成真正的 handler/service 呼叫

func (s *Server) Login(ctx context.Context, request api.LoginRequestObject) (api.LoginResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) Logout(ctx context.Context, request api.LogoutRequestObject) (api.LogoutResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) ListEstates(ctx context.Context, request api.ListEstatesRequestObject) (api.ListEstatesResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) CreateEstate(ctx context.Context, request api.CreateEstateRequestObject) (api.CreateEstateResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) DeleteEstate(ctx context.Context, request api.DeleteEstateRequestObject) (api.DeleteEstateResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) GetEstate(ctx context.Context, request api.GetEstateRequestObject) (api.GetEstateResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) UpdateEstate(ctx context.Context, request api.UpdateEstateRequestObject) (api.UpdateEstateResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) ListAccountingTitles(ctx context.Context, request api.ListAccountingTitlesRequestObject) (api.ListAccountingTitlesResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) ListAccountings(ctx context.Context, request api.ListAccountingsRequestObject) (api.ListAccountingsResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) CreateAccounting(ctx context.Context, request api.CreateAccountingRequestObject) (api.CreateAccountingResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) GetAccountingOverview(ctx context.Context, request api.GetAccountingOverviewRequestObject) (api.GetAccountingOverviewResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) DeleteAccounting(ctx context.Context, request api.DeleteAccountingRequestObject) (api.DeleteAccountingResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) GetAccounting(ctx context.Context, request api.GetAccountingRequestObject) (api.GetAccountingResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) UpdateAccounting(ctx context.Context, request api.UpdateAccountingRequestObject) (api.UpdateAccountingResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) ListEstateAttachments(ctx context.Context, request api.ListEstateAttachmentsRequestObject) (api.ListEstateAttachmentsResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) UploadEstateAttachment(ctx context.Context, request api.UploadEstateAttachmentRequestObject) (api.UploadEstateAttachmentResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) SortEstateAttachments(ctx context.Context, request api.SortEstateAttachmentsRequestObject) (api.SortEstateAttachmentsResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) DeleteEstateAttachment(ctx context.Context, request api.DeleteEstateAttachmentRequestObject) (api.DeleteEstateAttachmentResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) UpdateEstateAttachment(ctx context.Context, request api.UpdateEstateAttachmentRequestObject) (api.UpdateEstateAttachmentResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) DownloadEstateAttachment(ctx context.Context, request api.DownloadEstateAttachmentRequestObject) (api.DownloadEstateAttachmentResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) ListElectricReadings(ctx context.Context, request api.ListElectricReadingsRequestObject) (api.ListElectricReadingsResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) UpsertElectricReadings(ctx context.Context, request api.UpsertElectricReadingsRequestObject) (api.UpsertElectricReadingsResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) DownloadElectricReceipt(ctx context.Context, request api.DownloadElectricReceiptRequestObject) (api.DownloadElectricReceiptResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) DownloadElectricReport(ctx context.Context, request api.DownloadElectricReportRequestObject) (api.DownloadElectricReportResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) ListFacilities(ctx context.Context, request api.ListFacilitiesRequestObject) (api.ListFacilitiesResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) UpdateFacilityMemo(ctx context.Context, request api.UpdateFacilityMemoRequestObject) (api.UpdateFacilityMemoResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) ListFacilityAttachments(ctx context.Context, request api.ListFacilityAttachmentsRequestObject) (api.ListFacilityAttachmentsResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) UploadFacilityAttachment(ctx context.Context, request api.UploadFacilityAttachmentRequestObject) (api.UploadFacilityAttachmentResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) SortFacilityAttachments(ctx context.Context, request api.SortFacilityAttachmentsRequestObject) (api.SortFacilityAttachmentsResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) DeleteFacilityAttachment(ctx context.Context, request api.DeleteFacilityAttachmentRequestObject) (api.DeleteFacilityAttachmentResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) UpdateFacilityAttachment(ctx context.Context, request api.UpdateFacilityAttachmentRequestObject) (api.UpdateFacilityAttachmentResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) DownloadFacilityAttachment(ctx context.Context, request api.DownloadFacilityAttachmentRequestObject) (api.DownloadFacilityAttachmentResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) ListEstateMembers(ctx context.Context, request api.ListEstateMembersRequestObject) (api.ListEstateMembersResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) UpdateEstateMembers(ctx context.Context, request api.UpdateEstateMembersRequestObject) (api.UpdateEstateMembersResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) UpdateEstateMember(ctx context.Context, request api.UpdateEstateMemberRequestObject) (api.UpdateEstateMemberResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) ListRents(ctx context.Context, request api.ListRentsRequestObject) (api.ListRentsResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) CreateRent(ctx context.Context, request api.CreateRentRequestObject) (api.CreateRentResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) ListPaymentReminders(ctx context.Context, request api.ListPaymentRemindersRequestObject) (api.ListPaymentRemindersResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) DeleteRent(ctx context.Context, request api.DeleteRentRequestObject) (api.DeleteRentResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) GetRent(ctx context.Context, request api.GetRentRequestObject) (api.GetRentResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) UpdateRent(ctx context.Context, request api.UpdateRentRequestObject) (api.UpdateRentResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) ReactivateRent(ctx context.Context, request api.ReactivateRentRequestObject) (api.ReactivateRentResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) TerminateRent(ctx context.Context, request api.TerminateRentRequestObject) (api.TerminateRentResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) TerminateRentPreview(ctx context.Context, request api.TerminateRentPreviewRequestObject) (api.TerminateRentPreviewResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) ListRentAttachments(ctx context.Context, request api.ListRentAttachmentsRequestObject) (api.ListRentAttachmentsResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) UploadRentAttachment(ctx context.Context, request api.UploadRentAttachmentRequestObject) (api.UploadRentAttachmentResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) SortRentAttachments(ctx context.Context, request api.SortRentAttachmentsRequestObject) (api.SortRentAttachmentsResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) DeleteRentAttachment(ctx context.Context, request api.DeleteRentAttachmentRequestObject) (api.DeleteRentAttachmentResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) UpdateRentAttachment(ctx context.Context, request api.UpdateRentAttachmentRequestObject) (api.UpdateRentAttachmentResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) DownloadRentAttachment(ctx context.Context, request api.DownloadRentAttachmentRequestObject) (api.DownloadRentAttachmentResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) DownloadCheckoutSummary(ctx context.Context, request api.DownloadCheckoutSummaryRequestObject) (api.DownloadCheckoutSummaryResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) DownloadPaymentNotice(ctx context.Context, request api.DownloadPaymentNoticeRequestObject) (api.DownloadPaymentNoticeResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) GetRentPaymentSchedule(ctx context.Context, request api.GetRentPaymentScheduleRequestObject) (api.GetRentPaymentScheduleResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) ListRentTenants(ctx context.Context, request api.ListRentTenantsRequestObject) (api.ListRentTenantsResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) LinkTenantToRent(ctx context.Context, request api.LinkTenantToRentRequestObject) (api.LinkTenantToRentResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) UnlinkTenantFromRent(ctx context.Context, request api.UnlinkTenantFromRentRequestObject) (api.UnlinkTenantFromRentResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) GetRentTenant(ctx context.Context, request api.GetRentTenantRequestObject) (api.GetRentTenantResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) UpdateRentTenant(ctx context.Context, request api.UpdateRentTenantRequestObject) (api.UpdateRentTenantResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) ListRooms(ctx context.Context, request api.ListRoomsRequestObject) (api.ListRoomsResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) CreateRoom(ctx context.Context, request api.CreateRoomRequestObject) (api.CreateRoomResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) UpdateRoomSort(ctx context.Context, request api.UpdateRoomSortRequestObject) (api.UpdateRoomSortResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) DeleteRoom(ctx context.Context, request api.DeleteRoomRequestObject) (api.DeleteRoomResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) GetRoom(ctx context.Context, request api.GetRoomRequestObject) (api.GetRoomResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) UpdateRoom(ctx context.Context, request api.UpdateRoomRequestObject) (api.UpdateRoomResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) CopyRoom(ctx context.Context, request api.CopyRoomRequestObject) (api.CopyRoomResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) ListRoomAttachments(ctx context.Context, request api.ListRoomAttachmentsRequestObject) (api.ListRoomAttachmentsResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) UploadRoomAttachment(ctx context.Context, request api.UploadRoomAttachmentRequestObject) (api.UploadRoomAttachmentResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) SortRoomAttachments(ctx context.Context, request api.SortRoomAttachmentsRequestObject) (api.SortRoomAttachmentsResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) DeleteRoomAttachment(ctx context.Context, request api.DeleteRoomAttachmentRequestObject) (api.DeleteRoomAttachmentResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) UpdateRoomAttachment(ctx context.Context, request api.UpdateRoomAttachmentRequestObject) (api.UpdateRoomAttachmentResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) DownloadRoomAttachment(ctx context.Context, request api.DownloadRoomAttachmentRequestObject) (api.DownloadRoomAttachmentResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) ListSchedules(ctx context.Context, request api.ListSchedulesRequestObject) (api.ListSchedulesResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) CreateSchedule(ctx context.Context, request api.CreateScheduleRequestObject) (api.CreateScheduleResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) DeleteSchedule(ctx context.Context, request api.DeleteScheduleRequestObject) (api.DeleteScheduleResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) GetSchedule(ctx context.Context, request api.GetScheduleRequestObject) (api.GetScheduleResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) UpdateSchedule(ctx context.Context, request api.UpdateScheduleRequestObject) (api.UpdateScheduleResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) ListScheduleAttachments(ctx context.Context, request api.ListScheduleAttachmentsRequestObject) (api.ListScheduleAttachmentsResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) UploadScheduleAttachment(ctx context.Context, request api.UploadScheduleAttachmentRequestObject) (api.UploadScheduleAttachmentResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) SortScheduleAttachments(ctx context.Context, request api.SortScheduleAttachmentsRequestObject) (api.SortScheduleAttachmentsResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) DeleteScheduleAttachment(ctx context.Context, request api.DeleteScheduleAttachmentRequestObject) (api.DeleteScheduleAttachmentResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) UpdateScheduleAttachment(ctx context.Context, request api.UpdateScheduleAttachmentRequestObject) (api.UpdateScheduleAttachmentResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) DownloadScheduleAttachment(ctx context.Context, request api.DownloadScheduleAttachmentRequestObject) (api.DownloadScheduleAttachmentResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) CreateReply(ctx context.Context, request api.CreateReplyRequestObject) (api.CreateReplyResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) DeleteReply(ctx context.Context, request api.DeleteReplyRequestObject) (api.DeleteReplyResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) UpdateReply(ctx context.Context, request api.UpdateReplyRequestObject) (api.UpdateReplyResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) ListReplyAttachments(ctx context.Context, request api.ListReplyAttachmentsRequestObject) (api.ListReplyAttachmentsResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) UploadReplyAttachment(ctx context.Context, request api.UploadReplyAttachmentRequestObject) (api.UploadReplyAttachmentResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) SortReplyAttachments(ctx context.Context, request api.SortReplyAttachmentsRequestObject) (api.SortReplyAttachmentsResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) DeleteReplyAttachment(ctx context.Context, request api.DeleteReplyAttachmentRequestObject) (api.DeleteReplyAttachmentResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) UpdateReplyAttachment(ctx context.Context, request api.UpdateReplyAttachmentRequestObject) (api.UpdateReplyAttachmentResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) DownloadReplyAttachment(ctx context.Context, request api.DownloadReplyAttachmentRequestObject) (api.DownloadReplyAttachmentResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) ListGroups(ctx context.Context, request api.ListGroupsRequestObject) (api.ListGroupsResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) CreateGroup(ctx context.Context, request api.CreateGroupRequestObject) (api.CreateGroupResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) DeleteGroup(ctx context.Context, request api.DeleteGroupRequestObject) (api.DeleteGroupResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) GetGroup(ctx context.Context, request api.GetGroupRequestObject) (api.GetGroupResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) UpdateGroup(ctx context.Context, request api.UpdateGroupRequestObject) (api.UpdateGroupResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) ListTenantsGlobal(ctx context.Context, request api.ListTenantsGlobalRequestObject) (api.ListTenantsGlobalResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) CreateTenantGlobal(ctx context.Context, request api.CreateTenantGlobalRequestObject) (api.CreateTenantGlobalResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) DeleteTenantGlobal(ctx context.Context, request api.DeleteTenantGlobalRequestObject) (api.DeleteTenantGlobalResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) GetTenantGlobal(ctx context.Context, request api.GetTenantGlobalRequestObject) (api.GetTenantGlobalResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) UpdateTenantGlobal(ctx context.Context, request api.UpdateTenantGlobalRequestObject) (api.UpdateTenantGlobalResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) ListUsers(ctx context.Context, request api.ListUsersRequestObject) (api.ListUsersResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) CreateUser(ctx context.Context, request api.CreateUserRequestObject) (api.CreateUserResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) BatchAddUsersToGroup(ctx context.Context, request api.BatchAddUsersToGroupRequestObject) (api.BatchAddUsersToGroupResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) BatchRemoveUsersFromGroup(ctx context.Context, request api.BatchRemoveUsersFromGroupRequestObject) (api.BatchRemoveUsersFromGroupResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) BatchUpdateUsersField(ctx context.Context, request api.BatchUpdateUsersFieldRequestObject) (api.BatchUpdateUsersFieldResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) ListAvailableMembers(ctx context.Context, request api.ListAvailableMembersRequestObject) (api.ListAvailableMembersResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) BatchCreateUsers(ctx context.Context, request api.BatchCreateUsersRequestObject) (api.BatchCreateUsersResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) CheckUsername(ctx context.Context, request api.CheckUsernameRequestObject) (api.CheckUsernameResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) ImportUsers(ctx context.Context, request api.ImportUsersRequestObject) (api.ImportUsersResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) ChangeMyPassword(ctx context.Context, request api.ChangeMyPasswordRequestObject) (api.ChangeMyPasswordResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) GetUser(ctx context.Context, request api.GetUserRequestObject) (api.GetUserResponseObject, error) {
	return nil, s.notImplemented()
}

func (s *Server) UpdateUser(ctx context.Context, request api.UpdateUserRequestObject) (api.UpdateUserResponseObject, error) {
	return nil, s.notImplemented()
}
