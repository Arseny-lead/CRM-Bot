from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards import main_menu, funcs_kb, state_kb


from database import (add_client,
                      format_clients_list,
                      get_all_clients,
                      get_stats,
                      format_stats,
                      get_client_by_id,
                      update_client_field)

router = Router()

class Form(StatesGroup):
    choosing_client = State()
    choosing_field = State()
    editing_value = State()
    user_name = State()
    user_phone = State()
    user_mail = State()
    user_comm = State()
    user_tg = State()
    user_source = State()

user_data = []


@router.message(CommandStart())
async def start_command(message: Message):
    await message.answer("Привет! Выбери действие:", reply_markup=main_menu)


@router.message(F.text == "Функции")
async def help_command(message: Message):
    await message.answer(
        "📋 Доступные команды:\n"
        "1️⃣ Статистика — посмотреть текущую статистику.\n"
        "2️⃣ Изменить информацию о клиенте.\n"
        "3️⃣ Список клиентов — просмотреть всех клиентов.\n"
        "4️⃣ Добавить клиента — добавить нового клиента в базу.", reply_markup=funcs_kb)


@router.message(F.text == "Отмена действия")
async def cancel_command(message: Message, state: FSMContext):
    current_state = await state.get_state()

    await state.clear()
    await message.answer("Действие отменено", reply_markup=funcs_kb)


@router.message(F.text == "О боте")
async def about_bot_command(message: Message):
    await message.answer("🤖 *CRM-бот*\n\n"
                         "Бот для управления клиентами и заявками.\n"
                         "Помогает вести базу, контролировать статусы, получать напоминания и ускорять работу.",
                         reply_markup=main_menu)


@router.message(F.text == "Добавить клиента")
async def add_client_command(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Введите имя клиента:", reply_markup=state_kb)
    await state.set_state(Form.user_name)


@router.message(Form.user_name)  # Добавить имя клиента
async def get_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        await message.answer("Имя не может быть пустым. Введите имя:")
        return

    await state.update_data(name=name)
    await message.answer("Введите телефон (только цифры, например 89991234567):")
    await state.set_state(Form.user_phone)


@router.message(Form.user_phone)  # Добавить телефон клиента
async def get_phone(message: Message, state: FSMContext):
    raw = message.text.strip()
    digits = "".join(ch for ch in raw if ch.isdigit())

    if len(digits) < 7:
        await message.answer("Телефон слишком короткий. Введите корректный номер:")
        return

    await state.update_data(phone=digits)
    await message.answer("Введите Email (или отправьте '-' если нет):")
    await state.set_state(Form.user_mail)


@router.message(Form.user_mail)  # Добавить Email клиента
async def get_email(message: Message, state: FSMContext):
    email = None if message.text == "-" else message.text
    await state.update_data(email=email)
    await message.answer("Введите комментарий к клиенту (или '-' если нет):")
    await state.set_state(Form.user_comm)


@router.message(Form.user_comm)  # Добавить комментарий к клиенту
async def get_comment(message: Message, state: FSMContext):
    notes = None if message.text == "-" else message.text
    await state.update_data(notes=notes)
    await message.answer("Введите Telegram ID клиента (или '-' если нет):")
    await state.set_state(Form.user_tg)


@router.message(Form.user_tg)  # Добавить Telegram ID клиента
async def get_telegram(message: Message, state: FSMContext):
    telegram_id = None if message.text == "-" else message.text
    await state.update_data(telegram_id=telegram_id)
    await message.answer("Введите источник появления клиента:")
    await state.set_state(Form.user_source)


@router.message(Form.user_source)  # Добавить источник появления клиента
async def get_source(message: Message, state: FSMContext):
    # Сохраняем источник
    source = None if message.text == "-" else message.text
    await state.update_data(source=source)

    data = await state.get_data()
    print(data)

    name = data.get("name")
    phone = data.get("phone")
    email = data.get("email")
    notes = data.get("notes")
    telegram_id = data.get("telegram_id")
    source = data.get("source")

    # Добавляем клиента в базу
    add_client(name, phone, email, notes, telegram_id, source)

    await message.answer(
        f"✅ *Клиент добавлен!*\n\n"
        f"👤 Имя: {name}\n"
        f"📞 Телефон: {phone}\n"
        f"✉️ Email: {email or '-'}\n"
        f"📝 Комментарий: {notes or '-'}\n"
        f"💬 Telegram ID: {telegram_id or '-'}\n"
        f"📍 Источник: {source or '-'}",
        parse_mode="Markdown",
        reply_markup=funcs_kb
    )

    await state.clear()


@router.message(F.text == "Список клиентов")
async def get_clients_func(message: Message):
    await message.answer(format_clients_list(get_all_clients()))


@router.message(F.text == "Статистика")
async def get_stats_func(message: Message):
    await message.answer(format_stats(get_stats()))


@router.message(F.text == "Изменить информацию о клиенте")
async def start_edit(message: Message, state: FSMContext):
    clients = get_all_clients()

    if not clients:
        await message.answer("📭 Клиентов для редактирования нет")
        return

    formatted = format_clients_list(clients)
    await message.answer(
        f"{formatted}\n\n"
        "Введите ID клиента для редактирования:"
    )
    await state.set_state(Form.choosing_client)


@router.message(Form.choosing_client)
async def choose_client(message: Message, state: FSMContext):
    try:
        client_id = int(message.text)
        client = get_client_by_id(client_id)

        if not client:
            await message.answer("❌ Клиент с таким ID не найден. Попробуйте снова:")
            return

        await state.update_data(client_id=client_id, client_data=client)

        await message.answer(
            f"👤 Редактируем клиента:\n"
            f"ID: {client_id}\n"
            f"Имя: {client[1]}\n"
            f"Телефон: {client[2]}\n\n"
            "Какое поле хотите изменить?\n"
            "1 - Имя\n2 - Телефон\n3 - Email\n4 - Статус\n5 - Заметки\n6 - Источник"
        )
        await state.set_state(Form.choosing_field)

    except ValueError:
        await message.answer("❌ Введите корректный ID (число):")


@router.message(Form.choosing_field)
async def choose_field(message: Message, state: FSMContext):
    field_map = {
        '1': 'name',
        '2': 'phone',
        '3': 'email',
        '4': 'status',
        '5': 'notes',
        '6': 'source'
    }

    choice = message.text
    if choice not in field_map:
        await message.answer("❌ Выберите число от 1 до 6:")
        return

    field_name = field_map[choice]
    await state.update_data(editing_field=field_name)

    field_names = {
        'name': 'имя',
        'phone': 'телефон',
        'email': 'email',
        'status': 'статус',
        'notes': 'заметки',
        'source': 'источник'
    }

    await message.answer(f"Введите новое значение для {field_names[field_name]}:")
    await state.set_state(Form.editing_value)


@router.message(Form.editing_value)
async def save_edit(message: Message, state: FSMContext):
    data = await state.get_data()
    client_id = data['client_id']
    field = data['editing_field']
    new_value = message.text

    try:
        update_client_field(client_id, field, new_value)
        await message.answer("✅ Данные клиента обновлены!")

    except Exception as e:
        await message.answer(f"❌ Ошибка при обновлении: {e}")

    finally:
        await state.clear()
