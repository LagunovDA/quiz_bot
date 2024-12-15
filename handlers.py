from aiogram import Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F
from database import update_quiz_index, get_quiz_index, get_score, save_score
from questions import quiz_data
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from keyboards import generate_options_keyboard


dp = Dispatcher()

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Создаем сборщика клавиатур типа Reply
    builder = ReplyKeyboardBuilder()
    # Добавляем в сборщик одну кнопку
    builder.add(types.KeyboardButton(text="Начать игру"))
    # Прикрепляем кнопки к сообщению
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))
    
    

# Хэндлер на команды /quiz
@dp.message(F.text=="Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    # Отправляем новое сообщение без кнопок
    await message.answer(f"Давайте начнем квиз!")
    # Запускаем новый квиз
    await new_quiz(message)

   
async def new_quiz(message):
    # получаем id пользователя, отправившего сообщение
    user_id = message.from_user.id
    # сбрасываем значение текущего индекса вопроса квиза в 0
    current_question_index = 0
    current_score_index = 0
    await update_quiz_index(user_id, current_question_index, current_score_index)
    # запрашиваем новый вопрос для квиза
    await get_question(message, user_id)

    
async def get_question(message, user_id):
    # Запрашиваем из базы текущий индекс для вопроса
    current_question_index = await get_quiz_index(user_id)
    # Получаем индекс правильного ответа для текущего вопроса
    correct_index = quiz_data[current_question_index]['correct_option']
    # Получаем список вариантов ответа для текущего вопроса
    opts = quiz_data[current_question_index]['options']
    # Функция генерации кнопок для текущего вопроса квиза
    # В качестве аргументов передаем варианты ответов и значение правильного ответа (не индекс!)
    kb = generate_options_keyboard(opts, opts[correct_index])
    # Отправляем в чат сообщение с вопросом, прикрепляем сгенерированные кнопки
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)

    

@dp.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):
    await handle_answer(callback, True)

@dp.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    await handle_answer(callback, False)
    
           
async def handle_answer(callback: types.CallbackQuery, is_correct: bool):  
    user_id = callback.from_user.id    
    current_question_index = await get_quiz_index(callback.from_user.id) 
    current_score = await get_score(user_id)
    correct_option = quiz_data[current_question_index]['correct_option']
    await callback.bot.edit_message_reply_markup(chat_id=callback.from_user.id, message_id=callback.message.message_id, reply_markup=None)   
    
    if is_correct:
        await callback.message.answer("Верно!")        
        current_score = await get_score(callback.from_user.id)
        current_score += 1  # Увеличиваем счет на 1 за правильный ответ
        await save_score(callback.from_user.id, current_question_index, current_score)
    else:
        # correct_option = quiz_data[current_question_index -1]['correct_option']
        await callback.message.answer(f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")

    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index, current_score)
    
    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        current_score = await get_score(user_id)
        await callback.message.answer(f"Это был последний вопрос. Квиз завершен! Ваш результат: {current_score} правильных ответов.")
        await save_score(callback.from_user.id, current_question_index, current_score)