"""
配置加载器
支持 YAML 配置文件 + 环境变量替换
"""
import os
import re
import yaml
from pathlib import Path
from typing import Any, Dict


class ConfigLoader:
    """配置加载器单例"""

    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self, config_path: str = None) -> Dict[str, Any]:
        """加载配置文件"""
        if self._config is not None:
            return self._config

        if config_path is None:
            config_path = Path(__file__).parent.parent / "configs" / "config.yaml"

        with open(config_path, "r", encoding="utf-8") as f:
            raw = f.read()

        # 替换 ${ENV_VAR} 占位符
        raw = self._replace_env_vars(raw)

        self._config = yaml.safe_load(raw)
        return self._config

    def _replace_env_vars(self, text: str) -> str:
        """替换 ${VAR} 形式的环境变量"""
        pattern = re.compile(r'\$\{([A-Z_][A-Z0-9_]*)\}')

        def replacer(match):
            var_name = match.group(1)
            return os.environ.get(var_name, match.group(0))

        return pattern.sub(replacer, text)

    def get(self, key: str, default: Any = None) -> Any:
        """通过点号路径获取配置"""
        if self._config is None:
            self.load()

        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value


# 全局配置实例
config = ConfigLoader()
