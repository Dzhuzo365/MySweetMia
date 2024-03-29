#by Dzhuzo365
from aiogram import types, Router, Bot
from string import punctuation
from mainFile.filters.chat_types import  ChatTypes
from aiogram.filters import Command
from mainFile.common.restricted_words import restricted_words

user_group = Router()
user_group.message.filter(ChatTypes(['group', 'supergroup']))



@user_group.message(Command("admin"))
async def get_admins(message: types.Message, bot: Bot):
    chat_id = message.chat.id
    admins_list = await bot.get_chat_administrators(chat_id)
    admins_list = [
        member.user.id
        for member in admins_list
        if member.status == "creator" or member.status == "administrator"
    ]
    bot.my_admins_list = admins_list
    if message.from_user.id in admins_list:
        await message.delete()


def clean_text(text: str):
    return text.translate(str.maketrans('','',punctuation))


@user_group.edited_message()
@user_group.message()
async def restricted_cmd(message: types.Message):
    if restricted_words.intersection(clean_text(message.text.lower()).split()):
        await message.answer(f"{message.from_user.first_name} ,ты че ахуел, чертополох😶‍🌫️?")
        await message.delete()
        # await message.chat.ban(message.from_user.id)
