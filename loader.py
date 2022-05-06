from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()
bot = Bot(token='5284288973:AAH2DLdEy1gRtdpIvlMT44GC7P_kdP2xa8A')
dp = Dispatcher(bot, storage=storage)
