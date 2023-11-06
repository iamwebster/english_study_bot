from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from db_connect import Connect
import random
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup 


class CheckWord(StatesGroup):
    word = State()
    stat = State()

db = Connect()
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    check_user = db.cur.execute("SELECT * FROM statistics WHERE user_id = '{}'".format(message.from_user.id)).fetchone()
    if not check_user:
        db.create_user(message.from_user.id, message.from_user.first_name)
    ikb = InlineKeyboardBuilder()
    ikb.button(text='🎮 Играть', callback_data='start_game_cb')
    ikb.button(text='📊 Посмотреть статистику', callback_data='check_stat_cb')
    ikb = ikb.adjust(1).as_markup()
    await message.answer(f'Привет, {message.from_user.first_name}!\n\nНажми <u>Играть</u> чтобы запустить викторину:',
                         parse_mode='HTML', reply_markup=ikb)


@router.callback_query(lambda message: message.data == 'start_game_cb')
async def start_game(call: CallbackQuery, state: FSMContext):
    words = db.get_words() 
    right_word = words[random.randint(0, 3)] 
    words_ikb_builder = InlineKeyboardBuilder()
    for kb in words:
        words_ikb_builder.button(text=kb[2], callback_data=str(kb[0]))
    words_ikb_builder.adjust(2)
    
    await state.set_state(CheckWord.word)
    await state.update_data(word=right_word)

    words_ikb = words_ikb_builder.as_markup()
    await call.message.answer(f'💬 Как переводится слово <b>{right_word[1]}</b>?', reply_markup=words_ikb, parse_mode='HTML')
    await call.answer()


@router.callback_query(CheckWord.word)
async def right_answer(call: CallbackQuery, bot: Bot, state: FSMContext):
    right_word = await state.get_data()
    right_word = right_word['word']
    await state.clear()
    await call.message.delete()
    if call.data == str(right_word[0]):
        await call.message.answer(f'✅ Абсолютно верно! <b>{right_word[1]}</b> переводится как <b>{right_word[2]}</b>', parse_mode='HTML')
        db.update_right(call.from_user.id)
    else:
        await call.message.answer(f'❌ Не верно! <b>{right_word[1]}</b> переводится как <b>{right_word[2]}</b>', parse_mode='HTML')
        db.update_wrong(call.from_user.id)
    await bot.send_chat_action(call.from_user.id, action='typing')
    await start_game(call, state)


@router.callback_query(F.data == 'check_stat_cb')
async def get_stat(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer()
    answers = db.get_stat(call.from_user.id)

    ikb = InlineKeyboardBuilder()
    ikb.button(text='🎮 Продолжить играть', callback_data='start_game_cb')
    ikb.button(text='🧹 Отчистить статистику', callback_data='clear_stat_cb')
    ikb.adjust(1)
    ikb = ikb.as_markup()
    await call.message.answer(f'📊 Ваша статистика:\n\n'
                         f'💬 Всего дано ответов - {answers[0] + answers[1]}\n'
                         f'✅ Количество правильных - {answers[0]}\n'
                         f'❌ Количество ошибок - {answers[1]}\n', reply_markup=ikb)


@router.callback_query(F.data == 'clear_stat_cb')
async def clear_stat_cmd(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    db.clear_stat(call.from_user.id)
    await call.message.answer('Статистика успешно обновлена.')
    await get_stat(call, state)