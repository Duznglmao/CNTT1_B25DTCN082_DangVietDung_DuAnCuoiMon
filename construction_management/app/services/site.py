from sqlalchemy.orm import Session, joinedload

from app.models import (
    ConstructionSiteModel,
    SiteMemberModel,
    ActivityLogModel,
    UserModel,
    MemberRole,
)
from app.schemas import ConstructionSiteCreate, ConstructionSiteUpdate, SiteMemberCreate
from app.exceptions import (
    SiteNotFoundError,
    PermissionDeniedError,
    UserNotFoundError,
    MemberAlreadyExistsError,
    CannotRemoveOwnerError,
)


class SiteService:
    def __init__(self, db: Session):
        self.db = db

    def log_activity(
        self, user_id: int, site_id: int, action: str, details: str = None
    ) -> None:
        log_entry = ActivityLogModel(
            user_id=user_id, site_id=site_id, action=action, details=details
        )
        self.db.add(log_entry)

    def create_site(
        self, site_data: ConstructionSiteCreate, current_user: UserModel
    ) -> ConstructionSiteModel:
        new_site = ConstructionSiteModel(
            name=site_data.name,
            description=site_data.description,
            owner_id=current_user.id,
        )
        self.db.add(new_site)
        self.db.flush()

        new_member = SiteMemberModel(
            site_id=new_site.id, user_id=current_user.id, role=MemberRole.OWNER
        )
        self.db.add(new_member)

        self.log_activity(
            user_id=current_user.id,
            site_id=new_site.id,
            action="CREATE_SITE",
            details=f"Tạo công trình: {site_data.name}",
        )
        self.db.commit()
        self.db.refresh(new_site)
        return new_site

    def get_sites(
        self, current_user: UserModel, search_name: str = None
    ) -> list[ConstructionSiteModel]:
        query = (
            self.db.query(ConstructionSiteModel)
            .join(SiteMemberModel)
            .filter(
                SiteMemberModel.user_id == current_user.id,
                ConstructionSiteModel.is_deleted == False,
            )
        )

        if search_name:
            query = query.filter(
                ConstructionSiteModel.name.ilike(f"%{search_name.strip()}%")
            )

        return query.all()

    def get_site_detail(
        self, site_id: int, current_user: UserModel
    ) -> ConstructionSiteModel:
        site_record = (
            self.db.query(ConstructionSiteModel)
            .filter(
                ConstructionSiteModel.id == site_id,
                ConstructionSiteModel.is_deleted == False,
            )
            .first()
        )

        if not site_record:
            raise SiteNotFoundError(site_id)

        is_member = (
            self.db.query(SiteMemberModel)
            .filter(
                SiteMemberModel.site_id == site_id,
                SiteMemberModel.user_id == current_user.id,
            )
            .first()
        )

        if not is_member:
            raise PermissionDeniedError(
                "Bạn không phải là thành viên của công trình này!"
            )

        return site_record

    def check_owner_access(self, site_id: int, user_id: int) -> ConstructionSiteModel:
        site_record = (
            self.db.query(ConstructionSiteModel)
            .filter(
                ConstructionSiteModel.id == site_id,
                ConstructionSiteModel.is_deleted == False,
            )
            .first()
        )

        if not site_record:
            raise SiteNotFoundError(site_id)

        if site_record.owner_id != user_id:
            raise PermissionDeniedError(
                "Chỉ Owner mới có quyền chỉnh sửa hoặc xóa công trình!"
            )

        return site_record

    def update_site(
        self, site_id: int, update_data: ConstructionSiteUpdate, current_user: UserModel
    ) -> ConstructionSiteModel:
        site_record = self.check_owner_access(site_id, current_user.id)

        update_dict = update_data.model_dump(exclude_unset=True)

        for key, value in update_dict.items():
            setattr(site_record, key, value)

        self.log_activity(
            user_id=current_user.id,
            site_id=site_record.id,
            action="UPDATE_SITE",
            details="Cập nhật thông tin công trình",
        )

        self.db.commit()
        self.db.refresh(site_record)
        return site_record

    def delete_site(self, site_id: int, current_user: UserModel) -> None:
        site_record = self.check_owner_access(site_id, current_user.id)

        site_record.is_deleted = True

        self.log_activity(
            user_id=current_user.id,
            site_id=site_record.id,
            action="DELETE_SITE",
            details="Xóa công trình (soft delete)",
        )
        self.db.commit()

    def add_member(
        self, site_id: int, member_data: SiteMemberCreate, current_user: UserModel
    ) -> SiteMemberModel:
        site_record = self.check_owner_access(site_id, current_user.id)

        target_user = (
            self.db.query(UserModel)
            .filter(UserModel.id == member_data.user_id, UserModel.is_active == True)
            .first()
        )

        if not target_user:
            raise UserNotFoundError(member_data.user_id)

        existing_member = (
            self.db.query(SiteMemberModel)
            .filter(
                SiteMemberModel.site_id == site_id,
                SiteMemberModel.user_id == member_data.user_id,
            )
            .first()
        )

        if existing_member:
            raise MemberAlreadyExistsError()

        new_member = SiteMemberModel(
            site_id=site_id, user_id=member_data.user_id, role=member_data.role
        )
        self.db.add(new_member)

        self.log_activity(
            user_id=current_user.id,
            site_id=site_record.id,
            action="ADD_MEMBER",
            details=f"Thêm thành viên ID: {member_data.user_id}",
        )
        self.db.commit()
        self.db.refresh(new_member)
        return new_member

    def remove_member(
        self, site_id: int, target_user_id: int, current_user: UserModel
    ) -> None:
        site_record = self.check_owner_access(site_id, current_user.id)

        if site_record.owner_id == target_user_id:
            raise CannotRemoveOwnerError()

        member_record = (
            self.db.query(SiteMemberModel)
            .filter(
                SiteMemberModel.site_id == site_id,
                SiteMemberModel.user_id == target_user_id,
            )
            .first()
        )

        if not member_record:
            raise UserNotFoundError(target_user_id)

        self.db.delete(member_record)

        self.log_activity(
            user_id=current_user.id,
            site_id=site_record.id,
            action="REMOVE_MEMBER",
            details=f"Xóa thành viên ID: {target_user_id}",
        )
        self.db.commit()

    def get_members(
        self, site_id: int, current_user: UserModel
    ) -> list[SiteMemberModel]:
        self.get_site_detail(site_id, current_user)
        return (
            self.db.query(SiteMemberModel)
            .options(joinedload(SiteMemberModel.user))
            .filter(SiteMemberModel.site_id == site_id)
            .all()
        )
