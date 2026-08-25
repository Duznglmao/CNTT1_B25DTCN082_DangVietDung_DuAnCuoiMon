from fastapi import status


class AppException(Exception):
    def __init__(self, message: str, status_code: int, error_code: str):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code


class ExpiredSignatureException(AppException):
    def __init__(self):
        super().__init__(
            message="Token đã hết hạn!",
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="EXPIRED_SIGNATURE",
        )


class InvalidTokenException(AppException):
    def __init__(self):
        super().__init__(
            message="Token không hợp lệ!",
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="INVALID_TOKEN",
        )


class UserAlreadyExistsError(AppException):
    def __init__(self, value: str | int):
        super().__init__(
            message=f"Người dùng với {value} đã tồn tại!",
            status_code=status.HTTP_409_CONFLICT,
            error_code="USER_ALREADY_EXISTS",
        )


class InvalidCredentialsError(AppException):
    def __init__(self):
        super().__init__(
            message="Xác minh danh tính thất bại!",
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="INVALID_CREDENTIALS_ERROR",
        )


class InactiveUserError(AppException):
    def __init__(self):
        super().__init__(
            message="Tài khoản không còn hành động!",
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="INACTIVE_USER_ERROR",
        )


class UserNotFoundError(AppException):
    def __init__(self, value: str | int):
        super().__init__(
            message=f"Không tìm thấy tài khoản với {value}",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="USER_NOT_FOUND",
        )


class SiteNotFoundError(AppException):
    def __init__(self, site_id: int):
        super().__init__(
            message=f"Không tìm thấy công trường với ID {site_id}",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="SITE_NOT_FOUND",
        )


class PermissionDeniedError(AppException):
    def __init__(self, message: str = "Bạn không có quyền thực hiện thao tác này!"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="PERMISSION_DENIED",
        )


class MemberAlreadyExistsError(AppException):
    def __init__(self):
        super().__init__(
            message="Người dùng đã là thành viên của công trường này!",
            status_code=status.HTTP_409_CONFLICT,
            error_code="MEMBER_ALREADY_EXISTS",
        )


class CannotRemoveOwnerError(AppException):
    def __init__(self):
        super().__init__(
            message="Không thể xóa Owner khỏi công trường!",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="CANNOT_REMOVE_OWNER",
        )


class InvalidAssigneeError(AppException):
    def __init__(self):
        super().__init__(
            message="Người được gán (Assignee) không thuộc công trường này!",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_ASSIGNEE",
        )


class WorkItemNotFoundError(AppException):
    def __init__(self):
        super().__init__(
            message="Không tìm thấy hạng mục thi công!",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="WORK_ITEM_NOT_FOUND",
        )


class InvalidFileTypeError(AppException):
    def __init__(self):
        super().__init__(
            message="Chỉ chấp nhận file JPG, PNG, PDF!",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_FILE_TYPE",
        )


class FileTooLargeError(AppException):
    def __init__(self):
        super().__init__(
            message="Kích thước file vượt quá 5MB!",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="FILE_TOO_LARGE",
        )
