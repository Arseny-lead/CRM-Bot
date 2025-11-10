from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Функции"), KeyboardButton(text="О боте")]
    ],
    resize_keyboard=True
)


funcs_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Статистика"), KeyboardButton(text="Список клиентов")],
        [KeyboardButton(text="Добавить клиента")],
        [KeyboardButton(text="Изменить информацию о клиенте")],
        [KeyboardButton(text="/start")], [KeyboardButton(text="О боте")]
    ],
    resize_keyboard=True
)


state_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отмена действия")]
    ],
    resize_keyboard=True
)


skip_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Пропустить шаг")]
    ]
)