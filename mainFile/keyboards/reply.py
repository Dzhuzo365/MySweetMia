#by Dzhuzo365
import emoji
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, KeyboardButtonPollType
from aiogram.utils.keyboard import ReplyKeyboardBuilder


del_keyboard = ReplyKeyboardRemove()

# keyboard =  ReplyKeyboardMarkup(
#     keyboard=[
#         [
#             KeyboardButton(text = 'Кит старт'),
#             KeyboardButton(text = 'Новости'),
#         ],
#         [
#             KeyboardButton(text = 'Игры'),
#             KeyboardButton(text = 'Донатик'),
#         ],
#         [
#             KeyboardButton(text = 'СХРОН')
#         ]
#     ],
#     resize_keyboard=True,
#     input_field_placeholder='я буду тебя ждать...'
# )
#
# keyboard2 = ReplyKeyboardBuilder()
# keyboard2.add(
# KeyboardButton(text = 'Спаринг'),
#         KeyboardButton(text = 'Поло'),
#         KeyboardButton(text = 'Верховая езда'),
#         KeyboardButton(text = 'Онлайн партнер'),
# )
# keyboard2.adjust(2,1,1)



# keyboard3 = ReplyKeyboardMarkup(
#     keyboard=[
#     [
#         KeyboardButton(text = 'Создать опрос', request_poll=KeyboardButtonPollType()),
#     ],
#     [
#         KeyboardButton(text = 'Отправить номер', request_contact=True),
#         KeyboardButton(text = 'Отправить локацию', request_location=True)
#     ],
# ],
#     resize_keyboard=True
#
# )

def get_keyboard(
        *btns: str,
        placeholder: str = None,
        request_contact: int = None,
        request_location: int = None,
        sizes: tuple[int] = (2,),
):

    keyboard = ReplyKeyboardBuilder()

    for index, text in enumerate(btns, start=0):

        if request_contact and request_contact == index:
            keyboard.add(KeyboardButton(text=text, request_contact=True))

        elif request_location and request_location == index:
            keyboard.add(KeyboardButton(text=text, request_location=True))
        else:
            keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True, input_field_placeholder=placeholder)

























