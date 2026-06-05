"""
数据处理分析服务
对用户创作数据、社区数据进行分析
"""
import json
import logging
from collections import Counter
from datetime import datetime, timedelta
from typing import Dict, List, Any

from .backend_client import backend_client

logger = logging.getLogger(__name__)


class DataAnalyzer:
    """数据分析器"""

    async def analyze_user_behavior(self, user_id: int) -> Dict[str, Any]:
        """分析用户行为"""
        # 获取用户的创作历史
        history_result = await backend_client.list_history(current=1, size=1000)
        history_list = history_result.get("data", {}).get("records", [])

        # 获取用户的作品
        works_result = await backend_client.my_works(current=1, size=1000)
        works_list = works_result.get("data", {}).get("records", [])

        # 按类型统计
        type_counter = Counter(item.get("createType") for item in history_list)

        # 按时间统计（最近 7 天）
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        recent = []
        for item in history_list:
            created = item.get("createdAt", "")
            try:
                if created and datetime.fromisoformat(created.replace("Z", "")) > week_ago:
                    recent.append(item)
            except (ValueError, TypeError):
                continue

        # 计算消费
        total_cost = sum(float(item.get("cost", 0)) for item in history_list)

        return {
            "user_id": user_id,
            "total_creates": len(history_list),
            "total_works": len(works_list),
            "type_distribution": dict(type_counter),
            "recent_7days_creates": len(recent),
            "total_cost": round(total_cost, 2),
            "favorite_type": type_counter.most_common(1)[0][0] if type_counter else None,
            "analyzed_at": now.isoformat(),
        }

    async def analyze_community_trends(self) -> Dict[str, Any]:
        """分析社区趋势"""
        # 拉取所有公开作品
        all_works = []
        current = 1
        while True:
            result = await backend_client.list_works(current=current, size=100)
            records = result.get("data", {}).get("records", [])
            if not records:
                break
            all_works.extend(records)
            if len(records) < 100:
                break
            current += 1

        # 类型分布
        type_counter = Counter(w.get("workType") for w in all_works)

        # 热门标签
        all_tags = []
        for w in all_works:
            tags = w.get("tags", "")
            if tags:
                all_tags.extend([t.strip() for t in tags.split(",")])
        tag_counter = Counter(all_tags).most_common(20)

        # 总浏览数和点赞数
        total_views = sum(w.get("viewCount", 0) for w in all_works)
        total_likes = sum(w.get("likeCount", 0) for w in all_works)

        # 热门作品
        hot_works = sorted(all_works, key=lambda w: w.get("likeCount", 0), reverse=True)[:10]

        return {
            "total_works": len(all_works),
            "type_distribution": dict(type_counter),
            "hot_tags": [{"tag": t, "count": c} for t, c in tag_counter],
            "total_views": total_views,
            "total_likes": total_likes,
            "hot_works": [{"id": w["id"], "title": w["title"], "likes": w.get("likeCount", 0)} for w in hot_works],
            "analyzed_at": datetime.now().isoformat(),
        }

    async def generate_user_report(self, user_id: int) -> str:
        """生成用户报告（自然语言）"""
        behavior = await self.analyze_user_behavior(user_id)
        history_result = await backend_client.list_history(current=1, size=5)
        recent_works = history_result.get("data", {}).get("records", [])

        report_lines = [
            f"=== 用户 #{user_id} 创作报告 ===",
            f"总创作次数：{behavior['total_creates']}",
            f"总作品数：{behavior['total_works']}",
            f"近 7 天创作：{behavior['recent_7days_creates']} 次",
            f"累计消费：¥{behavior['total_cost']}",
            f"偏好创作类型：{behavior['favorite_type'] or '暂无数据'}",
            "",
            "=== 类型分布 ===",
        ]

        for t, count in sorted(behavior["type_distribution"].items(), key=lambda x: -x[1]):
            report_lines.append(f"  {t}: {count} 次")

        return "\n".join(report_lines)


# 全局分析器实例
data_analyzer = DataAnalyzer()
