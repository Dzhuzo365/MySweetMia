#by Dzhuzo365
import asyncio
import os
import random

from aiogram import F, Router, types, Bot
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mainFile.database.models import Photo
from mainFile.database.orm_query import (
    orm_add_news,
    orm_delete_new,
    orm_add_video,
    orm_add_photo,
    orm_get_new,
    orm_update_new, orm_delete_media, orm_get_games, orm_add_game, orm_get_food, orm_create_food, orm_get_one_food,
    orm_update_food, orm_delete_food, orm_add_admin, get_and_send_admins_with_positions,
    orm_delete_admin,
    full_info_admins, orm_get_admins, orm_get_admin, orm_update_admin, orm_get_end_new, orm_get_previous_new,
    orm_get_next_new, orm_get_game, orm_delete_game, orm_update_game, orm_count_news,
)

from mainFile.filters.chat_types import ChatTypes, IsAdmin
from mainFile.keyboards.inline import get_callback_btns
from mainFile.keyboards.reply import get_keyboard
from mainFile.common.botcommands import private



admin_router = Router()
admin_router.message.filter(ChatTypes(["private"]), IsAdmin(AsyncSession))
bot=Bot(token=os.getenv('TOKEN'),parse_mode=ParseMode.HTML)


ADMIN_KB = get_keyboard(
    "ADD NW",
    "MEDIA ADD",
    "NEWS",
    "GAMES",
    'FOOD',
    'BACK',
    placeholder="какую письку выложим?",
    sizes=(2, 3, 1),
)

home_kb = get_keyboard(
    'Новости',
    'Игры',
    'Донатик',
    'СХРОН',
    placeholder='я буду тебя ждать...',
    sizes=(2, 1, 1),
)

#////////////////////////////////////////////////////////////////\\\\\\\\ADD_ADMINS////////\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


class AddAdmin(StatesGroup):

    admin_del = State()
    admin_ch = State()
    ch_name = State()
    ch_cls = State()
    create = State()
    status = State()
    value = State()

    ch_ch = False

    admins_change = None
    last_messege = None




@admin_router.callback_query(F.data.startswith("nt_create"))
async def admin_nah(callback: types.CallbackQuery, session: AsyncSession,state: FSMContext):
    await callback.answer()
    query = select(Photo.photo)
    result = await session.execute(query)
    data = result.all()
    random_entry = random.choice(data)
    await callback.message.edit_text("Прошу прощения за неудобства...😞")
    await callback.message.answer_photo(photo=random_entry.photo,
                                        caption='в знак извинения, примите скромный дар...',
                                        reply_markup=ADMIN_KB)
    await state.clear()




@admin_router.callback_query(F.data.startswith("adm_list"))
async def admin_lst(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext ):
    await state.clear()
    admins_text = await get_and_send_admins_with_positions(session)
    await callback.message.edit_text(f'<i><b>Сколько папочек❤️😍</b></i>\n<tg-spoiler>{admins_text}</tg-spoiler>',
                         reply_markup=get_callback_btns(btns={
                                            'подправить': 'ch_adm',
                                            'раскулачить': 'ch_del'
                                        }))

@admin_router.message(Command("adm_list"))
async def admin_lst(message: types.Message, session: AsyncSession, state: FSMContext):
    await state.clear()
    admins_text = await get_and_send_admins_with_positions(session)
    await message.answer(f'<i><b>Сколько папочек❤️😍</b></i>\n<tg-spoiler>{admins_text}</tg-spoiler>',
                         reply_markup=get_callback_btns(btns={
                                            'подправить': 'ch_adm',
                                            'раскулачить': 'ch_del'
                                        }))


@admin_router.callback_query(F.data.startswith("ch_adm"))
async def ch_admin(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    adm_list = await full_info_admins(session)
    btns = {admin.name: f'admin_{admin.id}' for admin in adm_list}
    await callback.message.edit_text('Кого вы решили подправить?',
                                  reply_markup=get_callback_btns(btns=btns,sizes=(1,)))
    await state.set_state(AddAdmin.admin_ch)



@admin_router.callback_query(AddAdmin.admin_ch)
async def admin_change(callback: types.CallbackQuery,session: AsyncSession,state: FSMContext):
    admin_id = callback.data.split("_")[-1]
    AddAdmin.admins_change = await orm_get_admin(session, int(admin_id))
    await callback.message.edit_text('Что хотите изменить?',
                         reply_markup=get_callback_btns(btns={
                             'Имя': 'sname',
                             'Должность': 'cls',
                             'откат': 'nt_create',
                         }))
    await state.update_data(name=AddAdmin.admins_change.name)
    await state.update_data(cls=AddAdmin.admins_change.cls)
    await state.set_state(AddAdmin.value)

@admin_router.callback_query(AddAdmin.value,F.data.startswith("sname"))
async def ch_admin_name(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Как звать то?', reply_markup=get_callback_btns(btns={'откат': 'nt_create'}))
    await state.set_state(AddAdmin.ch_name)
    AddAdmin.last_messege = callback.message.message_id

@admin_router.message(AddAdmin.ch_name, F.text)
async def admin_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.bot.edit_message_text(chat_id = message.chat.id, message_id=AddAdmin.last_messege ,text='Что на счет должности?',reply_markup=
                                                        get_callback_btns(btns={
                                                            'оставь':'save_cls',
                                                            'изменить':'cls'
                                                        }))
    await  message.delete()
    AddAdmin.ch_ch = True
    await state.set_state(AddAdmin.value)

@admin_router.callback_query(AddAdmin.value,F.data.startswith("cls"))
async def ch_admin_name(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Ну и что он из себя представляет?', reply_markup=get_callback_btns(btns={'откат': 'nt_create'}))
    await state.set_state(AddAdmin.ch_cls)
    await state.set_state(AddAdmin.ch_cls)
    AddAdmin.last_messege = callback.message.message_id

@admin_router.message(AddAdmin.ch_cls, F.text)
async def admin_name(message: types.Message, state: FSMContext):
    await state.update_data(cls=message.text)
    await message.bot.edit_message_text(chat_id = message.chat.id,message_id=AddAdmin.last_messege,text='Что на счет имени?',reply_markup=
                                                        get_callback_btns(btns={
                                                            'оставь':'save_name',
                                                            'изменить':'sname'
                                                        }))
    await message.delete()
    AddAdmin.ch_ch = True
    await state.set_state(AddAdmin.value)

@admin_router.callback_query(AddAdmin.value,or_f(F.data.startswith("save_cls"),
                                                    F.data.startswith("save_name")))
async def admin_donwlpads(callback: types.CallbackQuery, session:AsyncSession ,state: FSMContext):
    data = await state.get_data()
    if AddAdmin.ch_ch == False:
        await callback.answer()
        await callback.message.edit_text('Да все и так пиздатенько',)
    else:
        await orm_update_admin(session, AddAdmin.admins_change.id, data)
        await callback.answer('✨повезло долбоебу✨')
        await callback.message.edit_text('да, не легкая это работка',)
        await callback.message.answer('✞ Дарую вам права моего отцаⓇ',reply_markup= ADMIN_KB)
        AddAdmin.ch_ch = False

    await  state.clear()



@admin_router.callback_query(F.data.startswith("ch_del"))
async def delete_ad(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    await callback.answer()
    adm_list = await full_info_admins(session)
    btns = {admin.name: f'admin_{admin.id}' for admin in adm_list}
    await callback.message.edit_text('Кто проявил неуважение?',
                                     reply_markup=get_callback_btns(btns=btns,sizes=(1,)
                                        ))
    await state.set_state(AddAdmin.admin_del)


@admin_router.callback_query(AddAdmin.admin_del)
async def adm_bye(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    adm_id = callback.data.split("_")[-1]
    await orm_delete_admin(session, int(adm_id))
    await callback.answer('а ну-ка нахуй отсюда.')
    await callback.message.edit_text('Он нас предал...',
                                     reply_markup=get_callback_btns(btns={
                                         "к списку":'adm_list',
                                         'хом':'home_adm',
                                     }
                                                                    ,)
                                        )
    await  state.clear()


@admin_router.callback_query(F.data.startswith("home_adm"))
async def adm_bye(callback: types.CallbackQuery,):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.edit_text('Сохраняем инфу...')
    await asyncio.sleep(0.7)
    await callback.message.edit_text('Предохраняемся...')
    await asyncio.sleep(0.4)
    await callback.message.edit_text('Готово')
    await asyncio.sleep(0.4)
    await callback.message.delete()
    await callback.message.answer('✨Вот мы и дома🎔',reply_markup=ADMIN_KB)



@admin_router.message(Command("create"))
async def admin_create(message: types.Message, state: FSMContext):
    sent_message = await message.answer("Ух-ты, у нас новая важная персона? Как ее зовут?",
                                        reply_markup=get_callback_btns(btns={
                                            'не нахуй': 'nt_create'
                                        }))
    await state.set_state(AddAdmin.create)

    await state.update_data(sent_message_id=sent_message.message_id)


@admin_router.message(AddAdmin.create, F.text)
async def admin_names(message: types.Message, session:AsyncSession ,state: FSMContext):
    admins_list = await orm_get_admins(session)
    if message.text in admins_list:
        await message.answer('Кажись он уже кому-то нализал, он в админах')
    else:
     await state.update_data(name=message.text)
     await message.delete()
     data = await state.get_data()
     sent_message_id = data.get('sent_message_id')

     await message.bot.edit_message_text(chat_id=message.chat.id, message_id=sent_message_id,
                                             text="Ага, а кто он сам по себе?", reply_markup=get_callback_btns(btns={
                                             'не нахуй': 'nt_create'
                                         }))

     await state.update_data(sent_message_id=sent_message_id)

     await state.set_state(AddAdmin.status)


@admin_router.message(AddAdmin.status, F.text)
async def admin_status(message: types.Message, session: AsyncSession, state: FSMContext):
    await message.delete()
    await state.update_data(cls=message.text)
    data = await state.get_data()
    sent_message_id = data.get('sent_message_id')
    try:
        await orm_add_admin(session, data)
        await message.bot.edit_message_text(chat_id=message.chat.id, message_id=sent_message_id,
                                            text="Ну, я добавила, но все равно предпочла бы только вас.")
        await state.clear()

    except Exception as e:
        await message.bot.edit_message_text(chat_id=message.chat.id, message_id=sent_message_id,text=
            f"Ошибочка вышла😩: \n{str(e)}\nСаня пидарас, опять хуевертит🤬",

        )
        await state.clear()


#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


class AddNews(StatesGroup):

    name = State()
    description = State()
    image = State()
    food = State()

    message_id = None

    texts = {
        'AddNews:name': 'Блиин, а мне так прошлое название понравилось...',
        'AddNews:description': 'Вот это да, вы можете и лучше написать,круто😳',
        'AddNews:image': 'Интересные картинки🤐',
        'AddNews:food': 'Ебанем хештег?',
    }


@admin_router.message(Command("admin"))
async def admin_features(message: types.Message, session: AsyncSession):
    await message.answer("Что хотите сделать господин🥰?\n Если вы у нас впервые напишите /help", reply_markup=ADMIN_KB)
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeChat(chat_id=1723636175))
    await message.delete()

@admin_router.message(Command("help"))
async def admin_help(message: types.Message, ):
    await message.delete()
    await message.answer("Вот список дополнительных комманд:\n"
                         "/admin     ➟ я буду в вашей власти..\n"
                         "/adm_list ➟ список папиков❦\n"
                         "/create     ➟ добавить папика☬")

@admin_router.message(F.text=="BACK")
async def admin_f(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Я соскучилась, давайте пообщаемся🥰?", reply_markup=home_kb)



# ======
class Scroll_adm_nw(StatesGroup):
    first_nw = State()
    other_nw = State()
    scroll = State()


    last_news = None
    last_chat = None


@admin_router.message(F.text == 'NEWS')
async def about_cmd(message: types.Message, session: AsyncSession, state: FSMContext):
    count = await orm_count_news(session)
    if count:
        await message.answer('нет нихуяшеньки')
    else:
        for new in await orm_get_end_new(session):
            LTS = await message.answer_photo(
                new.image,
                caption=f"<i><strong>{new.title}\
                                </strong></i>\n{new.news}\n{new.food}",reply_markup=get_callback_btns(btns={
                    'На базу': 'base',
                    'Дальше': f'attack_{new.id}',
                    "Удалить": f"delete_{new.id}",
                    "Изменить": f"change_{new.id}",

                }, sizes=(2,)
                ))
        Scroll_adm_nw.last_news = LTS.message_id
        await  state.set_state(Scroll_adm_nw.scroll)

@admin_router.callback_query(StateFilter(Scroll_adm_nw.scroll),F.data.startswith('attack'))
async def atk_nws(callback: types.CallbackQuery, session: AsyncSession, ):

    news_id = int(callback.data.split('_')[-1])
    news_update = await orm_get_previous_new(session,news_id)
    if news_update:
        await callback.answer()
        title = f"<b>{news_update.title}</b>"
        caption = '\n'.join([title, news_update.news, news_update.food])
        media = types.InputMediaPhoto(media=news_update.image, caption= caption)
        LTS = await callback.message.edit_media(media=media, reply_markup=get_callback_btns(btns={
            'Назад':f'homing_{news_update.id}',
            'Дальше': f'attack_{news_update.id}',
            "Удалить": f"delete_{news_update.id}",
            "Изменить": f"change_{news_update.id}",
            'На базу': 'base',


            }
        ))
    else:
        await callback.answer("а все, конец")
        return

    Scroll_adm_nw.last_news = LTS.message_id



@admin_router.callback_query(StateFilter(Scroll_adm_nw.scroll),F.data.startswith('homing'))
async def home_nws(callback: types.CallbackQuery, session: AsyncSession, ):
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
        LTS = await callback.message.edit_media(media=media, reply_markup=get_callback_btns(btns={
            'Назад': f'homing_{news_update.id}',
            'Дальше': f'attack_{news_update.id}',
            "Удалить": f"delete_{news_update.id}",
            "Изменить": f"change_{news_update.id}",
            'На базу': 'base',

        }
        ))
        Scroll_adm_nw.last_news = LTS.message_id




@admin_router.callback_query(StateFilter(Scroll_adm_nw.scroll),F.data.startswith('base'))
async def base_nws(callback: types.CallbackQuery,state: FSMContext ):
    await callback.answer()
    media = types.InputMediaVideo(media=os.getenv('news_home'),caption="правильно, нахуй их, на чем теперь залипнем? кста, смотришь аниме?👆😮‍💨")
    await callback.message.edit_media(media=media)
    await state.clear()

# ========


@admin_router.callback_query(StateFilter(Scroll_adm_nw.scroll),F.data.startswith("delete_"))
async def delete_new(callback: types.CallbackQuery, session: AsyncSession, ):
    new_id = callback.data.split("_")[-1]
    await orm_delete_new(session, int(new_id))
    await callback.answer('а ну-ка нахуй отсюда.')
    await callback.message.bot.edit_message_caption(chat_id=callback.message.chat.id,message_id=Scroll_adm_nw.last_news
                                                    ,caption='НОВОСТЬ УДАЛЕНА',reply_markup=get_callback_btns(btns={
            'Назад':f'homing_{new_id}',
            'Дальше': f'attack_{new_id}',
            "Удалить": f"delete_{new_id}",
            "Изменить": f"change_{new_id}",
            'На базу': 'base',


            }
        ))



# Становимся в состояние ожидания ввода name
@admin_router.message(F.text == "ADD NW")
async def add_news(message: types.Message, state: FSMContext):
    spent_name = await message.answer(
        "Как вы назовёте новость?",
    )
    await state.set_state(AddNews.name)
    Scroll_adm_nw.last_news = spent_name.message_id


# Хендлер отмены и сброса состояния должен быть всегда именно хдесь,
# после того как только встали в состояние номер 1 (элементарная очередность фильтров)
@admin_router.message(StateFilter('*'), Command("хуйня"))
@admin_router.message(StateFilter('*'), F.text.casefold() == "хуйня")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer("Прошу прощения за неудобства...😞", reply_markup=ADMIN_KB)


# Вернутся на шаг назад (на прошлое состояние)

@admin_router.message(StateFilter(AddNews), F.text.casefold() == "назад")
async def back_step_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state == AddNews.name:
        await message.answer('Хозяин... Пути назад нет, давайте доведем дело до конца😖?')
        return

    previous = None
    for step in AddNews.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(f"Охх, тяжело, вернемся назад?\n{AddNews.texts[previous.state]}")
            return
        previous = step


# Ловим данные для состояние name и потом меняем состояние на description
@admin_router.message(AddNews.name, F.text)
async def add_name(message: types.Message,state: FSMContext):

    if len(message.text) >= 100:
        await message.answer(
                "Слушай, что-то большевато вышло, в меня не влезет... \n Может, чуть поменьше?🥺"
            )

        return


    await state.update_data(name=message.text)
    spent_desc = await message.bot.edit_message_text(chat_id=message.chat.id,message_id=Scroll_adm_nw.last_news,text=
                                        f"Что же вы нам поведаете, мистер {message.from_user.first_name}?")
    Scroll_adm_nw.last_news = spent_desc.message_id
    await message.delete()

    await state.set_state(AddNews.description)


# Хендлер для отлова некорректных вводов для состояния name
@admin_router.message(AddNews.name)
async def add_name2(message: types.Message, ):
    fake_nw =await message.bot.edit_message_text(chat_id=message.chat.id,message_id=Scroll_adm_nw.last_news,
                                        text="Вау, это для меня🫢? Но как же вы назовете новость?")
    await message.delete()
    Scroll_adm_nw.last_news = fake_nw.message_id


# Ловим данные для состояние description и потом меняем состояние на price
@admin_router.message(AddNews.description, F.text)
async def add_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    spent_hash = await message.bot.edit_message_text(chat_id=message.chat.id,message_id=Scroll_adm_nw.last_news,
                                        text="Давай поставим #  для лучшего нахождения?")
    await message.delete()
    Scroll_adm_nw.last_news = spent_hash.message_id
    await state.set_state(AddNews.food)

@admin_router.message(AddNews.food, F.text)
async def add_food(message: types.Message, state: FSMContext):
    txt = message.text
    if '#' in txt:
        await state.update_data(food=message.text)
    else:
        await state.update_data(food='#'+message.text)
    spent_image = await message.bot.edit_message_text(chat_id=message.chat.id,message_id=Scroll_adm_nw.last_news,
                                        text="Будут ли какие нибудь иллюстрации?")
    Scroll_adm_nw.last_news = spent_image.message_id
    await message.delete()
    await state.set_state(AddNews.image)

@admin_router.message(AddNews.food)
async def add_food2(message: types.Message, ):
    fake_fod =await message.bot.edit_message_text(chat_id=message.chat.id,message_id=Scroll_adm_nw.last_news,
                                        text="А теперь ебани хештег прям на меня😘")
    await message.delete()
    Scroll_adm_nw.last_news = fake_fod.message_id

# Хендлер для отлова некорректных вводов для состояния description
@admin_router.message(AddNews.description)
async def add_description2(message: types.Message, ):
    fake_desc =await message.bot.edit_message_text(chat_id=message.chat.id,message_id=Scroll_adm_nw.last_news,
                                        text="Вау, это для меня🫢? Но как же вы назовете новость?")
    await message.delete()
    Scroll_adm_nw.last_news = fake_desc.message_id

# Ловим данные для состояние image и потом выходим из состояний
@admin_router.message(AddNews.image,F.photo)
async def add_image(message: types.Message, state: FSMContext, session: AsyncSession):

    await state.update_data(image=message.photo[-1].file_id)

    data = await state.get_data()
    try:
        await orm_add_news(session, data)
        forms = await message.bot.edit_message_text(chat_id=message.chat.id, message_id=Scroll_adm_nw.last_news,
                                                    text="оформите меня вечером, мастер⚤ 💘")
        Scroll_adm_nw.last_news = forms.message_id
        await message.delete()
        await asyncio.sleep(0.9)
        await message.bot.delete_message(message.chat.id, Scroll_adm_nw.last_news)
        await message.answer('кхм. Ура! Теперь люди будут посвещены!', reply_markup=ADMIN_KB)

        await state.clear()

    except Exception as e:
        firms = await message.bot.edit_message_text(chat_id=message.chat.id, message_id=Scroll_adm_nw.last_news,
                                                    text=
                                                    f"Ошибочка вышла😩: \n{str(e)}\n💘оформишь меня , в перерыве?💘",

                                                    )
        Scroll_adm_nw.last_news = firms.message_id
        await message.delete()
        await asyncio.sleep(0.9)
        await message.bot.delete_message(message.chat.id, Scroll_adm_nw.last_news)
        await message.answer('кхм. Ну ничего, скоро все починят, наверное..', reply_markup=ADMIN_KB)

        await state.clear()
    AddNews.new_for_change = None
    Scroll_adm_nw.last_news = None



@admin_router.message(AddNews.image, F.text.lower().contains('не'))
async def add_image2(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(image=os.getenv('new_miu'))
    data = await state.get_data()
    try:
        await orm_add_news(session, data)
        forms = await message.bot.edit_message_text(chat_id=message.chat.id, message_id=Scroll_adm_nw.last_news,
                                            text="оформите меня вечером, мастер⚤ 💘")
        Scroll_adm_nw.last_news = forms.message_id
        await message.delete()
        await asyncio.sleep(0.9)
        await message.bot.delete_message(message.chat.id, Scroll_adm_nw.last_news)
        await message.answer('кхм. Ура! Теперь люди будут посвещены!', reply_markup=ADMIN_KB)

        await state.clear()

    except Exception as e:
        firms = await message.bot.edit_message_text(chat_id=message.chat.id, message_id=Scroll_adm_nw.last_news,
                                            text=
                                            f"Ошибочка вышла😩: \n{str(e)}\n💘оформишь меня , в перерыве?💘",

                                            )
        Scroll_adm_nw.last_news = firms.message_id
        await message.delete()
        await asyncio.sleep(0.9)
        await message.bot.delete_message(message.chat.id, Scroll_adm_nw.last_news)
        await message.answer('кхм. Ну ничего, скоро все починят, наверное..', reply_markup=ADMIN_KB)

        await state.clear()
    AddNews.new_for_change = None
    Scroll_adm_nw.last_news = None


@admin_router.message(AddNews.image)
async def add_image3(message: types.Message, ):
    fake_img =await message.bot.edit_message_text(chat_id=message.chat.id,message_id=Scroll_adm_nw.last_news,
                                        text="Блин, что-то не получается, можете снова отправить фотку?")
    await message.delete()
    Scroll_adm_nw.last_news = fake_img.message_id

# ======================================================================================================================
# ==============================================___CHANGE CLASS___======================================================

change_kb = get_callback_btns(
    btns={
        'Название': 'ch_name',
        'Новость': 'ch_description',
        'Фото': 'ch_image',
        'Хештег': 'ch_food',
        'На главную': 'home',
    },
    sizes=(3,1,1)
)


class Change(StatesGroup):
    change = State()
    name = State()
    description = State()
    image = State()
    food = State()

    new_for_change = None
    ch_ch = False
    hey_party = None
    hellcat = None




@admin_router.callback_query(StateFilter(Scroll_adm_nw.scroll), F.data.startswith("change_"))
async def change_news_callback(
        callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    news_id = callback.data.split("_")[-1]
    new_for_change = await orm_get_new(session, int(news_id))
    Change.new_for_change = new_for_change
    await callback.answer()
    srt = await callback.message.answer(
        "Я что, ошиблась в новости😰?Прошу простите😭\nСкажите что не так, я тут же исправлю..",
        reply_markup=change_kb,
    )
    await state.update_data(name=Change.new_for_change.title)
    await state.update_data(description=Change.new_for_change.news)
    await state.update_data(image=Change.new_for_change.image)
    await state.update_data(food=Change.new_for_change.food)

    await state.set_state(Change.change)
    Change.hellcat = srt.message_id


@admin_router.callback_query(Change.change, F.data.startswith("ch_name"))
async def callback_name(callback: types.CallbackQuery, state: FSMContext ):
    await callback.answer()
    art = await callback.message.answer('Какое название вас устроит?',
                                  )
    await state.set_state(Change.name)
    Change.hey_party = art.message_id


@admin_router.message(Change.name, F.text)
async def update_name(message: types.Message,state: FSMContext, ):
    await state.update_data(name=message.text)
    await message.delete()
    await message.bot.delete_message(message.chat.id,Change.hey_party)
    srt = await message.bot.edit_message_text(chat_id=message.chat.id,message_id=Change.hellcat,
                                        text='Хотите еще что-то изменить?',
                                  reply_markup=change_kb)
    Change.ch_ch = True
    await state.set_state(Change.change)
    Change.hellcat = srt.message_id


@admin_router.callback_query(Change.change, F.data.startswith("ch_description"))
async def callback_destriction(callback: types.CallbackQuery, state: FSMContext,):
    await callback.answer()
    art = await callback.message.answer('Ты хочешь переписать новость? А мне понравилось..',
                                  )
    await state.set_state(Change.description)
    Change.hey_party = art.message_id

@admin_router.message(Change.description, F.text)
async def update_destriction(message: types.Message, state: FSMContext,):
    await message.delete()
    await message.bot.delete_message(message.chat.id, Change.hey_party)
    await state.update_data(description=message.text)
    # srt = await message.bot.edit_message_text(chat_id=message.chat.id, message_id=Change.hellcat,
    #                                     text='Хотите еще что-то изменить?',
    #                               reply_markup=change_kb)
    Change.ch_ch = True
    await state.set_state(Change.change)
    # Change.hellcat = srt.message_id


@admin_router.callback_query(Change.change, F.data.startswith("ch_food"))
async def callback_food(callback: types.CallbackQuery, state: FSMContext, ):
    await callback.answer()
    art = await callback.message.answer(f'Епт, хештег, ну ты чего?❤️',
                                  )
    await state.set_state(Change.food)
    Change.hey_party = art.message_id

@admin_router.message(Change.food, F.text)
async def update_food(message: types.Message, state: FSMContext,):
    txt = message.text
    await message.bot.delete_message(message.chat.id, Change.hey_party)
    await message.delete()
    if '#' in txt:
        await state.update_data(food=message.text)
    else:
        await state.update_data(food='#'+message.text)
    # srt = await message.bot.edit_message_text(chat_id=message.chat.id, message_id=Change.hellcat,
    #                                           text='Хотите еще что-то изменить?',
    #                               reply_markup=change_kb)
    Change.ch_ch = True
    await state.set_state(Change.change)
    # Change.hellcat = srt.message_id



@admin_router.callback_query(Change.change, F.data.startswith("ch_image"))
async def callback_image(callback: types.CallbackQuery, state: FSMContext, ):
    await callback.answer()
    srt = await callback.message.answer(f'Можно я буду на фотке? Ну пожалуйста❤️',
                                  )
    await state.set_state(Change.image)
    Change.hey_party = srt.message_id

@admin_router.message(Change.image, F.photo)
async def update_image(message: types.Message, state: FSMContext,):
    await message.delete()
    await message.bot.delete_message(message.chat.id, Change.hey_party)
    await state.update_data(image=message.photo[-1].file_id)
    # srt = await message.bot.edit_message_text(chat_id=message.chat.id, message_id=Change.hellcat,
    #                                           text='Хотите еще что-то изменить?',
    #                               reply_markup=change_kb)
    Change.ch_ch = True
    await state.set_state(Change.change)
    # Change.hellcat = srt.message_id

@admin_router.callback_query(Change.change, F.data.startswith("home"))
async def callback_image(callback: types.CallbackQuery, state: FSMContext,  session: AsyncSession):
    data = await state.get_data()
    if Change.ch_ch == False:
        await callback.answer()
        await callback.message.bot.delete_message(chat_id=callback.message.chat.id,
                                                  message_id=callback.message.message_id)
        await callback.message.answer('Да все и так пиздатенько', reply_markup=ADMIN_KB)
    else:
        await callback.answer('✨стало пизже✨')
        await callback.message.bot.delete_message(chat_id=callback.message.chat.id,
                                                  message_id=callback.message.message_id)
        await orm_update_new(session, Change.new_for_change.id, data)
        await callback.message.answer('да, не легкая это работка', reply_markup=ADMIN_KB)
        Change.ch_ch = False

    await  state.clear()






#=======================================================================================================================
#====================================__MEDIA CLASS__====================================================================


class AddMedia(StatesGroup):
    media = State()

    media_for_change = None
    more = False




@admin_router.message(AddMedia.media,Command('delete'))
async def delete_media(session: AsyncSession):
    await orm_delete_media(session)



@admin_router.message(StateFilter('*'), Command("хуйня"))
@admin_router.message(StateFilter('*'), F.text.casefold() == "хуйня")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.bot.delete_message(chat_id=message.chat.id,message_id=AddMedia.media_for_change)
    await message.answer("Прошу прощения за неудобства...😞", reply_markup=ADMIN_KB)


@admin_router.message(F.text == "MEDIA ADD")
async def donwload_media(message: types.Message, state: FSMContext):
    await message.delete()
    r = await message.answer("Ебать, контент? Если передумали, пишите 'хуйня'\nИли можно удалить все к хуям /delete",)
    await state.set_state(AddMedia.media)
    AddMedia.media_for_change = r.message_id


@admin_router.callback_query(AddMedia.media, F.data.startswith('home_md'))
async def home_media_clb(callback: types.CallbackQuery, state:FSMContext):
    await state.clear()
    r = await callback.message.bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                                 text='ща сек, сохраню инфу')
    await asyncio.sleep(0.8)
    await callback.message.bot.delete_message(chat_id=callback.message.chat.id, message_id=r.message_id)
    await callback.message.answer('мы дома', reply_markup=ADMIN_KB)



@admin_router.message(or_f(F.photo, F.video), StateFilter(AddMedia.media))
async def add_media(message: types.Message,session:AsyncSession, state: FSMContext):
    if message.photo:
        await state.update_data(photo=message.photo[-1].file_id)
        data = await state.get_data()
        try:
            await orm_add_photo(session, data)
            await message.delete()
            if AddMedia.more == False:
                r = await message.bot.edit_message_text(chat_id=message.chat.id,message_id=AddMedia.media_for_change,
                                                        text="Вау, увидеть бы ее в живую🥺",
                                                      reply_markup=get_callback_btns(
                                                         btns={
                                                             'домой':'home_md',
                                                           }
                 ))
                AddMedia.media_for_change = r.message_id
                AddMedia.more = True
        except Exception as e:
            r = await message.bot.edit_message_text(chat_id=message.chat.id, message_id=AddMedia.media_for_change,
                                                  text=
                f"Ошибочка вышла😩: \n{str(e)}\nСаня пидарас, опять хуевертит🤬",

            )
            AddMedia.media_for_change = r.message_id
            await state.clear()

    if message.video:
        await state.update_data(video=message.video.file_id)
        data = await state.get_data()
        await message.delete()
        try:
            await orm_add_video(session, data)
            if AddMedia.more == False:
                r = await message.bot.edit_message_text(chat_id=message.chat.id, message_id=AddMedia.media_for_change,
                                                      text="Вау, увидеть бы ее в живую🥺",reply_markup=get_callback_btns(
                                                         btns={
                                                              'домой':'home_md',
                                                            }
                    ))
                AddMedia.media_for_change = r.message_id
                AddMedia.more = True

        except Exception as e:
            r = await message.bot.edit_message_text(chat_id=message.chat.id, message_id=AddMedia.media_for_change,
                                                    text=
                f"Ошибочка вышла😩: \n{str(e)}\nСаня пидарас, опять хуевертит🤬",

                )
            AddMedia.media_for_change = r.message_id
            await state.clear()
    if message.video_note:
        await message.answer('хуй')


#=========================================------____GAMES_CLASS____-------==============================================


class GameDev(StatesGroup):
    start = State()
    development = State()
    preSTART = State()
    name = State()
    description = State()
    image = State()
    food_id = State()

    texts = {
        'GameDev:name': 'Ну что поделать вернемся к названию.',
        'GameDev:description': 'Предется заново переписывать...',
        'GameDev:development': 'Есть игрушки и поинтереснее❤️',
    }


    last_game_id = None
    last_game_id2 = None

@admin_router.message(F.text == 'GAMES')
async def admin_palying(message: types.Message, session: AsyncSession, state: FSMContext):
    play_list = await orm_get_games(session)
    btns = {game.name : f'category_{game.id}' for game in play_list}
    list_game = await message.answer_photo(photo=os.getenv('game_home'),caption="Вы решили поиграть?)", reply_markup=get_callback_btns(btns=btns,
                                                                                sizes=(1,)))
    await asyncio.sleep(0.4)
    game_make = await message.answer("Или может что-то новенькое?",reply_markup=get_keyboard('СОЗДАТЬ'))
    await  state.set_state(GameDev.development)
    GameDev.last_game_id = game_make.message_id
    GameDev.last_game_id2 = list_game.message_id

#=================================================

# @admin_router.message(or_f(GameDev.START,GameDev.preSTART), F.text == 'НАЕ..ИГРАЛСЯ')
# async def end_game(message: types.Message,  state: FSMContext):
#     global last_message_id
#     if last_message_id:
#         await bot.delete_message(message.chat.id, last_message_id)
#         last_message_id = None
#     await state.clear()
#     await message.answer('Хватит на сегодня игрушек..🥱🤯', reply_markup=home_kb)


@admin_router.callback_query(GameDev.development)
async def start_game(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    await  callback.answer()
    game_id = callback.data.split("_")[-1]
    game = await orm_get_game(session, int(game_id))
    name = f"<b>{game.name}</b>"
    caption = '\n'.join([name, game.description,])
    await callback.message.bot.delete_message(callback.message.chat.id, GameDev.last_game_id)
    media = types.InputMediaPhoto(media=game.image, caption=caption)
    last_message = await callback.message.bot.edit_message_media(chat_id=callback.message.chat.id, message_id=GameDev.last_game_id2
                                                                 ,media=media, )
    last_messagee = await callback.message.bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=last_message.message_id,
                                                         reply_markup=get_callback_btns(btns={
                 'Назад':'back',
                 'Удалить':f'del_{game_id}',
                 'Изменить':f'change_{game_id}'
            }, sizes=(1,2,)))

    GameDev.last_game_id = last_messagee.message_id
    await state.set_state(GameDev.preSTART)




# btns = {food.classification: f'category_{food.id}' for food in food_list}

@admin_router.callback_query(GameDev.preSTART,F.data.startswith('del_'))
async def restart_game(callback: types.CallbackQuery,session: AsyncSession, state: FSMContext):
    await callback.answer('🧹Мусор убран🗑')
    game_id = callback.data.split("_")[-1]
    await orm_delete_game(session, int(game_id))
    play_list = await orm_get_games(session)
    btns = {game.name: f'category_{game.id}' for game in play_list}
    media = types.InputMediaPhoto(media=os.getenv('game_home'), caption="Вы решили поиграть?)")
    list_game = await callback.message.bot.edit_message_media(chat_id=callback.message.chat.id,message_id=GameDev.last_game_id,
                                                              media=media,
                                           reply_markup=get_callback_btns(btns=btns,
                                                                          sizes=(1,)))
    await asyncio.sleep(0.7)
    game_make = await callback.message.answer("Или может что-то новенькое?", reply_markup=get_keyboard('СОЗДАТЬ'))
    await  state.set_state(GameDev.development)
    GameDev.last_game_id = game_make.message_id
    GameDev.last_game_id2 = list_game.message_id

#=======================================================================================================================
#========================================= ИЗМЕНЕНИЯ В ИГРАХ!!!!========================================================

game_kb = get_callback_btns(
    btns={
        'Название': 'ch_name',
        'Описание': 'ch_description',
        'Фото': 'ch_image',
        'Принадлежность': 'ch_food',
        'На главную': 'home',
    },
    sizes=(3,1,1)
)


class game_repair(StatesGroup):
    change = State()
    name = State()
    description = State()
    image = State()
    food = State()

    game_for_change = None
    ch_ch = False
    last_game_id = None
    media = types.InputMediaPhoto(media=os.getenv('repair_game'), caption="Мия чинила на связи босс📲 Что починить?", )





@admin_router.callback_query(GameDev.preSTART,F.data.startswith('change'))
async def change_game(callback: types.CallbackQuery,session: AsyncSession, state: FSMContext):
    game_id = callback.data.split("_")[-1]
    game_for_change = await orm_get_game(session, int(game_id))
    game_repair.game_for_change = game_for_change
    await callback.answer()
    await callback.message.bot.edit_message_media(chat_id=callback.message.chat.id,message_id=callback.message.message_id,
                                                  media=game_repair.media,reply_markup=game_kb,
    )
    await state.update_data(name=game_repair.game_for_change.name)
    await state.update_data(description=game_repair.game_for_change.description)
    await state.update_data(image=game_repair.game_for_change.image)
    await state.update_data(food=game_repair.game_for_change.food_id)


    await state.set_state(game_repair.change)


@admin_router.callback_query(game_repair.change, F.data.startswith("ch_name"))
async def cgame_name(callback: types.CallbackQuery, state: FSMContext ):
    await callback.answer()
    last = await callback.message.bot.edit_message_caption(chat_id=callback.message.chat.id,message_id=callback.message.message_id
                                                           ,caption='Какое название вас устроит?',
                                  )
    await state.set_state(game_repair.name)
    GameDev.last_game_id2 = last.message_id


@admin_router.message(game_repair.name, F.text)
async def ugame_name(message: types.Message,state: FSMContext, ):
    await state.update_data(name=message.text)
    await message.delete()
    last = await message.bot.edit_message_caption(chat_id=message.chat.id,message_id=GameDev.last_game_id2,caption=
    'Хотите еще что-то изменить?',
                                  reply_markup=game_kb)
    game_repair.ch_ch = True
    await state.set_state(game_repair.change)
    GameDev.last_game_id2 = last.message_id



@admin_router.callback_query(game_repair.change, F.data.startswith("ch_description"))
async def cgame_destriction(callback: types.CallbackQuery, state: FSMContext,):
    await callback.answer()
    last = await callback.message.bot.edit_message_caption(chat_id=callback.message.chat.id,
                                                           message_id=callback.message.message_id
                                                           , caption='Ща замажу, че писать то?',
                                  )
    await state.set_state(game_repair.description)
    GameDev.last_game_id2 = last.message_id


@admin_router.message(game_repair.description, F.text)
async def upgame_destriction(message: types.Message, state: FSMContext,):
    desc = f'<i>{message.text}</i>'
    await state.update_data(description=desc)
    await message.delete()
    last = await message.bot.edit_message_caption(chat_id=message.chat.id,message_id=GameDev.last_game_id2,
                                                  caption='Хотите еще что-то изменить?',
                                  reply_markup=game_kb)
    game_repair.ch_ch = True
    await state.set_state(game_repair.change)
    GameDev.last_game_id2 = last.message_id



@admin_router.callback_query(game_repair.change, F.data.startswith("ch_food"))
async def cgame_food(callback: types.CallbackQuery, session:AsyncSession,state: FSMContext, ):
    await callback.answer()
    food = await orm_get_food(session)
    btns = {category.classification: str(category.id) for category in food}
    last = await callback.message.bot.edit_message_caption(chat_id=callback.message.chat.id,
                                                           message_id=callback.message.message_id
                                                           , caption='Хм думаю что-то из следующего?', reply_markup=get_callback_btns(btns=btns))
    await state.set_state(game_repair.food)
    GameDev.last_game_id2 = last.message_id


@admin_router.callback_query(game_repair.food, )
async def ugame_food(callback: types.CallbackQuery, state: FSMContext,):
    await callback.answer()
    await state.update_data(food=callback.data)
    last = await callback.message.bot.edit_message_caption(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                                  caption='Хотите еще что-то изменить?',
                                  reply_markup=game_kb)
    game_repair.ch_ch = True
    await state.set_state(game_repair.change)
    GameDev.last_game_id2 = last.message_id




@admin_router.callback_query(game_repair.change, F.data.startswith("ch_image"))
async def callback_image(callback: types.CallbackQuery, state: FSMContext, ):
    await callback.answer()
    last = await callback.message.bot.edit_message_caption(chat_id=callback.message.chat.id,
                                                           message_id=callback.message.message_id
                                                           , caption=f'Можно я буду на фотке? Ну пожалуйста❤️',
                                  )
    await state.set_state(game_repair.image)
    GameDev.last_game_id2 = last.message_id


@admin_router.message(game_repair.image, F.photo)
async def update_image(message: types.Message, state: FSMContext,):
    await state.update_data(image=message.photo[-1].file_id)
    await message.delete()
    last = await message.bot.edit_message_caption(chat_id=message.chat.id,
                                                           message_id=GameDev.last_game_id2,
                                                           caption='Хотите еще что-то изменить?',
                                  reply_markup=game_kb)
    game_repair.ch_ch = True
    await state.set_state(game_repair.change)
    GameDev.last_game_id2 = last.message_id


@admin_router.callback_query(game_repair.change, F.data.startswith("home"))
async def callback_image(callback: types.CallbackQuery, state: FSMContext,  session: AsyncSession):
    data = await state.get_data()
    if game_repair.ch_ch == False:
        await callback.answer()
        media = types.InputMediaPhoto(media=os.getenv('zaebis'),
                                      caption='Дай-ка в штанишки твои залезу', )
        tr = await callback.message.bot.edit_message_media(chat_id=callback.message.chat.id,message_id=callback.message.message_id,
                                                      media=media, )
        await asyncio.sleep(0.7)
        await callback.message.bot.delete_message(chat_id=callback.message.chat.id, message_id=tr.message_id,)

        await callback.message.answer_photo(photo=os.getenv('big_pansil'),caption='кхм. лучше домой', reply_markup=ADMIN_KB)
        await state.clear()
    else:
        await orm_update_game(session, game_repair.game_for_change.id, data)
        await callback.answer('✨стало пизже✨')
        medias = types.InputMediaPhoto(media=os.getenv('zaebis'),
                                       caption='да, не легкая это работка')
        sr = await callback.message.bot.edit_message_media(chat_id=callback.message.chat.id,
                                                      message_id=callback.message.message_id,
                                                      media=medias, )
        await asyncio.sleep(1)
        await callback.message.bot.delete_message(chat_id=callback.message.chat.id, message_id=sr.message_id,)

        await callback.message.answer_photo(photo=os.getenv('big_pansil'),caption='можно и отдохнуть', reply_markup=ADMIN_KB)
        await state.clear()
        game_repair.ch_ch = False

    await  state.clear()






#=======================================================================================================================
#========================================= =============================================================================


@admin_router.callback_query(GameDev.preSTART,F.data.startswith('back'))
async def back_game(callback: types.CallbackQuery,session:AsyncSession,  state: FSMContext) -> None:
    global list_game,game_make
    current_state = await state.get_state()
    await callback.answer()
    previous = None
    play_list = await orm_get_games(session)
    btns = {game.name: f'category_{game.id}' for game in play_list}
    for step in GameDev.__all_states__:
        if step.state == current_state:

            await state.set_state(previous)
            media = types.InputMediaPhoto(media=os.getenv('game_home'), caption=f"{GameDev.texts[previous.state]}")
            list_game = await callback.message.edit_media(media=media,
                                          reply_markup=get_callback_btns(btns=btns,
                                                                                sizes=(1,)))
            game_make = await callback.message.answer("Или может что-то новенькое?",
                                                      reply_markup=get_keyboard('СОЗДАТЬ'))
            await  state.set_state(GameDev.development)
            GameDev.last_game_id = game_make.message_id
            GameDev.last_game_id2 = list_game.message_id

            return
        previous = step





@admin_router.callback_query(GameDev.preSTART,F.data.startswith('exit'))
async def exit_game(callback: types.CallbackQuery,  state: FSMContext):
    await callback.answer()
    media = types.InputMediaVideo(media=os.getenv('game_home'),
                                  caption="правильно, нахуй их, на чем теперь залипнем? кста, как тебе?👆😮‍💨",)
    await callback.message.edit_media(media=media)
    await callback.message.answer('Охх, подзаебалась я маленько, ты как?',reply_markup=home_kb)
    await state.clear()
#========================================================================================




@admin_router.message(or_f(StateFilter(GameDev.development), StateFilter(GameDev.name)), F.text.casefold() == "назад")
async def back_home(message: types.Message, state: FSMContext) -> None:
    await message.delete()

    lat = await message.answer("возвращаемся...",)
    if (await state.get_state() == "GameDev:name"):
        await message.bot.delete_message(message.chat.id, GameDev.last_game_id)
    if (await state.get_state() == "GameDev:development"):
        await asyncio.sleep(0.07)
        await message.bot.delete_message(message.chat.id, GameDev.last_game_id)
        await asyncio.sleep(0.07)
        await message.bot.delete_message(message.chat.id, GameDev.last_game_id2)
    await asyncio.sleep(0.3)
    await state.clear()
    await message.bot.delete_message(chat_id=lat.chat.id, message_id=lat.message_id,
                                        )
    await message.answer('мы дома, глава🫡', reply_markup=ADMIN_KB)





@admin_router.message(StateFilter(GameDev), F.text.casefold() == "назад")
async def back_step(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    previous = None
    for step in GameDev.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(f"Мдаа.. Игры делать не PR0N смотреть...😓\n{GameDev.texts[previous.state]}")
            return
        previous = step



@admin_router.message(GameDev.development ,F.text == 'СОЗДАТЬ')
async def add_GAME(message: types.Message,state: FSMContext):
    await message.delete()
    await message.bot.delete_message(message.chat.id, GameDev.last_game_id)
    aout = await message.answer('Подготавливаем условия...',reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(0.4)
    await message.bot.delete_message(message.chat.id, aout.message_id)
    await message.bot.delete_message(message.chat.id, GameDev.last_game_id2)
    name = await message.answer("Как будет называться игра?",
                                        )
    await state.set_state(GameDev.name)
    GameDev.last_game_id = name.message_id


@admin_router.message(GameDev.name, F.text)
async def add_GAME_name(message: types.Message, state: FSMContext):
    await message.delete()
    await state.update_data(name=message.text)
    desc = await message.bot.edit_message_text(chat_id=message.chat.id,message_id=GameDev.last_game_id,
                                               text="Самое то для этого, если вы понимаете о чем я🤭🔥\nТеперь займемся описанием?")
    await state.set_state(GameDev.description)
    GameDev.last_game_id = desc.message_id

@admin_router.message(GameDev.description, F.text)
async def add_GAME_desc(message: types.Message, state: FSMContext):
    text = f'<i>{message.text}</i>'
    await state.update_data(description=text)
    await message.delete()
    photo = await message.bot.edit_message_text(chat_id=message.chat.id, message_id=GameDev.last_game_id,
                                               text="Вау, мне аж самой захотелось поиграть... Для уверенности закинем фоточку!")
    await state.set_state(GameDev.image)
    GameDev.last_game_id = photo.message_id



@admin_router.message(GameDev.image, F.photo)
async def add_GAME_image(message: types.Message,session: AsyncSession, state: FSMContext):
    await state.update_data(image=message.photo[-1].file_id)
    await message.delete()
    food = await orm_get_food(session)
    btns = {category.classification: str(category.id) for category in food}
    fod = await message.bot.edit_message_text(chat_id=message.chat.id,message_id=GameDev.last_game_id,
                                               text="Жалко это не ты, я бы посмотрела🔥\nТак, о чем это мы? Точно а какой это фуд?",
                         reply_markup=get_callback_btns(
                        btns=btns, sizes=(2,2,2)))
    await state.set_state(GameDev.food_id)
    GameDev.last_game_id = fod.message_id



@admin_router.callback_query(GameDev.food_id)
async def add_GAME_food(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    if int(callback.data) in [category.id for category in await orm_get_food(session)]:
        await callback.answer()
        await state.update_data(food=callback.data)
    else:
        exec = await callback.message.bot.edit_message_text(chat_id=callback.message.chat.id,message_id=GameDev.last_game_id,
                                               text='Выберите катеорию из кнопок.')
        await callback.answer()
        GameDev.last_game_id = exec.message_id

    data = await state.get_data()
    try:
        await orm_add_game(session, data)
        tryt = await callback.message.bot.edit_message_text(chat_id=callback.message.chat.id, message_id=GameDev.last_game_id,
                                                   text="Отлично, +игрушка в копилку!",)
        await state.clear()
        await asyncio.sleep(1)
        await callback.message.bot.delete_message(chat_id=callback.message.chat.id, message_id=tryt.message_id)
        await callback.message.answer('Мы дома' ,reply_markup=ADMIN_KB)


    except Exception as e:
        scr = await callback.message.bot.edit_message_text(chat_id=callback.message.chat.id, message_id=GameDev.last_game_id,
                                                   text=
            f"Ошибочка вышла😩: \n{str(e)}\nСаня пидарас, опять хуевертит🤬",

        )
        await asyncio.sleep(1)
        await callback.message.bot.delete_message(chat_id=callback.message.chat.id, message_id=scr.message_id)
        await callback.message.answer('Ну и хуй с ним',reply_markup=ADMIN_KB,)

    await state.clear()




#=========================================------____FOOD_CLASS____-------==============================================
#=========================================------____FOOD_CLASS____-------==============================================


class Foodcort(StatesGroup):
    change = State()
    ch_change = State()
    ch_delete = State()
    ch_name = State()
    ch_description = State()
    foodcort = State()
    name = State()
    description = State()

    ch_ch = False
    fod_for_change = None

    last_food = None
    last_food2 = None
    other = None

@admin_router.message(F.text == 'FOOD')
async def admin_fooding(message: types.Message, session: AsyncSession, state: FSMContext):
    food_list = await orm_get_food(session)
    btns = {food.classification : f'category_{food.id}' for food in food_list}
    fos = await message.answer("Что-ж вот список смачного food'a", reply_markup=get_callback_btns(btns=btns,
                                                                                sizes=(1,)))

    fods = await message.answer("Че делать будем?",reply_markup=get_keyboard('СОЗДАТЬ',
                                                                   'ИЗМЕНИТЬ',
                                                                   'УДАЛИТЬ',
                                                                    'НА ХАТУ',
                                                        sizes=(1,1,1)))
    await state.set_state(Foodcort.foodcort)
    Foodcort.last_food = fos.message_id
    Foodcort.last_food2 = fods.message_id





@admin_router.message(StateFilter(Foodcort.foodcort),F.text == 'НА ХАТУ')
async def add_FOOD(message: types.Message,state: FSMContext):
    st = await message.bot.edit_message_text(chat_id=message.chat.id, message_id=Foodcort.last_food,
                                        text="Иду домой...")
    await message.delete()
    await asyncio.sleep(1)
    await st.delete()
    await message.answer('мы дома', reply_markup=ADMIN_KB)

    await message.bot.delete_message(chat_id=message.chat.id, message_id=Foodcort.last_food2)
    await state.set_state(Foodcort.name)



@admin_router.callback_query(Foodcort.ch_delete)
async def delete_new(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    fod_id = callback.data.split("_")[-1]
    await orm_delete_food(session, int(fod_id))
    await callback.answer('а ну-ка нахуй отсюда.',)
    await callback.message.bot.delete_message(chat_id=callback.message.chat.id, message_id=Foodcort.other)
    await callback.message.answer('Что-ж, поработали и хватит', reply_markup=ADMIN_KB)
    await  state.clear()

@admin_router.message(Foodcort.foodcort, F.text == 'УДАЛИТЬ')
async def dl_FOOD(message: types.Message, session: AsyncSession,state: FSMContext):
    food_list = await orm_get_food(session)
    btns = {food.classification: f'category_{food.id}' for food in food_list}
    other = await message.bot.edit_message_text(chat_id=message.chat.id,message_id=Foodcort.last_food,
                                                text="👆Выберите food, который хотите delete-nahui👆",
                                                reply_markup=get_callback_btns(btns=btns,
                                                                                sizes=(1,)))
    await message.delete()
    Foodcort.other = other.message_id
    await message.bot.delete_message(chat_id=message.chat.id, message_id=Foodcort.last_food2)
    await state.set_state(Foodcort.ch_delete)



@admin_router.message(Foodcort.foodcort, F.text == 'ИЗМЕНИТЬ')
async def CH_FOOD(message: types.Message, session: AsyncSession,state: FSMContext):
    food_list = await orm_get_food(session)
    btns = {food.classification: f'category_{food.id}' for food in food_list}
    ch_fod = await message.bot.edit_message_text(chat_id=message.chat.id,message_id=Foodcort.last_food,
                                                 text="👆Выберите food, который хотите натянуть👆",
                                                 reply_markup=get_callback_btns(btns=btns,
                                                                                sizes=(1,)))
    await message.delete()
    await message.bot.delete_message(chat_id=message.chat.id, message_id=Foodcort.last_food2)
    await state.set_state(Foodcort.change)
    Foodcort.last_food =ch_fod.message_id

@admin_router.callback_query(Foodcort.change)
async def ch_food(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    food_id = callback.data.split("_")[-1]
    fod_for_change = await orm_get_one_food(session, int(food_id))
    Foodcort.fod_for_change = fod_for_change
    await callback.answer()
    set = await callback.bot.edit_message_text(chat_id=callback.message.chat.id,message_id=Foodcort.last_food,text=
        "Редактор Мия в пути! Скажите что хотите исправить?👩‍🎨",
        reply_markup=get_callback_btns(btns={'Название':'name',
                                             'Описание':'description',
                                             'НА ХАТУ': 'home'
                                             },
                                       sizes=(2,)))

    await state.update_data(name=Foodcort.fod_for_change.classification)
    await state.update_data(description=Foodcort.fod_for_change.description)
    await state.set_state(Foodcort.ch_change)
    Foodcort.last_food = set.message_id



@admin_router.callback_query(Foodcort.ch_change, F.data.startswith('name'))
async def sfood(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    nam =await callback.bot.edit_message_text(chat_id=callback.message.chat.id,message_id=Foodcort.last_food,
                                         text='Какое название вас устроит?',
                                  )
    await state.set_state(Foodcort.ch_name)
    Foodcort.last_food = nam.message_id

@admin_router.message(Foodcort.ch_name, F.text)
async def update_name(message: types.Message, state: FSMContext, ):
    await state.update_data(name=message.text)
    await message.delete()
    form = await message.bot.edit_message_text(chat_id=message.chat.id,message_id=Foodcort.last_food,
                                        text='Хотите еще что-то изменить?',
                         reply_markup=get_callback_btns(btns={'Название':'name',
                                                              'Описание':'description',
                                                              'НА ХАТУ':'home'}
                                                    ))
    Foodcort.ch_ch = True
    await state.set_state(Foodcort.ch_change)
    Foodcort.last_food = form.message_id



@admin_router.callback_query(Foodcort.ch_change, F.data.startswith('description'))
async def DOUBLE(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    scr = await callback.bot.edit_message_text(chat_id=callback.message.chat.id,message_id=Foodcort.last_food,
                                               text='Эхх, время в пустую..',
                                  )
    await state.set_state(Foodcort.ch_description)
    Foodcort.last_food = scr.message_id

@admin_router.message(Foodcort.ch_description, F.text)
async def update_description(message: types.Message, state: FSMContext, ):
    await state.update_data(description=message.text)
    awe = await message.bot.edit_message_text(chat_id=message.chat.id,message_id=Foodcort.last_food,
                                        text='Хотите еще что-то изменить?',
                         reply_markup=get_callback_btns(btns={'Название': 'name',
                                                              'Описание': 'description',
                                                              'НА ХАТУ': 'home'}
                                                        ))
    await message.delete()
    Foodcort.ch_ch = True
    await state.set_state(Foodcort.ch_change)
    Foodcort.last_food = awe.message_id


@admin_router.callback_query(Foodcort.ch_change, F.data.startswith('home'))
async def END_CH(callback: types.CallbackQuery,  session: AsyncSession,state: FSMContext):
    data = await state.get_data()
    if Foodcort.ch_ch == False:
        await callback.answer()
        tr = await callback.bot.edit_message_text(chat_id=callback.message.chat.id,message_id=Foodcort.last_food,
                                             text='Да все и так пиздатенько')
        await asyncio.sleep(1)
        sr = await callback.bot.edit_message_text(chat_id=callback.message.chat.id, message_id=tr.message_id,
                                             text='профессиональное обслуживание...')
        await asyncio.sleep(1)
        await callback.message.bot.delete_message(chat_id=callback.message.chat.id, message_id=sr.message_id)
        await callback.message.answer('*swallow*🥵🔞*swallow*', reply_markup=ADMIN_KB)

    else:
        await orm_update_food(session, Foodcort.fod_for_change.id, data)
        await callback.answer('✨стало пизже✨')
        tr = await callback.bot.edit_message_text(chat_id=callback.message.chat.id,message_id=Foodcort.last_food,
                                             text='да, не легкая это работка',)
        await asyncio.sleep(0.8)
        sr = await callback.bot.edit_message_text(chat_id=callback.message.chat.id, message_id=tr.message_id,
                                                  text='профессиональное обслуживание...')
        await asyncio.sleep(1)
        await callback.message.bot.delete_message(chat_id=callback.message.chat.id, message_id=sr.message_id)
        await callback.message.answer('*swallow*🥵🔞*swallow*', reply_markup=ADMIN_KB)
        Foodcort.ch_ch = False

    await  state.clear()
    Foodcort.last_food = None





@admin_router.message(Foodcort.foodcort ,F.text == 'СОЗДАТЬ')
async def add_FOOD(message: types.Message,state: FSMContext):
    awe = await message.bot.edit_message_text(chat_id=message.chat.id,message_id=Foodcort.last_food,
                                        text="Как будет называться food?", )
    await message.delete()
    await message.bot.delete_message(chat_id=message.chat.id,message_id=Foodcort.last_food2)
    await state.set_state(Foodcort.name)
    Foodcort.last_food = awe.message_id

@admin_router.message(Foodcort.name, F.text)
async def add_FOOD_name(message: types.Message, session:AsyncSession, state: FSMContext):
    categories = await orm_get_food(session)
    if message.text in {category.classification: str(category.id) for category in categories}:
        asd = await message.bot.edit_message_text(chat_id=message.chat.id,message_id=Foodcort.last_food,
                                            text="Ой, я нашла совпадение, это точно то название?🧐")
        Foodcort.last_food = asd.message_id
        await message.delete()
    else:
        await state.update_data(name=message.text)
        auf = await message.bot.edit_message_text(chat_id=message.chat.id,message_id=Foodcort.last_food,
                                            text="Что мы представим на свет?")
        await message.delete()
        await state.set_state(Foodcort.description)
        Foodcort.last_food = auf.message_id

@admin_router.message(Foodcort.description, F.text)
async def add_FOOD_name(message: types.Message, session:AsyncSession, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()
    try:
        await orm_create_food(session, data)
        TR = await message.bot.edit_message_text(chat_id=message.chat.id,message_id=Foodcort.last_food,
                                            text="Обработка...", )
        await message.delete()
        await asyncio.sleep(0.7)
        qw =await message.bot.edit_message_text(chat_id=message.chat.id,message_id=TR.message_id,
                                            text='Загрузка...')
        await asyncio.sleep(0.5)
        strr = await message.bot.edit_message_text(chat_id=message.chat.id,message_id=qw.message_id,text='Глубокий минет...')
        await asyncio.sleep(0.6)
        await message.bot.delete_message(chat_id=message.chat.id,message_id=strr.message_id)
        await message.answer('Я закончила!',reply_markup=ADMIN_KB)
        await state.clear()


    except Exception as e:
        TR = await  message.bot.edit_message_text(chat_id=message.chat.id,message_id=Foodcort.last_food,
                                            text=
            f"Ошибочка вышла😩: \n{str(e)}\nСаня пидарас, опять хуевертит🤬",
            )
        await message.delete()
        await message.bot.delete_message(chat_id=message.chat.id,message_id=TR.message_id)
        await message.answer('Ну да и хуй с ним, пошли по бабам', reply_markup=ADMIN_KB)

    await state.clear()

