#by Dzhuzo365
import asyncio, openai
import os, random


from aiogram import types, Router, F, Bot
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import ReplyKeyboardRemove


from mainFile.database.models import Photo, Video
from mainFile.database.orm_query import (
    orm_get_games,
    orm_get_game,

    orm_get_end_new,
    orm_get_previous_new,
    orm_get_next_new, orm_count_news,
)
from mainFile.filters.chat_types import ChatTypes
from mainFile.ChatGPT.gpt import gpt

from mainFile.keyboards.inline import get_callback_btns, get_url_btns
from mainFile.keyboards.reply import get_keyboard
bot=Bot(token=os.getenv('TOKEN'),parse_mode=ParseMode.HTML)

home_kb = get_keyboard(
    'Новости',
    'Игры',
    'Донатик',
    'СХРОН',
    placeholder='я буду тебя ждать...',
    sizes=(2, 1, 1),
)

user_router = Router()
user_router.message.filter(ChatTypes(['private']))
count_list = 0


# @user_router.message(F.photo)
# async def first_cmd(message: types.Message):
#     file_id = message.photo[-1].file_id
#     await message.answer(file_id)

@user_router.message(Command('cmd'))
async def cmd(message: types.Message):
    await message.delete()
    await message.answer('А вот и они☺️🍀', reply_markup=home_kb)

# @user_router.message(F.video)
# async def first_cmd(message: types.Message):
#     file_id = message.video.file_id
#     await message.answer(file_id)

#ЭТО ДОЛЖНО БЫТЬ ANSWER_VIDEO С ОБУЧАЛКО1
@user_router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await message.answer_video(video=os.getenv('start_hello'),caption='Приветик, я Мия🤗 одна из участниц стесняшек,\n'
                         'Давай повеселимся❤️\n'
                         '<tg-spoiler>не знаешь с чего начать? пиши /help</tg-spoiler>',
                         reply_markup = home_kb)
    await state.clear()



#=======================================================================================================================
class Scroll_News(StatesGroup):
    first_nw = State()
    other_nw = State()

# @user_router.message(Command('about'))
@user_router.message(F.text.lower().contains('ново'))
async def about_cmd(message: types.Message, session: AsyncSession):
    count = await orm_count_news(session)
    if count:
        await message.answer('Хм, скучно,  ничего нового, может лучше в <a href="https://t.me/mysweetmiya">логово</a> заглянуть?')
    else:
        for new in await orm_get_end_new(session):
            await message.answer_photo(
                new.image,
                caption=f"<i><strong>{new.title}\
                                </strong></i>\n{new.news}\n{new.food}",reply_markup=get_callback_btns(btns={
                    'На базу':'base',
                    'Дальше':f'attack_{new.id}'
                }
                ))

@user_router.callback_query(F.data.startswith('attack'))
async def atk_nws(callback: types.CallbackQuery, session: AsyncSession):
    news_id = int(callback.data.split('_')[-1])
    news_update = await orm_get_previous_new(session,news_id)
    if news_update:
        await callback.answer()
        title = f"<b>{news_update.title}</b>"
        caption = '\n'.join([title, news_update.news, news_update.food])
        media = types.InputMediaPhoto(media=news_update.image, caption= caption)
        await callback.message.edit_media(media=media, reply_markup=get_callback_btns(btns={
            'Назад':f'homing_{news_update.id}',
            'Дальше': f'attack_{news_update.id}',
            'На базу': 'base',


            }
        ))
    else:
        await callback.answer("а все, конец")
        return



@user_router.callback_query(F.data.startswith('homing'))
async def home_nws(callback: types.CallbackQuery, session: AsyncSession):
    news_id = int(callback.data.split('_')[-1])
    news_update = await orm_get_next_new(session, news_id)
    if news_update == None:
        await callback.answer('Это новейшее')
        return


    if news_update:
        await callback.answer()
        title = f"<b>{news_update.title}</b>"
        caption = '\n'.join([title, news_update.news, news_update.food])
        media = types.InputMediaPhoto(media=news_update.image, caption=caption)
        await callback.message.edit_media(media=media, reply_markup=get_callback_btns(btns={
            'Назад': f'homing_{news_update.id}',
            'Дальше': f'attack_{news_update.id}',
            'На базу': 'base',

        }
        ))




@user_router.callback_query(F.data.startswith('base'))
async def base_nws(callback: types.CallbackQuery, session: AsyncSession):
    await callback.answer()
    media = types.InputMediaVideo(media=os.getenv('news_home'),caption="правильно, нахуй их, на чем теперь залипнем? кста, как тебе?👆😮‍💨")
    await callback.message.edit_media(media=media)
# короче проблема в том что os.getenv  чтото не от отправляет и функция не может фотку поменять
#=======================================================================================================================


class UserGame(StatesGroup):
    START = State()
    preSTART = State()


    text = {
        'UserGame:START':'Есть игрушки и поинтереснее❤️'
    }

    last_message_id = None



@user_router.message(or_f(UserGame.START,UserGame.preSTART), F.text == 'НАЕ..ИГРАЛСЯ')
async def end_game(message: types.Message,  state: FSMContext):
    global last_message_id
    if last_message_id:
        await bot.delete_message(message.chat.id, last_message_id)
        last_message_id = None
    await state.clear()
    await message.answer('Хватит на сегодня игрушек..🥱🤯', reply_markup=home_kb)



# @user_router.message(Command('tired'))
@user_router.message(F.text.lower().contains('игры'))
async def tired_cmd(message: types.Message, session: AsyncSession, state: FSMContext):
    await message.answer('Решил поиграть? Тогда вот👇❤️',reply_markup =ReplyKeyboardRemove())
    play_list = await orm_get_games(session)
    btns = {game.name: f'category_{game.id}' for game in play_list}
    await message.answer_photo(photo=os.getenv('game_home'), caption='<b>Виды ролевых игрушек🥵🔥:</b>',reply_markup=get_callback_btns(btns=btns,
                                                                                sizes=(1,)))
    await state.set_state(UserGame.START)

@user_router.callback_query(UserGame.START)
async def start_game(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    global last_message_id
    await  callback.answer()
    game_id = callback.data.split("_")[-1]
    game = await orm_get_game(session, int(game_id))
    name = f"<b>{game.name}</b>"
    caption = '\n'.join([name, game.description,])
    media = types.InputMediaPhoto(media=game.image, caption=caption)
    await callback.message.edit_media(media=media, reply_markup=get_callback_btns(btns={
                 'Назад':'back',
                 'Играть':'play'
            }))
    last_message = await callback.message.answer('Кстати, еще больше контента у моих <a href="https://t.me/+V4Z9-kpFWpliYzk6">подружек</a>',
                                  reply_markup=get_keyboard('НАЕ..ИГРАЛСЯ'))
    last_message_id = last_message.message_id
    await state.set_state(UserGame.preSTART)




# btns = {food.classification: f'category_{food.id}' for food in food_list}

@user_router.callback_query(UserGame.preSTART,F.data.startswith('play'))
async def restart_game(callback: types.CallbackQuery,):
    await callback.answer()
    global last_message_id
    await bot.delete_message(callback.message.chat.id, last_message_id)
    last_message_id = None
    await callback.message.edit_caption(caption='В РАЗРАБОТКЕ, МОЗГУ НЕ ЕБИ СМОТРИ СХРОН',
                                        reply_markup=get_callback_btns(btns={
                                         'К играм':'list_games',
                                         'выход':'exit'}))



@user_router.callback_query(UserGame.preSTART,F.data.startswith('back'))
async def back_game(callback: types.CallbackQuery,session:AsyncSession,  state: FSMContext) -> None:
    global last_message_id
    await bot.delete_message(callback.message.chat.id, last_message_id)
    last_message_id = None
    current_state = await state.get_state()
    previous = None
    play_list = await orm_get_games(session)
    btns = {game.name: f'category_{game.id}' for game in play_list}
    for step in UserGame.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            media = types.InputMediaPhoto(media=os.getenv('game_home'), caption=f"{UserGame.text[previous.state]}")
            await callback.message.edit_media(media=media,
                                          reply_markup=get_callback_btns(btns=btns,
                                                                                sizes=(1,)))
            return
        previous = step
    await callback.answer()



@user_router.callback_query(UserGame.preSTART,F.data.startswith('list_games'))
async def list_game(callback: types.CallbackQuery,session:AsyncSession,  state: FSMContext):
    await callback.answer()
    play_list = await orm_get_games(session)
    btns = {game.name: f'category_{game.id}' for game in play_list}
    media=types.InputMediaPhoto(media=os.getenv('game_home'), caption='<b>Виды игрушек🥵🔥:</b>', reply_markup=get_keyboard('НАЕ..ИГРАЛСЯ'))
    await callback.message.edit_media(media=media,
                               reply_markup=get_callback_btns(btns=btns,
                                                              sizes=(1,)))
    await state.set_state(UserGame.START)

@user_router.callback_query(UserGame.preSTART,F.data.startswith('exit'))
async def exit_game(callback: types.CallbackQuery,  state: FSMContext):
    await callback.answer()
    media = types.InputMediaVideo(media=os.getenv('afk2'),
                                  caption="правильно, нахуй их, на чем теперь залипнем? кста, как тебе?👆😮‍💨",)
    await callback.message.edit_media(media=media)
    await callback.message.answer('Охх, подзаебалась я маленько, ты как?',reply_markup=home_kb)
    await state.clear()






# @user_router.message(Command('money'))
@user_router.message(or_f(Command('money'),F.text.lower().contains('донат')))
async def money_cmd(message: types.Message):
    await message.answer_photo(photo=os.getenv('donate_art'),
                               caption='Мама, у меня интеллект будет такими темпами🥰',
                               reply_markup=get_url_btns(btns={'ЮMoney': 'https://yoomoney.ru/fundraise/11P0R2TD4I4.240329'}
                                                         ))

class shron(StatesGroup):

    shronpre = State()

    last_class = None






@user_router.callback_query(F.data.startswith('full_pls'))
async def ffull_callback(callback: types.CallbackQuery, session: AsyncSession, ):

    query = (
        select( Video.video, Photo.photo))


    result = await session.execute(query)
    data = result.all()
    await  callback.answer()

    if data:

        random_entry = random.choice(data)
        video, photo = random_entry
        media = [video, photo]
        call = random.choice(media)

        if call == video:
            media = types.InputMediaVideo(media=video, caption="Может что-то еще?", )

            r = await callback.message.bot.edit_message_media(chat_id=callback.message.chat.id,message_id=callback.message.message_id,
            media=media, reply_markup=get_callback_btns(btns={
                'Еще': 'full_pls',

            }))
            shron.last_class = r.message_id
        elif call == photo:
            media = types.InputMediaPhoto(media=photo, caption="Может что-то еще?", )

            r = await callback.message.bot.edit_message_media(chat_id=callback.message.chat.id,message_id=callback.message.message_id,
                                                              media=media,
                                              reply_markup=get_callback_btns(btns={
                                                  'Еще': 'full_pls',

                                              }))
            shron.last_class = r.message_id
    else:
        await callback.message.answer('Блинский, твой запросик не получается выполнить😭\n'
                                      'Похоже никто пока не интресовался этой категорией')




@user_router.message(F.text.lower().contains('схрон'))
async def shron_call(message: types.Message, session: AsyncSession,state: FSMContext):

    query = (
        select(Video.video, Photo.photo))


    result = await session.execute(query)
    data = result.all()

    if data:
        random_entry = random.choice(data)
        video, photo = random_entry
        media = [video,photo]
        call = random.choice(media)


        if call == video:
            r = await message.answer_video(video=video, caption="Может что-то еще?",
                                       reply_markup=get_callback_btns(btns={
                                                  'Еще': 'full_pls',

                                              }))
            shron.last_class = r.message_id
        elif call == photo:
            r = await message.answer_photo(photo=photo, caption="Может что-то еще?",
                                              reply_markup=get_callback_btns(btns={
                                                  'Еще': 'full_pls',

                                              }))
            shron.last_class = r.message_id


    else:
        await message.answer_photo(photo=os.getenv('shron_home'), caption='Походу нет порнухи, открывай пх',
                                   reply_markup=get_url_btns(btns={'PornHub': 'https://t.me/+V4Z9-kpFWpliYzk6'}
                                       ))
    await state.clear()




@user_router.message(Command("help"))
async def admin_help(message: types.Message, ):
    tr = await message.answer('Не знаешь что делать? Хмм, дай подумать..')
    await asyncio.sleep(1.5)
    sr = await message.answer('На самом деле я сама хз')
    await asyncio.sleep(0.7)
    sy = await message.answer('Сходи подрочи хуй знает🙃')
    await asyncio.sleep(0.8)
    ft = await message.answer('Ой бля, я же бот, сорри😵‍💫🤐')
    await asyncio.sleep(0.8)
    await message.bot.delete_message(message.chat.id, tr.message_id)
    await message.bot.delete_message(message.chat.id, sr.message_id)
    await message.bot.delete_message(message.chat.id, sy.message_id)
    await message.bot.delete_message(message.chat.id, ft.message_id)
    await message.answer('Не знаешь что поделать?\nНе проблема, Мия всегда на коротком поводке! \n'
                         'Ты можешь перейти в схрон, там всегда мноого интересного, можешь почитать новости в разделе или поиграть🥰')


@user_router.message(F.text)
async def first_cmd(message: types.Message,):
    await message.answer(f'Хееей, {message.from_user.first_name}, я даже не знаю что ответить 😣')


# @user_router.message(F.text=='чат гпт')
# async def first_cmd(message: types.Message,session:AsyncSession):
#     chat_ids = await orm_get_gpt_chat_ids(session)
#     if str(message.chat.id) not in chat_ids:
#         await orm_add_gpt(session, str(message.chat.id), '', '')
#     await message.answer('Привет, это чат-бот на основе модели gpt 3.5🔥\nПриступим!')

# @user_router.message(F.text)
# async def mes(message: types.Message, session:AsyncSession):
#     await gpt(session,
#     message.text, message.from_user.id, message.message_id)