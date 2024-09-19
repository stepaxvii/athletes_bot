from sqlalchemy import (
    create_engine,
    Boolean,
    Column,
    Date,
    Integer,
    ForeignKey,
    String
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker


# Настраиваем базу данных
DATA_URL = "sqlite:///athletes_.db"
Base = declarative_base()
engine = create_engine(DATA_URL)
Session = sessionmaker(bind=engine)

Session()
session = Session()


class User(Base):
    """Модель пользователя."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_tg_id = Column(Integer, unique=True, nullable=False)
    level = Column(Integer, default=0)
    notification = Column(Boolean, default=False)
    notification_time = Column(String, default="8:00")


class Achievement(Base):
    """Модель достижений."""

    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    push_ups_count = Column(Integer, nullable=False)


# Создаём таблицы
Base.metadata.create_all(engine)


def create_or_update_account(
        user_tg_id, level, notification, notification_time
):
    """Создание или обновление аккаунта пользователя."""

    # Поиск пользователя в базе данных
    user = session.query(User).filter_by(user_tg_id=user_tg_id).first()

    if user:
        # Обновление полей, если они отличаются
        updated = False
        if user.level != level:
            user.level = level
            updated = True
        if user.notification != notification:
            user.notification = notification
            updated = True
        if user.notification_time != notification_time:
            user.notification_time = notification_time
            updated = True

        if updated:
            session.commit()
    else:
        # Если пользователь не найден, создаем нового
        new_user = User(
            user_tg_id=user_tg_id,
            level=level,
            notification=notification,
            notification_time=notification_time
        )
        session.add(new_user)
        session.commit()

    session.close()
