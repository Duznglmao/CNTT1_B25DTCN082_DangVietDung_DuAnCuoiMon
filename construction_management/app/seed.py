from datetime import datetime, timezone, timedelta
from loguru import logger

from app.db import SessionLocal
from app.models import (
    UserModel,
    RoleUser,
    ConstructionSiteModel,
    SiteMemberModel,
    MemberRole,
    WorkItemModel,
    WorkItemStatus,
    WorkItemPriority,
)
from app.core import hash_password


def seed_data():
    db = SessionLocal()
    try:
        if db.query(UserModel).first():
            logger.info("Database đã có sẵn dữ liệu. Bỏ qua bước seed.")
            return

        logger.info("Bắt đầu tạo dữ liệu mẫu!")

        admin_user = UserModel(
            email="dungxyz9999@construct.com",
            password_hash=hash_password("Dungxyz1234"),
            full_name="dangvietdung",
            role=RoleUser.ADMIN,
            is_active=True,
        )

        owner_user = UserModel(
            email="owner@construct.com",
            password_hash=hash_password("Owner@12345"),
            full_name="Nguyễn Văn Chủ Đầu Tư",
            role=RoleUser.USER,
            is_active=True,
        )

        member_user = UserModel(
            email="member@construct.com",
            password_hash=hash_password("Member@12345"),
            full_name="Trần Văn Thợ Xây",
            role=RoleUser.USER,
            is_active=True,
        )

        db.add_all([admin_user, owner_user, member_user])
        db.commit()
        db.refresh(admin_user)
        db.refresh(owner_user)
        db.refresh(member_user)

        site1 = ConstructionSiteModel(
            name="Chung cư cao cấp Sunshine Tower",
            description="Dự án xây dựng chung cư 20 tầng tại Cầu Giấy, Hà Nội.",
            owner_id=owner_user.id,
            is_deleted=False,
        )

        site2 = ConstructionSiteModel(
            name="Biệt thự sinh thái Green Park",
            description="Khu đô thị nhà ở liền kề ven đô.",
            owner_id=admin_user.id,
            is_deleted=False,
        )

        db.add_all([site1, site2])
        db.commit()
        db.refresh(site1)
        db.refresh(site2)

        member_link_1 = SiteMemberModel(
            site_id=site1.id, user_id=owner_user.id, role=MemberRole.OWNER
        )
        member_link_2 = SiteMemberModel(
            site_id=site1.id, user_id=member_user.id, role=MemberRole.MEMBER
        )
        member_link_3 = SiteMemberModel(
            site_id=site2.id, user_id=admin_user.id, role=MemberRole.OWNER
        )
        member_link_4 = SiteMemberModel(
            site_id=site2.id, user_id=member_user.id, role=MemberRole.MEMBER
        )

        db.add_all([member_link_1, member_link_2, member_link_3, member_link_4])
        db.commit()

        item1 = WorkItemModel(
            site_id=site1.id,
            title="Đổ móng và cốt thép tầng 1",
            description="Thi công phần móng chính khối A theo đúng bản vẽ thiết kế kỹ thuật.",
            assignee_id=member_user.id,
            status=WorkItemStatus.IN_PROGRESS,
            priority=WorkItemPriority.HIGH,
            due_date=datetime.now(timezone.utc) + timedelta(days=7),
        )

        item2 = WorkItemModel(
            site_id=site1.id,
            title="Khảo sát hiện trạng và định vị mặt bằng",
            description="Đã hoàn thành đo đạc trắc địa và bàn giao mốc ranh giới.",
            assignee_id=owner_user.id,
            status=WorkItemStatus.DONE,
            priority=WorkItemPriority.MEDIUM,
            due_date=datetime.now(timezone.utc) - timedelta(days=3),
        )

        item3 = WorkItemModel(
            site_id=site2.id,
            title="Lắp đặt hệ thống điện nước ngầm",
            description="Thi công đường ống cấp thoát nước tổng toàn khu biệt thự.",
            assignee_id=member_user.id,
            status=WorkItemStatus.TODO,
            priority=WorkItemPriority.HIGH,
            due_date=datetime.now(timezone.utc) + timedelta(days=14),
        )

        db.add_all([item1, item2, item3])
        db.commit()

        logger.info("Seed dữ liệu mẫu thành công.")

    except Exception as e:
        db.rollback()
        logger.error(f"Lỗi xảy ra trong quá trình seed dữ liệu: {e}")
    finally:
        db.close()

