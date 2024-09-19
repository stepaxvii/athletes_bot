import os
import re
from random import choice

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    Message
)

from data_base import create_or_update_account
from keybords import (
    level_keyboard,
    time_keyboard,
    done_or_not_keyboard,
    power_keyboard
)
from main import UserFMS

router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message):
    """Обработка команды старт и предложение использования бота."""

    keybord = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='С кайфом)', callback_data='registration'
            )],
            [InlineKeyboardButton(
                text='Что за кринге? 😲', callback_data='about'
            )]

        ]
    )
    user_name = message.from_user.first_name if message.from_user else 'User'
    await message.answer(
        text=f'Здарова, {user_name}.\n'
        'Есть вариант подкачать грудь.',
        reply_markup=keybord
    )


@router.callback_query(
        lambda cq: cq.data in ['registration', 'about']
)
async def offer_of_registration(
    callback_query: CallbackQuery
):
    """Обрабатываем callback регистрации или подробностей проекта."""

    keyboard_fixed = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='Зафиксировать', callback_data='fixed_result'
            )]
        ]
    )
    keyboard_registration = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='Окей!)', callback_data='registration'
            )]
        ]
    )
    selected_option = callback_query.data
    if selected_option == 'registration':
        await callback_query.message.edit_text(
            text='Для оптимальной программы тренировок мне нужно, '
            'чтобы ты отжался максимально возможное количество раз от пола '
            'за один подход.\n<b>Я зафиксирую результат</b>. '
            'Если сейчас неудобно проверить - отожмись позже.\n'
            '\n<tg-spoiler><b>Я никуда не денусь)</b></tg-spoiler>',
            reply_markup=keyboard_fixed
        )
    if selected_option == 'about':
        await callback_query.message.edit_text(
            text='Здесь будет README',
            reply_markup=keyboard_registration
        )


@router.callback_query(lambda cq: cq.data == 'fixed_result')
async def registration_process(
    callback_query: CallbackQuery
):
    """Обрабатываем callback фиксации уровня подготовки."""

    await callback_query.message.edit_text(
        text='Выбери твой уровень плодготовки 👇',
        reply_markup=level_keyboard()
    )


@router.callback_query(lambda cq: cq.data.startswith('level_'))
async def process_level_selection(
    callback_query: CallbackQuery,
    state: FSMContext
):
    "Регистрируем уровень подготовки пользователя."

    await state.set_state(state=UserFMS.level)
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
    data = await state.get_data()
    notification = data.get('notification')
    if not notification:
        await callback_query.message.edit_text(
            text='Хочешь получать уведомления?',
            reply_markup=keybord
        )
    if notification:
        user_data = await state.get_data()
        level = user_data.get('level')
        notification_time = user_data.get('notification_time')
        await callback_query.message.edit_text(
            text='Так норм?\n'
            f'Уровень подготовки: {level}\nВремя уведомлений: {notification_time}',
            reply_markup=done_or_not_keyboard()
            )


@router.callback_query(
        lambda cq: cq.data in ['notification_yes', 'notification_no']
)
async def process_notification_selection(
    callback_query: CallbackQuery,
    state: FSMContext
):
    """Регистрируем уведомления."""

    selected_option = callback_query.data

    if selected_option == 'notification_no':
        user_data = await state.get_data()
        level = user_data.get('level')
        create_or_update_account(
            user_tg_id=callback_query.from_user.id,
            level=level,
            notification=0,
            notification_time='8:00'
        )
        await callback_query.message.answer(
            text='Регистрация завершена без уведомлений.',
            reply_markup=power_keyboard()
        )

    elif selected_option == 'notification_yes':
        await state.update_data(notification=1)
        await callback_query.message.edit_text(
            text='В какое время удобно будет получать уведомления?',
            reply_markup=time_keyboard()
        )


@router.callback_query(lambda cq: cq.data.startswith('time_'))
async def process_notification_time_selection(
    callback_query: CallbackQuery,
    state: FSMContext
):
    """Фиксируем время уведомлений и предлагаем проверку."""

    await state.set_state(state=UserFMS.notification_time)
    data = str(callback_query.data)
    hour = int(re.findall(r'\d+', data)[0])
    await state.update_data(notification_time=f'{hour}:00')
    user_data = await state.get_data()
    level = user_data.get('level')
    notification_time = user_data.get('notification_time')
    await callback_query.message.edit_text(
        text='Отлично 👌\n\nПроверь, всё ли верно?\n'
        f'Уровень подготовки: {level}\nВремя уведомлений: {notification_time}',
        reply_markup=done_or_not_keyboard()
        )


@router.callback_query(lambda cq: cq.data == 'edits')
async def edits(
    callback_query: CallbackQuery
):
    """Уточнение данных требующих изменения."""

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='Количество отжиманий 🦾', callback_data='edit_pushups'
            )],
            [InlineKeyboardButton(
                text='Уведомления ⏰', callback_data='edit_notification'
            )]
        ]
    )
    await callback_query.message.answer(
        text='Что именно нужно исправить?',
        reply_markup=keyboard
    )


@router.callback_query(lambda cq: cq.data.startswith('edit_'))
async def edit_data(
    callback_query: CallbackQuery,
    state: FSMContext
):
    """Изменение данных перед регистрацией."""

    if callback_query.data == 'edit_notification':
        await state.set_state(state=UserFMS.notification_time)
        await callback_query.message.edit_text(
            text='В какое время удобно будет получать уведомления?',
            reply_markup=time_keyboard()
        )
    if callback_query.data == 'edit_pushups':
        await state.set_state(state=UserFMS.level)
        await callback_query.message.edit_text(
            text='Выбери твой уровень плодготовки 👇',
            reply_markup=level_keyboard()
        )


@router.callback_query(lambda cq: cq.data == 'create_a_record')
async def add_data_in_data_base(
    callback_query: CallbackQuery,
    state: FSMContext
):
    """Запись аккаунта пользователя в базу данных."""

    user_data = await state.get_data()
    level = user_data.get('level')
    notification = user_data.get('notification')
    notification_time = user_data.get('notification_time')
    create_or_update_account(
        user_tg_id=callback_query.from_user.id,
        level=level,
        notification=notification,
        notification_time=notification_time
    )
    await callback_query.message.answer(
        text='Кайф.\n\nПока на этом всё)',
        reply_markup=power_keyboard()
    )
    await state.clear()


@router.callback_query(lambda cq: cq.data == 'power')
async def send_power_phrases(
    callback_query: CallbackQuery
):
    """Заряд бодрости для пользователя."""
    words = os.getenv('POWER_WORDS').split(',')
    word = choice(words)
    await callback_query.message.edit_text(
        text=f'ТЫ {word.upper()}!',
        reply_markup=power_keyboard()
    )


@router.message()
async def message_handler(message: Message):
    """Обработчик неизвестного действия."""
    await message.answer_sticker(
        sticker='CAACAgIAAxkBAAEInlhm7HsqaNeN-g'
        'YRHz4IwZGRcRjU1gACCU8AAv0-OUi0dANZez_9_jYE'
    )
