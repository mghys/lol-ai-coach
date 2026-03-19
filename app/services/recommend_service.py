from app.services.data_service import DataService
from config import CHAMPION_LIST
import random

class RecommendService:
    @staticmethod
    def get_best_compositions(db, enemy_team: list = None, ally_team: list = None):
        all_champions = DataService.get_all_champion_stats(db)
        
        if not all_champions:
            return RecommendService._get_default_recommendations()
        
        compositions = []
        used = set()
        
        if enemy_team:
            used.update(enemy_team)
        if ally_team:
            used.update(ally_team)
        
        top_champs = [c for c in all_champions if c["champion"] not in used]
        
        for i in range(min(5, len(top_champs))):
            champ = top_champs[i]
            compositions.append({
                "role": "核心carry",
                "champion": champ["champion"],
                "win_rate": champ["win_rate"],
                "reason": f"当前数据胜率最高的英雄，{champ['total_games']}场胜率{champ['win_rate']*100:.1f}%"
            })
        
        for champ in top_champs[5:10]:
            if champ["champion"] not in used:
                compositions.append({
                    "role": "优质选择",
                    "champion": champ["champion"],
                    "win_rate": champ["win_rate"],
                    "reason": f"高胜率英雄，适合当前对局"
                })
                if len(compositions) >= 10:
                    break
        
        return compositions
    
    @staticmethod
    def _get_default_recommendations():
        default_champs = [
            ("Kai'Sa", "高爆发AD", 52.5),
            ("Jinx", "持续输出", 51.8),
            ("Aphelios", "后期大核", 52.1),
            ("Ezreal", "灵活位移", 51.2),
            ("Miss Fortune", "超高爆发", 53.0),
            ("Senna", "输出辅助", 52.8),
            ("Vayne", "坦克杀手", 51.5),
            ("Lucian", "对线强势", 50.8),
            ("Tristana", "后期carry", 51.0),
            ("Caitlyn", "手长优势", 50.5),
        ]
        
        return [
            {
                "role": "推荐英雄" if i < 3 else "备选英雄",
                "champion": c[0],
                "win_rate": c[2],
                "reason": c[1]
            }
            for i, c in enumerate(default_champs)
        ]
    
    @staticmethod
    def analyze_team_composition(db, team: list):
        if not team:
            return {"strength": "未知", "suggestions": []}
        
        stats = []
        for champ in team:
            champ_stats = [c for c in DataService.get_all_champion_stats(db, 200) 
                          if c["champion"].lower() == champ.lower()]
            if champ_stats:
                stats.append(champ_stats[0])
        
        if not stats:
            return {"strength": "数据不足", "suggestions": ["暂无历史数据"]}
        
        avg_win_rate = sum(s["win_rate"] for s in stats) / len(stats)
        
        strength = "较强" if avg_win_rate > 0.52 else "一般" if avg_win_rate > 0.48 else "较弱"
        
        suggestions = []
        for champ in team:
            champ_lower = champ.lower()
            if any(c["champion"].lower() == champ_lower for c in stats):
                continue
            suggestions.append(f"考虑更换 {champ}")
        
        return {
            "strength": strength,
            "avg_win_rate": round(avg_win_rate * 100, 1),
            "suggestions": suggestions if suggestions else ["阵容合理"]
        }
