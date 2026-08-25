from sqlalchemy.orm import Session
from datetime import timedelta

from app.models import UserModel
from app.schemas import UserCreate, Token
from app.exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    InactiveUserError,
    UserNotFoundError,
    InvalidTokenException,
)
from app.core import (
    hash_password,
    DUMMY_HASH,
    verify_password,
    create_access_token,
    settings,
    decode_token,
    create_refresh_token,
)


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> UserModel | None:
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    def create_user(self, user_in: UserCreate) -> UserModel | None:
        if self.get_by_email(user_in.email):
            raise UserAlreadyExistsError(user_in.email)

        user = UserModel(
            **user_in.model_dump(exclude={"password"}),
            password_hash=hash_password(user_in.password),
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate_user(self, email: str, password: str) -> UserModel | None:
        user = self.get_by_email(email)

        if not user:
            verify_password(password, DUMMY_HASH)
            return None

        if not verify_password(password, user.password_hash):
            return None

        return user

    def login(self, email: str, password: str) -> Token:
        user = self.authenticate_user(email, password)

        if not user:
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InactiveUserError()

        access_token_time = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_time = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        access_token = create_access_token(
            {"sub": user.email}, expires_delta=access_token_time
        )
        refresh_token = create_refresh_token(
            {"sub": user.email}, expires_delta=refresh_token_time
        )

        return Token(access_token=access_token, refresh_token=refresh_token)

    def refresh_token(self, refresh_token_str: str) -> Token:
        payload = decode_token(refresh_token_str)

        if payload.get("type") != "refresh":
            raise InvalidTokenException()

        email = payload.get("sub")
        if not email:
            raise InvalidTokenException()

        user = self.get_by_email(email)
        if not user:
            raise UserNotFoundError(email)

        if not user.is_active:
            raise InactiveUserError()

        access_token_time = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        new_refresh_token_time = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        new_access_token = create_access_token(
            {"sub": user.email}, expires_delta=access_token_time
        )
        new_refresh_token = create_refresh_token(
            {"sub": user.email}, expires_delta=new_refresh_token_time
        )

        return Token(access_token=new_access_token, refresh_token=new_refresh_token)

    def get_users(
        self, search: str | None = None, skip: int = 0, limit: int = 100
    ) -> list[UserModel]:
        query = self.db.query(UserModel)
        if search:
            search_filter = f"%{search.strip()}%"
            query = query.filter(
                (UserModel.full_name.ilike(search_filter))
                | (UserModel.email.ilike(search_filter))
            )
        return query.offset(skip).limit(limit).all()
