from sqlalchemy import Column, Integer, Float, Boolean
from db.database import Base

class PlayerModel(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    health = Column(Integer)
    regenerate_health = Column(Integer)
    speed = Column(Float)
    jump = Column(Float)
    is_dead = Column(Boolean)
    armor = Column(Integer)
    hit_speed = Column(Integer)
