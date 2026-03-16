package apperr

// OpenAPI contract 定義的 API error code。
const (
	ValidationError             = "VALIDATION_ERROR"
	AuthRequired                = "AUTH_REQUIRED"
	TokenExpired                = "TOKEN_EXPIRED"
	Forbidden                   = "FORBIDDEN"
	InternalError               = "INTERNAL_ERROR"
	NotImplemented              = "NOT_IMPLEMENTED"
	EstateNotFound              = "ESTATE_NOT_FOUND"
	EstateAccessDenied          = "ESTATE_ACCESS_DENIED"
	RoomNotFound                = "ROOM_NOT_FOUND"
	RentNotFound                = "RENT_NOT_FOUND"
	RentAlreadyTerminated       = "RENT_ALREADY_TERMINATED"
	TenantNotFound              = "TENANT_NOT_FOUND"
	ScheduleNotFound            = "SCHEDULE_NOT_FOUND"
	AccountingNotFound          = "ACCOUNTING_NOT_FOUND"
	GroupNotFound               = "GROUP_NOT_FOUND"
	GroupHasMembers             = "GROUP_HAS_MEMBERS"
	GroupNameAlreadyExists      = "GROUP_NAME_ALREADY_EXISTS"
	UserNotFound                = "USER_NOT_FOUND"
	UsernameAlreadyExists       = "USERNAME_ALREADY_EXISTS"
	AttachmentNotFound          = "ATTACHMENT_NOT_FOUND"
	CannotDeleteHasRoomsOrRents = "CANNOT_DELETE_HAS_ROOMS_OR_RENTS"
	CannotDeleteHasAccounting   = "CANNOT_DELETE_HAS_ACCOUNTING"
	CurrentPasswordIncorrect    = "CURRENT_PASSWORD_INCORRECT"
)
