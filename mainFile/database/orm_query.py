#by Dzhuzo365
from sqlalchemy import select, update, delete, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from mainFile.database.models import News, Photo, Video, Food, Games, sUser, GPT, payment


#////////////////////////////////////////////////____ADMIN____\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
async  def orm_add_admin(session:AsyncSession, data: dict):
    obj = sUser(
        name=data["name"],
        cls=data["cls"],
    )
    session.add(obj)
    await session.commit()

async def orm_get_admins(session: AsyncSession):
    query = select(sUser)
    result = await session.execute(query)
    users = result.scalars().all()
    usernames = [user.name for user in users]
    return usernames

async def orm_get_admin(session: AsyncSession, admin_id: int):
    query = select(sUser).where(sUser.id == admin_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_update_admin(session: AsyncSession, admin_id: int, data):
    query = update(sUser).where(sUser.id == admin_id).values(
        name=data["name"],
        cls=data["cls"],
    )
    await session.execute(query)
    await session.commit()

async def orm_delete_admin(session: AsyncSession, admin_id: int):
    query = delete(sUser).where(sUser.id == admin_id)
    await session.execute(query)
    await session.commit()



async def get_and_send_admins_with_positions(session: AsyncSession):
    query = select(sUser)
    result = await session.execute(query)
    users = result.scalars().all()
    admins_text = "\n".join(f"{i+1}.  <b>{admin.name}</b> ➟ <i>{admin.cls}</i>"  for i, admin in enumerate(users))

    return admins_text

async def full_info_admins(session: AsyncSession):
    query = select(sUser)
    result = await session.execute(query)
    admins = result.scalars().all()
    return admins
#===========================================================================================================================

async  def orm_add_news(session:AsyncSession, data: dict):
    obj = News(
        title=data["name"],
        news=data["description"],
        image=data["image"],
        food=data["food"]
    )
    session.add(obj)
    await session.commit()

async def orm_get_news(session: AsyncSession):
    query = select(News)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_count_news(session: AsyncSession):
    # statement = select(News)
    # result = await session.execute(statement)
    # row_count = result.scalars()
    # return row_count == 0
    stmt = select(News)
    result = await session.execute(stmt)
    rows = result.fetchall()
    count = len(rows)
    return count == 0


async def orm_get_new(session: AsyncSession, news_id: int):
    query = select(News).where(News.id == news_id)
    result = await session.execute(query)
    return result.scalar()
#==============================================____перелистывание новостей____==========================================


async def orm_get_previous_new(session: AsyncSession, news_id: int):
    query = select(News).where(News.id < news_id).order_by(desc(News.id)).limit(1)
    result = await session.execute(query)
    return result.scalar()

async def orm_get_next_new(session: AsyncSession, news_id: int):
    query = select(News).where(News.id > news_id).order_by(News.id).limit(1)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_end_new(session: AsyncSession):
    result = await session.execute(
        select(News).order_by(desc(News.id)).limit(1))

    last_record = result.scalar()
    return [last_record]

#=======================================================================================================================

async def orm_update_new(session: AsyncSession, new_id: int, data):
    query = update(News).where(News.id == new_id).values(
        title=data["name"],
        news=data["description"],
        image=data["image"],
        food=data["food"]
    )
    await session.execute(query)
    await session.commit()


async def orm_delete_new(session: AsyncSession, new_id: int):
    query = delete(News).where(News.id == new_id)
    await session.execute(query)
    await session.commit()


#======================================---MEDIA_LOCK---==================================================================

async  def orm_add_photo(session:AsyncSession, data: dict):
    obj = Photo(
        photo=data["photo"],
    )
    session.add(obj)
    await session.commit()


async  def orm_add_video(session:AsyncSession, data: dict):
    obj = Video(
        video=data["video"],

    )
    session.add(obj)
    await session.commit()


async def orm_get_photo(session: AsyncSession):
    result = await session.execute(
        select(Photo).order_by(func.random()).limit(1)
    )
    photo_object = result.scalar_one_or_none()

    return photo_object.photo


async def orm_get_video(session: AsyncSession):
    result = await session.execute(
        select(Video).order_by(func.random()).limit(1)
    )
    video_object = result.scalar_one_or_none()

    return video_object.video


async def orm_delete_media(session: AsyncSession):
    query = delete(Photo).where(Photo.id>0)
    await session.execute(query)
    await session.commit()

#======================================---FOOD_LOCK---==================================================================


async def orm_get_food(session: AsyncSession):
    query = select(Food)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_get_one_food(session: AsyncSession, food_id: int):
    query = select(Food).where(Food.id == food_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_create_food(session: AsyncSession, data: dict):
    obj = Food(
        classification=data['name'],
        description=data['description']
    )
    session.add(obj)
    await session.commit()

async def orm_update_food(session: AsyncSession, food_id: int, data):
    query = update(Food).where(Food.id == food_id).values(
        classification=data["name"],
        description=data["description"]
    )
    await session.execute(query)
    await session.commit()

async def orm_delete_food(session: AsyncSession, food_id: int):
    query = delete(Food).where(Food.id == food_id)
    await session.execute(query)
    await session.commit()


#======================================---PLAY_LOCK---==================================================================


async  def orm_add_game(session:AsyncSession, data: dict):
    obj = Games(
        name=data["name"],
        description=data["description"],
        food_id=int(data["food"]),
        image=data["image"]
    )
    session.add(obj)
    await session.commit()

# .where(Games.food_id == int(food_id))
async def orm_get_games(session: AsyncSession):
    query = select(Games)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_game(session: AsyncSession, game_id: int):
    query = select(Games).where(Games.id == game_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_update_game(session: AsyncSession, game_id: int, data:dict):
    query = update(Games).where(Games.id == game_id).values(
        name=data["name"],
        description=data["description"],
        food_id=int(data["food"]),
        image=data["image"]
    )
    await session.execute(query)
    await session.commit()


async def orm_delete_game(session: AsyncSession, game_id: int):
    query = delete(Games).where(Games.id == game_id)
    await session.execute(query)
    await session.commit()


#======================================================================================================================

async def orm_add_gpt(session: AsyncSession, chat_id,con,con2):
    obj = GPT(
        chat_id=chat_id,
        con=con,
        con2=con2
    )
    session.add(obj)
    await session.commit()


async def orm_get_gpt(session: AsyncSession):
    # query = select(GPT)
    # result = await session.execute(query)
    # return result.scalars().all()
    query = select(GPT)
    result = await session.execute(query)
    gpt_data = result.scalars().first()
    return gpt_data


async def orm_update_gpt(session: AsyncSession, chat_id: str,con, con2):
    query = update(GPT).where(GPT.chat_id == chat_id ).values(
        chat_id=chat_id,
        con=con,
        con2=con2,
    )
    await session.execute(query)
    await session.commit()

async def orm_get_gpt_chat_ids(session: AsyncSession):
    query = select(GPT.chat_id)
    result = await session.execute(query)
    return [str(row) for row in result.scalars().all()]
#=======================================================================================================================
#_____________________________________________PAYMENT___________________________________________________________________

async def orm_get_payment(session:AsyncSession):
    query = select(payment)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_delete_payment(session: AsyncSession, pay_id: int):
    query = delete(payment).where(payment.id == pay_id)
    await session.execute(query)
    await session.commit()


async def orm_add_pay(session: AsyncSession, data: dict):
    obj = payment(
        payment_name=data['payment'],
        adress=data['address'],
    )
    session.add(obj)
    await session.commit()