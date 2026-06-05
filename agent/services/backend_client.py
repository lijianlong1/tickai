"""
Java 后端 API 客户端
负责与 Java 后端通信，进行数据库读写
"""
import json
import logging
from typing import Dict, Any, Optional, List
import httpx

from ..core.config_loader import config

logger = logging.getLogger(__name__)


class BackendClient:
    """Java 后端 API 客户端"""

    def __init__(self):
        self.base_url = config.get("backend.base_url", "http://localhost:8080/api")
        self.timeout = config.get("backend.timeout", 30)
        self.token: Optional[str] = None
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    def set_token(self, token: str):
        """设置 JWT Token"""
        self.token = token

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def _request(
        self,
        method: str,
        path: str,
        params: Dict = None,
        json_data: Dict = None,
    ) -> Dict[str, Any]:
        """通用请求方法"""
        client = await self._get_client()
        url = f"{self.base_url}{path}"

        try:
            resp = await client.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                headers=self._headers(),
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as e:
            logger.error(f"后端请求失败: {method} {url} - {e}")
            return {"code": 500, "message": str(e), "data": None}

    # ============= 用户相关 =============

    async def register(self, username: str, email: str, password: str) -> Dict:
        return await self._request("POST", "/auth/register", json_data={
            "username": username, "email": email, "password": password
        })

    async def login(self, email: str, password: str) -> Dict:
        result = await self._request("POST", "/auth/login", json_data={
            "email": email, "password": password
        })
        if result.get("code") == 200 and result.get("data", {}).get("token"):
            self.set_token(result["data"]["token"])
        return result

    async def get_me(self) -> Dict:
        return await self._request("GET", "/auth/me")

    # ============= 社区作品 =============

    async def list_works(self, work_type: str = None, current: int = 1, size: int = 12) -> Dict:
        params = {"current": current, "size": size}
        if work_type:
            params["work_type"] = work_type
        return await self._request("GET", "/community/works/public", params=params)

    async def get_work(self, work_id: int) -> Dict:
        return await self._request("GET", f"/community/works/{work_id}/detail")

    async def create_work(self, work: Dict) -> Dict:
        return await self._request("POST", "/community/works", json_data=work)

    async def delete_work(self, work_id: int) -> Dict:
        return await self._request("DELETE", f"/community/works/{work_id}")

    async def my_works(self, current: int = 1, size: int = 12) -> Dict:
        return await self._request("GET", "/community/works/my", params={
            "current": current, "size": size
        })

    # ============= 提示词 =============

    async def list_prompts(self, category: str = None, current: int = 1, size: int = 12) -> Dict:
        params = {"current": current, "size": size}
        if category:
            params["category"] = category
        return await self._request("GET", "/community/prompts/public", params=params)

    async def get_prompts_by_work(self, work_id: int) -> Dict:
        return await self._request("GET", f"/community/prompts/work/{work_id}")

    async def create_prompt(self, prompt: Dict) -> Dict:
        return await self._request("POST", "/community/prompts", json_data=prompt)

    async def use_prompt(self, prompt_id: int) -> Dict:
        return await self._request("POST", f"/community/prompts/{prompt_id}/use")

    # ============= 创作历史 =============

    async def list_history(self, create_type: str = None, current: int = 1, size: int = 20) -> Dict:
        params = {"current": current, "size": size}
        if create_type:
            params["create_type"] = create_type
        return await self._request("GET", "/create/history", params=params)

    async def save_history(self, history: Dict) -> Dict:
        return await self._request("POST", "/create/history", json_data=history)

    # ============= 语音历史 =============

    async def list_voice_history(self, current: int = 1, size: int = 20) -> Dict:
        return await self._request("GET", "/voice/history", params={
            "current": current, "size": size
        })

    async def save_voice(self, voice: Dict) -> Dict:
        return await self._request("POST", "/voice/history", json_data=voice)

    async def delete_voice(self, voice_id: int) -> Dict:
        return await self._request("DELETE", f"/voice/history/{voice_id}")

    async def close(self):
        """关闭客户端"""
        if self._client:
            await self._client.aclose()
            self._client = None


# 全局客户端实例
backend_client = BackendClient()
