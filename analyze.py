import sys

sys.path.insert(0, ".")
from app.models.models import SessionLocal, Player, Game, ChampionStats
from app.services.recommend_service import RecommendService

db = SessionLocal()

print("=" * 60)
print("     海克斯大乱斗数据分析报告")
print("=" * 60)

print("\n【玩家战绩汇总】")
print("-" * 50)
players = db.query(Player).all()
for p in players:
    games = db.query(Game).filter(Game.player_id == p.id).all()
    wins = sum(1 for g in games if g.win)
    wr = wins / len(games) * 100 if games else 0
    print(
        f"{p.riot_id:18} {len(games):2}场  {wins}胜 {len(games) - wins}负  胜率:{wr:5.1f}%"
    )

print("\n【英雄胜率排名】")
print("-" * 50)
stats = db.query(ChampionStats).order_by(ChampionStats.win_rate.desc()).all()
for s in stats:
    wr = s.wins / s.total_games * 100
    print(f"{s.champion:15} {s.wins}胜{s.total_games - s.wins}负  胜率:{wr:5.1f}%")

print("\n【推荐选人策略】")
print("-" * 50)
recommendations = RecommendService.get_best_compositions(db)
for i, r in enumerate(recommendations[:5], 1):
    print(f"{i}. {r['champion']} - {r['win_rate']}% ({r['reason']})")

db.close()
