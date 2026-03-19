from app.models.models import Player, Game, ChampionStats, get_db
from sqlalchemy.orm import Session
from sqlalchemy import func

class DataService:
    @staticmethod
    def save_game_data(db: Session, player_riot_id: str, game_data: dict):
        riot_id = game_data.get("player_id") or player_riot_id
        if not riot_id:
            return None
        
        parts = riot_id.split("#")
        game_name = parts[0] if len(parts) > 0 else ""
        tag_line = parts[1] if len(parts) > 1 else ""
        
        player = db.query(Player).filter(Player.riot_id == riot_id).first()
        if not player:
            player = Player(riot_id=riot_id, game_name=game_name, tag_line=tag_line)
            db.add(player)
            db.commit()
            db.refresh(player)
        
        champion = game_data.get("champion")
        if champion:
            game = Game(
                player_id=player.id,
                champion=champion,
                win=game_data.get("win"),
                kills=game_data.get("kills", 0),
                deaths=game_data.get("deaths", 0),
                assists=game_data.get("assists", 0)
            )
            db.add(game)
            db.commit()
            
            DataService.update_champion_stats(db, champion, game_data.get("win", False), 
                                              game_data.get("kills", 0), 
                                              game_data.get("deaths", 0), 
                                              game_data.get("assists", 0))
        
        return player
    
    @staticmethod
    def update_champion_stats(db: Session, champion: str, win: bool, kills: int, deaths: int, assists: int):
        stats = db.query(ChampionStats).filter(ChampionStats.champion == champion).first()
        
        if not stats:
            stats = ChampionStats(champion=champion, total_games=1, wins=1 if win else 0)
            db.add(stats)
        else:
            stats.total_games += 1
            if win:
                stats.wins += 1
        
        stats.win_rate = stats.wins / stats.total_games if stats.total_games > 0 else 0
        
        total_k = db.query(func.sum(Game.kills)).filter(Game.champion == champion).scalar() or 0
        total_d = db.query(func.sum(Game.deaths)).filter(Game.champion == champion).scalar() or 0
        total_a = db.query(func.sum(Game.assists)).filter(Game.champion == champion).scalar() or 0
        
        stats.avg_kills = total_k / stats.total_games
        stats.avg_deaths = total_d / stats.total_games
        stats.avg_assists = total_a / stats.total_games
        
        db.commit()
    
    @staticmethod
    def get_player_stats(db: Session, riot_id: str):
        player = db.query(Player).filter(Player.riot_id == riot_id).first()
        if not player:
            return None
        
        games = db.query(Game).filter(Game.player_id == player.id).all()
        
        total_games = len(games)
        wins = sum(1 for g in games if g.win)
        win_rate = wins / total_games if total_games > 0 else 0
        
        champion_games = {}
        for game in games:
            if game.champion:
                if game.champion not in champion_games:
                    champion_games[game.champion] = {"games": 0, "wins": 0}
                champion_games[game.champion]["games"] += 1
                if game.win:
                    champion_games[game.champion]["wins"] += 1
        
        return {
            "player": player,
            "total_games": total_games,
            "wins": wins,
            "win_rate": win_rate,
            "champion_stats": champion_games
        }
    
    @staticmethod
    def get_all_champion_stats(db: Session, limit: int = 20):
        stats = db.query(ChampionStats).order_by(ChampionStats.win_rate.desc()).limit(limit).all()
        return [{"champion": s.champion, "win_rate": s.win_rate, "total_games": s.total_games,
                "avg_kills": s.avg_kills, "avg_deaths": s.avg_deaths, "avg_assists": s.avg_assists} 
               for s in stats]
    
    @staticmethod
    def get_recommendations(db: Session, enemy_champions: list = None):
        query = db.query(ChampionStats).order_by(ChampionStats.win_rate.desc())
        all_stats = query.all()
        
        recommendations = []
        for s in all_stats:
            if enemy_champions and s.champion in enemy_champions:
                continue
            recommendations.append({
                "champion": s.champion,
                "win_rate": round(s.win_rate * 100, 1),
                "games": s.total_games,
                "avg_kda": round((s.avg_kills + s.avg_assists) / max(s.avg_deaths, 1), 2)
            })
            if len(recommendations) >= 10:
                break
        
        return recommendations
