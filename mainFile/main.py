#by Dzhuzo365

import asyncio
import os


from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

load_dotenv(find_dotenv())
import openai

from mainFile.middlewares.db import DataBaseSession
from mainFile.database.engine import create_db, drop_db, session_maker
from handlers.user_private import user_router
from handlers.user_group import user_group
from handlers.admin_private import admin_router
from common.botcommands import all


bot=Bot(token=os.getenv('TOKEN'),parse_mode=ParseMode.HTML)

dp = Dispatcher()

dp.include_router(admin_router)
dp.include_router(user_router)
dp.include_router(user_group)

bot.my_admins_list = []


async def on_startup(bot):

    # await drop_db()


    await create_db()


async def on_shutdown(bot):
    print('-------------------------!!!!!!!!!МИЕ ПИЗДА, ЕЕ ЕБУТ!!!!!!!-----------------------')




async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await bot.delete_webhook(drop_pending_updates=True)
    # await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(commands=all, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())




asyncio.run(main())