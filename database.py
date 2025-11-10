import sqlite3 as sq
from datetime import datetime

def get_connection():
    return sq.connect('crm_bot.db')


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            created_at TEXT,
            status TEXT,
            notes TEXT,
            telegram_id TEXT,
            source TEXT
        )
    """)

    conn.commit()
    conn.close()


def add_client(name, phone, email=None, notes=None, telegram_id=None, source=None):
    create_tables()

    conn = get_connection()
    cursor = conn.cursor()

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute('''
        INSERT INTO clients (name, phone, email, created_at, notes, telegram_id, source, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'new')
    ''', (name, phone, email, created_at, notes, telegram_id, source))

    conn.commit()
    conn.close()


def get_all_clients():
    conn = get_connection()
    cursor = conn.cursor()

    # Выбираем имя, телефон, статус и дату
    cursor.execute('''
        SELECT name, phone, status, created_at
        FROM clients
        ORDER BY created_at DESC
    ''')
    clients = cursor.fetchall()
    conn.close()
    return clients


def format_clients_list(clients):
    if not clients:
        return "📭 Клиентов пока нет"

    result = ["📋 Список клиентов:\n"]
    for i, client in enumerate(clients, 1):
        name, phone, status, created_at = client

        date_str = "неизвестно"
        if created_at:
            try:
                date_obj = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
                date_str = date_obj.strftime("%d.%m")
            except:
                date_str = created_at[:5]  # fallback

        result.append(f"{i}. 👤 {name} | 📞 {phone} | 🏷️ {status} | 📅 {date_str}")

    return "\n".join(result)


def get_stats():
    conn = get_connection()
    cursor = conn.cursor()

    # Общее количество клиентов
    cursor.execute('SELECT COUNT(*) FROM clients')
    total = cursor.fetchone()[0]

    # Клиенты по статусам
    cursor.execute('SELECT status, COUNT(*) FROM clients GROUP BY status')
    status_counts = dict(cursor.fetchall())

    # Клиенты за сегодня
    cursor.execute('''
        SELECT COUNT(*) FROM clients
        WHERE DATE(created_at) = DATE('now')
    ''')
    today = cursor.fetchone()[0]

    # Клиенты за неделю
    cursor.execute('''
        SELECT COUNT(*) FROM clients
        WHERE created_at >= DATE('now', '-7 days')
    ''')
    week = cursor.fetchone()[0]

    conn.close()

    return {
        'total': total,
        'by_status': status_counts,
        'today': today,
        'week': week
    }


def format_stats(stats):
    total = stats['total']
    by_status = stats['by_status']
    today = stats['today']
    week = stats['week']

    # Получаем значения статусов (если нет - 0)
    new = by_status.get('new', 0)
    active = by_status.get('active', 0)
    completed = by_status.get('completed', 0)

    return (
        "📊 Статистика CRM:\n\n"
        f"👥 Всего клиентов: {total}\n\n"
        f"🏷️ По статусам:\n"
        f"   • Новые: {new}\n"
        f"   • В работе: {active}\n"
        f"   • Завершённые: {completed}\n\n"
        f"📈 Активность:\n"
        f"   • Сегодня: {today}\n"
        f"   • За неделю: {week}"
    )


def get_client_by_id(client_id):
    """Получить клиента по ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (client_id,))
    client = cursor.fetchone()
    conn.close()
    return client

def update_client_field(client_id, field, new_value):
    """Обновить поле клиента"""
    conn = get_connection()
    cursor = conn.cursor()

    # Безопасное обновление через параметры
    cursor.execute(f'UPDATE clients SET {field} = ? WHERE id = ?', (new_value, client_id))

    conn.commit()
    conn.close()