from aiogram import Dispatcher, types
from loader import dp
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove
from aiogram.dispatcher.filters import Text
from yolov5 import detect
from os import makedirs
from pathlib import Path
import datetime
import os
import shutil
from keyboards import choice
from recommendation.model import genre_recommendations, recommend, movie_data
from os.path import exists


answers = ['Да ✅', 'Нет ❌']

dict_object = {"0 ":'Алексей', "1 ":'Андрей', "2 ":'Антон', "3 ":'Денис', "4 ":'Федя', "5 ":'Ильдус', "6 ":'Иван', "7 ":'Костя', \
              "8 ":'Леша', "9 ":'Маша', "10 ":'Саня', "11":'Саша', "12":'Валера'}

top_5 = '\n\n1) The Shawshank Redemption (1994) IMDb: 9.3 \n2) The Godfather (1972) IMDb: 9.2 \n3) The Dark Knight (2008) IMDb: 9.0 \n4) The Godfather: Part II (1974) IMDb: 9.0 \n5) 12 Angry Men (1957) IMDb: 9.0'

top_5_picture =  ['https://m.media-amazon.com/images/M/MV5BMDFkYTc0MGEtZmNhMC00ZDIzLWFmNTEtODM1ZmRlYWMwMWFmXkEyXkFqcGdeQXVyMTMxODk2OTU@.jpg',
  'https://m.media-amazon.com/images/M/MV5BM2MyNjYxNmUtYTAwNi00MTYxLWJmNWYtYzZlODY3ZTk3OTFlXkEyXkFqcGdeQXVyNzkwMjQ5NzM@.jpg',
  'https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@.jpg',
  'https://m.media-amazon.com/images/M/MV5BMWMwMGQzZTItY2JlNC00OWZiLWIyMDctNDk2ZDQ2YjRjMWQ0XkEyXkFqcGdeQXVyNzkwMjQ5NzM@.jpg',
  'https://m.media-amazon.com/images/M/MV5BMWU4N2FjNzYtNTVkNC00NzQ0LTg0MjAtYTJlMjFhNGUxZDFmXkEyXkFqcGdeQXVyNjc1NTYyMjg@.jpg']

def names(dict_obj, path):
    list_names = [i[:2] for i in Path(f'{path}').read_text().split('\n')]
    text = 'На этой фотографии:'
    for k,v in dict_obj.items():
        if k in list_names:
            text +='\n' + str(v)
    return text

def rec(dict_obj, path):
    list_names = [i[:2] for i in Path(f'{path}').read_text().split('\n')]
    name = []
    for k,v in dict_obj.items():
        if k in list_names:
            name.append(v)
    return name

class Form(StatesGroup):
    start = State()
    detection = State()
    question = State()

async def command_start(message : types.Message):
    await Form.start.set()
    await message.answer('Загрузите фотографию 📸', reply_markup = ReplyKeyboardRemove())

async def empty(message : types.Message):
    await Form.start.set()
    await message.answer('Загрузите фотографию 📸')

async def detecting(message: types.Message, state: FSMContext):
    uniq_filename = str(datetime.datetime.now().date()) + '-' + str(datetime.datetime.now().time()).replace(':', '.')
    await message.photo[-1].download(f'./trash/trash-{uniq_filename}.jpg', make_dirs=False)

    os.system(f"python ./yolov5/detect.py --weights ./yolov5/runs/train/exp6/weights/best.pt --source \
    ./trash/trash-{uniq_filename}.jpg \
    --save-txt --name ~/PycharmProjects/project/result --exist-ok --conf-thres 0.5")

    path = f'./result/labels/trash-{uniq_filename}.txt'

    # if exists(path) == True:
    a = names(dict_object, path)
    await message.answer(genre_recommendations(recommend(rec(dict_object, path))))
    d = movie_data(genre_recommendations(recommend(rec(dict_object, path))))
    b = '\n'.join(d[0])
    c = d[1]
    await Form.detection.set()
    await state.update_data(uniq=uniq_filename)
    await message.answer_photo(photo=open(f'./result/trash-{uniq_filename}.jpg', 'rb'), caption = a)
    media = types.MediaGroup()
    for i in range(len(c)):
        media.attach_photo((c[i]), caption = f'Рекомендуемые фильмы для просмотра: \n{b}' if i==0 else '')
    await message.answer_media_group(media=media)
    await message.answer('Хотите помочь стать нашей модели лучше? 😏', reply_markup = choice)
    # else:
    #     await message.answer('На фотографии никто не обнаружен 😞')
    #     media = types.MediaGroup()
    #     for i in range(len(top_5_picture)):
    #         media.attach_photo((top_5_picture[i]), caption=f'Топ-5 фильмов: {top_5}' if i == 0 else '')
    #     await message.answer_media_group(media=media)

async def answer_yes(message : types.Message, state: FSMContext):
    await Form.question.set()
    await message.answer('На фотографии все люди указаны верно?', reply_markup = choice)

async def filter_answer(message: types.Message, state: FSMContext):
    if message.text not in answers:
        await message.answer('Воспользуйся кнопками 💻️', reply_markup = choice)

async def end(message : types.Message, state: FSMContext):
    await message.answer('Спасибо, еще буду учиться 🤓')

async def end_yes(message : types.Message, state: FSMContext):
    data = await state.get_data()
    uniq_filename = data.get('uniq')
    file_source_label = f'./result/labels/trash-{uniq_filename}.txt'
    file_source = f'./trash/trash-{uniq_filename}.jpg'
    file_destination = './match'
    shutil.move(file_source_label, file_destination)
    shutil.move(file_source, file_destination)
    await message.answer(f'Спасибо, еще буду учиться 🤓')

async def set_default_commands():
    await dp.bot.set_my_commands([types.BotCommand("start", "Запустить бота")])

def register_bot_handlers(dp: Dispatcher):
    dp.register_message_handler(command_start, commands = ['start'], state='*')
    dp.register_message_handler(detecting, content_types=['photo'],  state=Form.start)
    dp.register_message_handler(empty, state=Form.start)
    dp.register_message_handler(answer_yes, Text(equals='Да ✅'), state=Form.detection)
    dp.register_message_handler(end, Text(equals='Нет ❌'), state=[Form.detection,Form.question])
    dp.register_message_handler(end_yes, Text(equals='Да ✅'), state=Form.question)
    dp.register_message_handler(filter_answer, state=[Form.detection,Form.question])
    dp.register_message_handler(set_default_commands)


