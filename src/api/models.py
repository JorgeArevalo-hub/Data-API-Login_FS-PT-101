from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Float, Integer, Date
from enum import Enum as PyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from sqlalchemy import Enum as SQLAEnum

db = SQLAlchemy()


class enumRank(PyEnum):
    Diamond = "Diamond"
    Master = "Master"
    Grandmaster = "Grandmaster"
    Challenger = "Challenger"
    NA = "N/A"    

class enumGender(PyEnum):
    Male = "Male"
    Female = "Female"
    Other = "Other"
    NA = "N/A"
class enumLane(PyEnum):
    Top = "Top"
    Jungle = "Jungle"
    Mid = "Mid"
    ADCarry = "ADCarry"
    Support = "Support"
    NA = "N/A"

class Users(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    nick: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    gender: Mapped[enumGender] = mapped_column(SQLAEnum(enumGender), default=enumGender.NA, nullable=False)
    rank: Mapped[enumRank] = mapped_column(SQLAEnum(enumRank), default=enumRank.NA, nullable=False)
    mainrole: Mapped[enumLane] = mapped_column(SQLAEnum(enumLane), default=enumLane.NA, nullable=False)

    builds: Mapped[list["Builds"]] = relationship("Builds", back_populates="user")
    favourites: Mapped[list["Favourites"]] = relationship("Favourites", back_populates="user")

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "nick": self.nick,
            "gender": self.gender.value,
            "rank": self.rank.value,
            "mainrole": self.mainrole.value,
        }
    
class Champions(db.Model):
    __tablename__ = "champions"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    lane: Mapped[enumLane] = mapped_column(SQLAEnum(enumLane), default=enumLane.NA, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    media: Mapped[str] = mapped_column(String, nullable=False)
    stats_id: Mapped[int] = mapped_column(ForeignKey("stats.id"), nullable=False)

    builds: Mapped[list["Builds"]] = relationship("Builds", back_populates="champion")
    stat: Mapped["Stats"] = relationship("Stats", back_populates="champion", uselist=False)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "lane": self.lane.value,
            "type": self.type,
            "media": self.media,
            "stats": self.stat.serialize() if self.stat else None
        }

class Items(db.Model):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    stats_id: Mapped[int] = mapped_column(ForeignKey("stats.id"), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    media: Mapped[str] = mapped_column(String, nullable=False)

    stat: Mapped["Stats"] = relationship("Stats", back_populates="items")
    builditems: Mapped[list["Builditems"]] = relationship("Builditems", back_populates="item")

    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "stats_id": self.stats_id,
            "description": self.description,
            "media": self.media,
        }
    
class Stats(db.Model):
    __tablename__ = "stats"
    id: Mapped[int] = mapped_column(primary_key=True)
    ad: Mapped[int] = mapped_column(Integer, nullable=False)
    ap: Mapped[int] = mapped_column(Integer, nullable=False)
    hp: Mapped[int] = mapped_column(Integer, nullable=False)
    hpreg: Mapped[int] = mapped_column(Integer, nullable=False)
    mana: Mapped[int] = mapped_column(Integer, nullable=False)
    manareg: Mapped[int] = mapped_column(Integer, nullable=False)
    atspeed: Mapped[Float] = mapped_column(Float, nullable=False)
    lifesteal: Mapped[int] = mapped_column(Integer, nullable=False)
    spellvamp: Mapped[int] = mapped_column(Integer, nullable=False)
    crit: Mapped[int] = mapped_column(Integer, nullable=False)
    cd: Mapped[int] = mapped_column(Integer, nullable=False)
    armor: Mapped[int] = mapped_column(Integer, nullable=False)
    mresist: Mapped[int] = mapped_column(Integer, nullable=False)
    armorpen: Mapped[int] = mapped_column(Integer, nullable=False)
    magicpen: Mapped[int] = mapped_column(Integer, nullable=False)
    lethal: Mapped[int] = mapped_column(Integer, nullable=False)
    mvspeed: Mapped[int] = mapped_column(Integer, nullable=False)
    
    champion: Mapped["Champions"] = relationship("Champions", back_populates="stat", uselist=False)

    items: Mapped[list["Items"]] = relationship("Items", back_populates="stat")

    def serialize(self):
        return{
            "id": self.id,
            "ad": self.ad,
            "ap": self.ap,
            "hp": self.hp,
            "hpreg": self.hpreg,
            "mana": self.mana,
            "manareg": self.manareg,
            "atspeed": self.atspeed,
            "lifesteal": self.lifesteal,
            "spellvamp": self.spellvamp,
            "crit": self.crit,
            "cd": self.cd,
            "armor": self.armor,
            "mresist": self.mresist,
            "armorpen": self.armorpen,
            "magicpen": self.magicpen,
            "lethal": self.lethal,
            "mvspeed": self.mvspeed,

        }

class Builds(db.Model):
    __tablename__ = "builds"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    champion_id: Mapped[int] = mapped_column(ForeignKey("champions.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    creation_date: Mapped[datetime] = mapped_column(Date,nullable=False)

    champion: Mapped["Champions"] = relationship("Champions", back_populates="builds", uselist=False)
    user: Mapped["Users"] = relationship("Users", back_populates="builds", uselist=False)
    builditems: Mapped[list["Builditems"]] = relationship("Builditems", back_populates="build")
    favourites: Mapped[list["Favourites"]] = relationship("Favourites", back_populates="build")

    def serialize(self):
        return{
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "champion_id": self.champion_id,
            "user_id": self.user_id,
            "creation_date": self.creation_date,
            "user": self.user.serialize() if self.user else None,
            "items": sorted(
            [{"position": bi.item_position, **bi.item.serialize()} for bi in self.builditems],
            key=lambda x: x["position"]
            )

        }

class Builditems(db.Model):
    __tablename__ = "builditems"
    build_id: Mapped[int] = mapped_column(ForeignKey("builds.id"),primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"),primary_key=True)
    item_position: Mapped[int] = mapped_column(Integer, nullable=False)

    item: Mapped["Items"] = relationship("Items", back_populates="builditems")
    build: Mapped["Builds"] = relationship("Builds", back_populates="builditems")

    
    def serialize(self):
        return{
            "build_id": self.build_id,
            "item_id": self.item_id,
            "item_position": self.item_position,
        }


class Favourites(db.Model):
    __tablename__ = "favourites"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"),primary_key=True)
    build_id: Mapped[int] = mapped_column(ForeignKey("builds.id"),primary_key=True)

    user: Mapped["Users"] = relationship("Users", back_populates="favourites")
    build: Mapped["Builds"] = relationship("Builds", back_populates="favourites")

    
    def serialize(self):
        return{
            "user_id": self.user_id,
            "build_id": self.build_id,
        }