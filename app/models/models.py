from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
from config import DATABASE_URL

Base = declarative_base()

class Player(Base):
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True)
    riot_id = Column(String(100), unique=True, nullable=False)
    game_name = Column(String(50))
    tag_line = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    games = relationship("Game", back_populates="player")

class Game(Base):
    __tablename__ = "games"
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    champion = Column(String(30))
    win = Column(Boolean)
    kills = Column(Integer)
    deaths = Column(Integer)
    assists = Column(Integer)
    game_duration = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    player = relationship("Player", back_populates="games")

class ChampionStats(Base):
    __tablename__ = "champion_stats"
    
    id = Column(Integer, primary_key=True)
    champion = Column(String(30), unique=True)
    total_games = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    avg_kills = Column(Float, default=0.0)
    avg_deaths = Column(Float, default=0.0)
    avg_assists = Column(Float, default=0.0)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
