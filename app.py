from aiogram.utils import executor
from loader import dp
from handlers import bot_handlers

bot_handlers.register_bot_handlers(dp)

executor.start_polling(dp, skip_updates=True)