#by Dzhuzo365
from sqlalchemy import String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class News(Base):
    __tablename__ = 'News'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title:Mapped[str] = mapped_column(String(80), nullable=False)
    food: Mapped[str] = mapped_column(String(80))
    news:Mapped[str] = mapped_column(Text)
    image:Mapped[str] = mapped_column(String(150), nullable=True)





class Photo(Base):
    __tablename__ = 'Photo'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    photo: Mapped[str] = mapped_column(String(150), nullable=False)


class Video(Base):
    __tablename__ = 'Video'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    video: Mapped[str] = mapped_column(String(150), nullable=False)


class User(Base):
    __tablename__ = 'User'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    like_food: Mapped[str] = mapped_column(String(150), nullable=False)


class User_set(Base):
    __tablename__ = 'User_set'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('User.username', ondelete='CASCADE'), nullable=False)
    food_id: Mapped[int] = mapped_column(ForeignKey('Food.id'), nullable=False)

    user: Mapped['User'] = relationship(backref='User_set')
    food: Mapped['Food'] = relationship(backref='User_set')

class sUser(Base):
    __tablename__ = 'sUser'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    cls: Mapped[str] = mapped_column(String(50), nullable=False)


class Food(Base):
    __tablename__ = 'Food'
    id: Mapped[int] = mapped_column(primary_key=True
                                     , autoincrement=True)
    classification: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text)



class Games(Base):
    __tablename__ = 'Games'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    image: Mapped[str] = mapped_column(String(100), nullable=False)
    food_id: Mapped[str] = mapped_column(ForeignKey('Food.id'), nullable=False)
    food: Mapped['Food'] = relationship(backref='Games')


class GPT(Base):
    __tablename__ = 'GPT'

    chat_id: Mapped[str] = mapped_column(String(100), nullable=False, primary_key=True)
    con: Mapped[str] = mapped_column(Text)
    con2: Mapped[str] = mapped_column(Text)



class payment(Base):
    __tablename__ = 'payment'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name_wallet: Mapped[str] = mapped_column(String(100), nullable=False)
    adress: Mapped[str] = mapped_column(String(150), nullable=False)