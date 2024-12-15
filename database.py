import aiosqlite
from config import DB_NAME

async def create_table():
    # Создаем соединение с базой данных (если она не существует, то она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Выполняем SQL-запрос к базе данных
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER, score INTEGER)''')
        # Сохраняем изменения
        await db.commit()

async def save_score(user_id, index, score):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index, score) VALUES (?, ?, ?)', (user_id, index, score))
        await db.commit()
        
async def get_score(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT score FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

async def update_quiz_index(user_id, index, score):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index, score) VALUES (?, ?, ?)', (user_id, index, score))
        # Сохраняем изменения
        await db.commit()

async def get_quiz_index(user_id):
     # Подключаемся к базе данных
     async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0