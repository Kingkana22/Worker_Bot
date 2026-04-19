from __future__ import annotations

from typing import Any

import aiohttp


class HackerOneAPI:
    def __init__(self, base_url: str, username: str, token: str) -> None:
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.token = token

    async def fetch_program_scope(self, program_handle: str) -> list[str]:
        if not self.username or not self.token:
            return []

        url = f'{self.base_url}/v1/hackers/programs/{program_handle}/structured_scopes'
        auth = aiohttp.BasicAuth(login=self.username, password=self.token)

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            async with session.get(url, auth=auth) as response:
                if response.status >= 400:
                    return []
                payload: dict[str, Any] = await response.json(content_type=None)

        scopes: list[str] = []
        for item in payload.get('data', []):
            attributes = item.get('attributes', {})
            asset_identifier = attributes.get('asset_identifier')
            if asset_identifier:
                scopes.append(str(asset_identifier))
        return scopes
