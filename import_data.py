import sys

sys.path.insert(0, ".")
from app.models.models import init_db, SessionLocal, Player, Game, ChampionStats

init_db()
db = SessionLocal()

db.query(Game).delete()
db.query(Player).delete()
db.query(ChampionStats).delete()
db.commit()

games_data = [
    {
        "ally": [
            {
                "name": "狂幽#7812",
                "champion": "Tristana",
                "kills": 5,
                "deaths": 3,
                "assists": 9,
                "win": True,
            },
            {
                "name": "逆天的皮城",
                "champion": "Lucian",
                "kills": 10,
                "deaths": 4,
                "assists": 5,
                "win": True,
            },
            {
                "name": "我在等",
                "champion": "Ornn",
                "kills": 2,
                "deaths": 4,
                "assists": 11,
                "win": True,
            },
            {
                "name": "浮夸的狂野",
                "champion": "Ashe",
                "kills": 6,
                "deaths": 4,
                "assists": 12,
                "win": True,
            },
            {
                "name": "夜未央、",
                "champion": "Blitzcrank",
                "kills": 2,
                "deaths": 5,
                "assists": 12,
                "win": True,
            },
        ],
        "enemy": [
            {
                "name": "嗯啊好累",
                "champion": "Graves",
                "kills": 3,
                "deaths": 5,
                "assists": 3,
                "win": False,
            },
            {
                "name": "你的小可爱",
                "champion": "Kayn",
                "kills": 4,
                "deaths": 6,
                "assists": 4,
                "win": False,
            },
            {
                "name": "追风少年",
                "champion": "Yone",
                "kills": 7,
                "deaths": 5,
                "assists": 6,
                "win": False,
            },
            {
                "name": "这波啊这波",
                "champion": "Jhin",
                "kills": 4,
                "deaths": 5,
                "assists": 2,
                "win": False,
            },
            {
                "name": "皮城女警",
                "champion": "Xayah",
                "kills": 3,
                "deaths": 6,
                "assists": 4,
                "win": False,
            },
        ],
    },
    {
        "ally": [
            {
                "name": "浮夸的狂野",
                "champion": "Lucian",
                "kills": 7,
                "deaths": 5,
                "assists": 8,
                "win": False,
            },
            {
                "name": "夜未央、",
                "champion": "Ashe",
                "kills": 2,
                "deaths": 7,
                "assists": 7,
                "win": False,
            },
            {
                "name": "狂幽#7812",
                "champion": "Xayah",
                "kills": 4,
                "deaths": 6,
                "assists": 4,
                "win": False,
            },
            {
                "name": "逆天的皮城",
                "champion": "Ornn",
                "kills": 2,
                "deaths": 5,
                "assists": 8,
                "win": False,
            },
            {
                "name": "我在等",
                "champion": "Blitzcrank",
                "kills": 1,
                "deaths": 7,
                "assists": 10,
                "win": False,
            },
        ],
        "enemy": [
            {
                "name": "追风少年",
                "champion": "Yone",
                "kills": 9,
                "deaths": 3,
                "assists": 8,
                "win": True,
            },
            {
                "name": "嗯啊好累",
                "champion": "Graves",
                "kills": 10,
                "deaths": 4,
                "assists": 8,
                "win": True,
            },
            {
                "name": "你的小可爱",
                "champion": "Kayn",
                "kills": 7,
                "deaths": 3,
                "assists": 7,
                "win": True,
            },
            {
                "name": "皮城女警",
                "champion": "Jinx",
                "kills": 10,
                "deaths": 3,
                "assists": 7,
                "win": True,
            },
            {
                "name": "这波啊这波",
                "champion": "Jhin",
                "kills": 5,
                "deaths": 2,
                "assists": 9,
                "win": True,
            },
        ],
    },
    {
        "ally": [
            {
                "name": "逆天的皮城",
                "champion": "Lucian",
                "kills": 7,
                "deaths": 3,
                "assists": 7,
                "win": True,
            },
            {
                "name": "夜未央、",
                "champion": "Blitzcrank",
                "kills": 1,
                "deaths": 5,
                "assists": 11,
                "win": True,
            },
            {
                "name": "我在等",
                "champion": "Ornn",
                "kills": 1,
                "deaths": 4,
                "assists": 9,
                "win": True,
            },
            {
                "name": "浮夸的狂野",
                "champion": "Jinx",
                "kills": 10,
                "deaths": 2,
                "assists": 6,
                "win": True,
            },
            {
                "name": "皮城女警",
                "champion": "Ashe",
                "kills": 6,
                "deaths": 2,
                "assists": 11,
                "win": True,
            },
        ],
        "enemy": [
            {
                "name": "追风少年",
                "champion": "Yone",
                "kills": 7,
                "deaths": 5,
                "assists": 6,
                "win": False,
            },
            {
                "name": "嗯啊好累",
                "champion": "Graves",
                "kills": 3,
                "deaths": 5,
                "assists": 3,
                "win": False,
            },
            {
                "name": "你的小可爱",
                "champion": "Kayn",
                "kills": 5,
                "deaths": 6,
                "assists": 3,
                "win": False,
            },
            {
                "name": "这波啊这波",
                "champion": "Jhin",
                "kills": 4,
                "deaths": 5,
                "assists": 2,
                "win": False,
            },
            {
                "name": "狂幽#7812",
                "champion": "Xayah",
                "kills": 3,
                "deaths": 6,
                "assists": 3,
                "win": False,
            },
        ],
    },
]

all_player_names = set()
for game in games_data:
    for p in game["ally"] + game["enemy"]:
        all_player_names.add(p["name"])

for name in all_player_names:
    parts = name.split("#")
    player = Player(
        riot_id=name, game_name=parts[0], tag_line=parts[1] if len(parts) > 1 else ""
    )
    db.add(player)

db.commit()

for game in games_data:
    for p in game["ally"] + game["enemy"]:
        player = db.query(Player).filter(Player.riot_id == p["name"]).first()
        if player:
            game_record = Game(
                player_id=player.id,
                champion=p["champion"],
                win=p["win"],
                kills=p["kills"],
                deaths=p["deaths"],
                assists=p["assists"],
            )
            db.add(game_record)

            stats = (
                db.query(ChampionStats)
                .filter(ChampionStats.champion == p["champion"])
                .first()
            )
            if not stats:
                stats = ChampionStats(champion=p["champion"], total_games=0, wins=0)
                db.add(stats)
                db.flush()
            stats.total_games += 1
            if p["win"]:
                stats.wins += 1
            stats.win_rate = stats.wins / stats.total_games

    db.commit()

print("Imported", len(games_data), "games")
print("Players:", db.query(Player).count())
print("Games:", db.query(Game).count())
print("Stats:", db.query(ChampionStats).count())

db.close()
