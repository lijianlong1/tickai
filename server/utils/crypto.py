"""
加密工具

用于 API Key 加密存储和解密使用。
基于 cryptography.fernet（对称加密）。
"""
import os
import base64
import hashlib
import logging
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


# 固定的开发密钥（生产环境必须从环境变量覆盖）
DEV_KEY = "ZGV2LWtleS0xMjM0NTY3ODkwYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXo="


def _get_fernet() -> Fernet:
    """
    获取 Fernet 加密器

    密钥优先级：
    1. 环境变量 API_KEY_ENCRYPTION_KEY
    2. 派生的开发密钥（基于 SECRET_KEY 或默认值）
    """
    key = os.getenv("API_KEY_ENCRYPTION_KEY")
    if not key:
        # 尝试从 SECRET_KEY 派生
        secret = os.getenv("JWT_SECRET", "tick-ai-secret-key")
        # 使用 SHA256 派生一个 32 字节的 key
        derived = hashlib.sha256(secret.encode()).digest()
        key = base64.urlsafe_b64encode(derived).decode()

    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_api_key(plain_key: str) -> str:
    """
    加密 API Key

    Args:
        plain_key: 明文 API Key

    Returns:
        加密后的字符串（base64 编码）
    """
    if not plain_key:
        return ""
    try:
        fernet = _get_fernet()
        return fernet.encrypt(plain_key.encode()).decode()
    except Exception as e:
        logger.error(f"加密 API Key 失败: {e}")
        raise


def decrypt_api_key(encrypted_key: str) -> str:
    """
    解密 API Key

    Args:
        encrypted_key: 加密的字符串

    Returns:
        明文 API Key
    """
    if not encrypted_key:
        return ""
    try:
        fernet = _get_fernet()
        return fernet.decrypt(encrypted_key.encode()).decode()
    except Exception as e:
        logger.error(f"解密 API Key 失败: {e}")
        return ""
