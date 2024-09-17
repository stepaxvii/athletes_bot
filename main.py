import asyncio
import logging
import sys
from os import getenv
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.state import State, StatesGroup
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
import handlers

load_dotenv()

# Из окружения извлекаем необходимые токены, ключи и переменные
TELEGRAM_TOKEN = getenv('TELEGRAM_TOKEN')

# Настраиваем базу данных
DATA_URL = 'sqlite:///athletes/athletes_.db'
Base = declarative_base()
engine = create_engine(DATA_URL)
Session = sessionmaker(bind=engine)


class User(Base):
    """Модель пользователя."""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_tg_id = Column(Integer, unique=True, nullable=False)
    level = Column(Integer, default=0)
    notification = Column(Boolean, default=False)
    notification_time = Column(String, default='8:00')


class Achievement(Base):
    """Модель достижений."""
    __tablename__ = 'achievements'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(Date, nullable=False)
    push_ups_count = Column(Integer, nullable=False)


# Создаём таблицы
Base.metadata.create_all(engine)


class UserFMS(StatesGroup):
    """Определение состояния FMS."""
    level = State()
    notification = State()
    notification_time = State()


async def main():
    bot = Bot(
        token=TELEGRAM_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.include_router(handlers.router)
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as error:
        logging.error(f'Произошла ошибка: {error}')


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
    )
    asyncio.run(main())
