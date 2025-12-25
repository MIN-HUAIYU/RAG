"""
DeepSeek API 服务模块
支持流式和非流式调用
"""

import json
import httpx
from typing import AsyncGenerator, Generator
from loguru import logger


class DeepSeekService:
    """DeepSeek API 服务类"""

    def __init__(self, api_key: str, api_url: str, model: str):
        """
        初始化 DeepSeek 服务

        Args:
            api_key: DeepSeek API 密钥
            api_url: API 端点 URL
            model: 模型名称 (如 "deepseek-chat")
        """
        self.api_key = api_key
        self.api_url = api_url
        self.model = model
        self.timeout = 60.0

        # 请求头配置
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        logger.info(f"DeepSeek 服务已初始化: {model}")

    def _build_payload(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False,
    ) -> dict:
        """
        构建 API 请求 payload

        Args:
            prompt: 用户提示
            system_prompt: 系统提示
            temperature: 温度参数 (0-2)
            max_tokens: 最大令牌数
            stream: 是否流式传输

        Returns:
            请求 payload 字典
        """
        messages = []

        # 添加系统提示
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # 添加用户提示
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        return payload

    def stream_chat(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        retry: int = 3,
    ) -> Generator[str, None, None]:
        """
        流式调用 DeepSeek API

        Args:
            prompt: 用户提示
            system_prompt: 系统提示
            temperature: 温度参数
            max_tokens: 最大令牌数
            retry: 重试次数（用于处理 DNS 失败）

        Yields:
            流式返回的文本片段

        Example:
            for chunk in service.stream_chat("你好"):
                print(chunk, end="", flush=True)
        """
        payload = self._build_payload(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        last_error = None
        for attempt in range(retry):
            try:
                with httpx.stream(
                    "POST",
                    self.api_url + "/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=self.timeout,
                ) as response:
                    response.raise_for_status()

                    for line in response.iter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]  # 移除 "data: " 前缀

                            if data_str == "[DONE]":
                                logger.debug("流式响应结束")
                                break

                            try:
                                data = json.loads(data_str)
                                if "choices" in data and len(data["choices"]) > 0:
                                    choice = data["choices"][0]
                                    if "delta" in choice:
                                        content = choice["delta"].get("content", "")
                                        if content:
                                            yield content
                            except json.JSONDecodeError as e:
                                logger.warning(f"JSON 解析失败: {e}")
                                continue
                return  # 成功完成，退出函数

            except (httpx.ConnectError, OSError) as e:
                last_error = e
                if attempt < retry - 1:
                    logger.warning(f"连接失败（尝试 {attempt + 1}/{retry}）: {e}")
                    import time
                    time.sleep(1)  # 等待 1 秒后重试
                    continue
                else:
                    logger.error(f"API 请求失败（已重试 {retry} 次）: {e}")
                    raise
            except httpx.HTTPStatusError as e:
                logger.error(f"API 返回错误: {e.response.status_code} - {e.response.text}")
                raise
            except httpx.RequestError as e:
                logger.error(f"API 请求失败: {e}")
                raise

    def sync_chat(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        同步调用 DeepSeek API（非流式）

        Args:
            prompt: 用户提示
            system_prompt: 系统提示
            temperature: 温度参数
            max_tokens: 最大令牌数

        Returns:
            完整的回复文本

        Example:
            response = service.sync_chat("你好")
            print(response)
        """
        payload = self._build_payload(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
        )

        try:
            response = httpx.post(
                self.api_url + "/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()

            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            else:
                raise ValueError("API 响应格式错误")

        except httpx.RequestError as e:
            logger.error(f"API 请求失败: {e}")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"API 返回错误: {e.response.status_code} - {e.response.text}")
            raise

    async def async_stream_chat(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> AsyncGenerator[str, None]:
        """
        异步流式调用 DeepSeek API（高级用法）

        Args:
            prompt: 用户提示
            system_prompt: 系统提示
            temperature: 温度参数
            max_tokens: 最大令牌数

        Yields:
            流式返回的文本片段

        Example:
            async for chunk in service.async_stream_chat("你好"):
                print(chunk, end="", flush=True)
        """
        payload = self._build_payload(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    self.api_url + "/chat/completions",
                    headers=self.headers,
                    json=payload,
                ) as response:
                    response.raise_for_status()

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]

                            if data_str == "[DONE]":
                                break

                            try:
                                data = json.loads(data_str)
                                if "choices" in data and len(data["choices"]) > 0:
                                    choice = data["choices"][0]
                                    if "delta" in choice:
                                        content = choice["delta"].get("content", "")
                                        if content:
                                            yield content
                            except json.JSONDecodeError:
                                continue

        except httpx.RequestError as e:
            logger.error(f"异步 API 请求失败: {e}")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"异步 API 返回错误: {e.response.status_code}")
            raise
