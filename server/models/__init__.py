"""
数据库模型集合
"""
from .user import User
from .work import Work
from .prompt import Prompt
from .create_history import CreateHistory
from .voice_history import VoiceHistory
from .recharge_record import RechargeRecord
from .consume_record import ConsumeRecord
from .work_like import WorkLike
from .work_comment import WorkComment
from .favorite import Favorite

__all__ = [
    "User",
    "Work",
    "Prompt",
    "CreateHistory",
    "VoiceHistory",
    "RechargeRecord",
    "ConsumeRecord",
    "WorkLike",
    "WorkComment",
    "Favorite",
]
