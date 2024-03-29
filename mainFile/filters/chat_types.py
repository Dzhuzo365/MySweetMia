#by Dzhuzo365
from aiogram.filters import Filter
from aiogram import types, Bot
from sqlalchemy.ext.asyncio import AsyncSession
from mainFile.database.orm_query import orm_get_admins


class ChatTypes(Filter):
    def __init__(self, chat_types:list[str]) -> None:
        self.chat_types = chat_types

    async def __call__(self, message: types.Message) -> bool:
        return message.chat.type in self.chat_types

# class IsAdmin(Filter):
#     def __init__(self) -> None:
#         pass
#
#     async def __call__(self, message: types.Message, bot: Bot) -> bool:
#         return message.from_user.id in bot.my_admins_list

class IsAdmin(Filter):
    def __init__(self,session: AsyncSession) -> None:
            pass

    async def __call__(self, message: types.Message, session: AsyncSession) -> bool:

        admins_list = await orm_get_admins(session)

        return message.from_user.username in admins_list
