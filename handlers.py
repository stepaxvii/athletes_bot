import re

from aiogram import Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    Message
)
from main import Session, User, UserFMS
from keybords import level_keyboard, time_keyboard

router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message):
    """Обработка команды старт и предложение использования бота."""
    keybord = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='Регистрация', callback_data='registration'
            )]
        ]
    )
    user_name = message.from_user.first_name if message.from_user else 'User'
    await message.answer(
        text=f'Здарова, {user_name}.\n',
        reply_markup=keybord
    )


@router.callback_query(lambda cq: cq.data == 'registration')
async def registration_process(
    callback_query: CallbackQuery,
    state: FSMContext
):
    """Обрабатываем callback регистрации."""
    await callback_query.message.answer(
        text='Сколько?',
        reply_markup=level_keyboard()
    )
    await state.set_state(UserFMS.level)


@router.callback_query(lambda cq: cq.data.startswith('level_'))
async def process_level_selection(
    callback_query: CallbackQuery,
    state: FSMContext
):
    "Регистрируем уровень подготовки пользователя."
    data = str(callback_query.data)
    level = int(re.findall(r'\d+', data)[0])
    await state.update_data(level=level)
    keybord = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='да', callback_data='notification_yes'
            )],
            [InlineKeyboardButton(
                text='нет', callback_data='notification_no'
            )]
        ]
    )
    await callback_query.message.edit_text(
        text='Хотите ли вы получать уведомления?',
        reply_markup=keybord
    )
    await state.set_state(UserFMS.notification)


@router.callback_query(
        lambda cq: cq.data in ['notification_yes', 'notification_no']
)
async def process_notification_selection(
    callback_query: CallbackQuery,
    state: FSMContext
):
    """Регистрируем уведомления."""
    selected_option = callback_query.data

    user_data = await state.get_data()
    level = user_data.get('level')

    session = Session()

    if selected_option == 'notification_no':
        new_user = User(user_tg_id=callback_query.from_user.id, level=level)
        session.add(new_user)
        session.commit()
        session.close()
        await callback_query.message.answer(
            text='Регистрация завершена без уведомлений.'
        )

    elif selected_option == 'notification_yes':
        await state.update_data(notification=1)
        await callback_query.message.edit_text(
            text='В какое время удобно будет получать уведомления?',
            reply_markup=time_keyboard()
        )

    await state.set_state(UserFMS.notification_time)


@router.callback_query(lambda cq: cq.data.startswith('time_'))
async def process_notification_time_selection(
    callback_query: CallbackQuery,
    state: FSMContext
):
    """Регистрируем время уведомлений."""
    data = str(callback_query.data)
    hour = int(re.findall(r'\d+', data)[0])
    await state.update_data(notification_time=f'{hour}:00')
    await callback_query.answer(
        text='Done)',
        reply_markup=None
        )
    user_data = await state.get_data()
    level = user_data.get('level')
    notification = user_data.get('notification')
    notification_time = user_data.get('notification_time')
    session = Session()
    new_user = User(
        user_tg_id=callback_query.from_user.id,
        level=level,
        notification=notification,
        notification_time=notification_time
        )
    session.add(new_user)
    session.commit()
    session.close()
    await state.clear()
    await callback_query.message.answer(
        text=')))',
        reply_markup=None
    )
