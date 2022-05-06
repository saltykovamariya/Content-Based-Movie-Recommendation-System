from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import emoji

answers = ['Да ✅', 'Нет ❌']
choice = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
for i in answers:
    choice.add(KeyboardButton(i))