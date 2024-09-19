from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def power_keyboard():
    """Создание клавиатуры для отправки мотивационных фраз."""

    keybord = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='⚡️',
                callback_data='power'
            )]
        ]
    )
    return keybord


def done_or_not_keyboard():
    """Создание клавиатуры подтверждения."""

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='✔️', callback_data='create_a_record'
            )],
            [InlineKeyboardButton(
                text='✖️', callback_data='edits'
            )],
        ]
    )
    return keyboard


def level_keyboard():
    """Создание клавиатуры с вариантами уровня."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='0-10', callback_data='level_0')],
            [InlineKeyboardButton(text='10-20', callback_data='level_1')],
            [InlineKeyboardButton(text='20-30', callback_data='level_2')],
            [InlineKeyboardButton(text='30-40', callback_data='level_3')],
            [InlineKeyboardButton(text='40-50', callback_data='level_4')],
            [InlineKeyboardButton(text='50-60', callback_data='level_5')]
        ],
        row_width=2
    )
    return keyboard


def time_keyboard():
    """Сооздание клавиатуры с вариантами времени."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='05:00', callback_data='time_5')],
            [InlineKeyboardButton(text='06:00', callback_data='time_6')],
            [InlineKeyboardButton(text='07:00', callback_data='time_7')],
            [InlineKeyboardButton(text='08:00', callback_data='time_8')],
            [InlineKeyboardButton(text='09:00', callback_data='time_9')],
            [InlineKeyboardButton(text='10:00', callback_data='time_10')],
            [InlineKeyboardButton(text='11:00', callback_data='time_11')],
            [InlineKeyboardButton(text='12:00', callback_data='time_12')],
            [InlineKeyboardButton(text='13:00', callback_data='time_13')],
            [InlineKeyboardButton(text='14:00', callback_data='time_14')]
        ],
        row_width=2
    )

    return keyboard
