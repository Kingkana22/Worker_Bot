from __future__ import annotations

from typing import Any

import aiohttp


class BugcrowdAPI:
    def __init__(self, base_url: str, api_token: str) -> None:
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token

    async def fetch_program_scope(self, program_code: str) -> list[str]:
        if not self.api_token:
            return []

        url = f'{self.base_url}/programs/{program_code}/scope'
        headers = {'Authorization': f'Token {self.api_token}'}

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            async with session.get(url, headers=headers) as response:
                if response.status >= 400:
                    return []
                payload: dict[str, Any] = await response.json(content_type=None)

        scopes: list[str] = []
        for item in payload.get('targets', []):
            target = item.get('name') or item.get('target')
            if target:
                scopes.append(str(target))
        return scopes
