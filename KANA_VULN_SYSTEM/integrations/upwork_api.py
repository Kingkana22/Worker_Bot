from __future__ import annotations

from datetime import datetime, timezone
from typing import Sequence

import aiohttp

from core.task_models import JobPosting


class UpworkAPI:
    def __init__(self, base_url: str, api_token: str) -> None:
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token

    async def search_jobs(self, keywords: Sequence[str], limit: int = 25) -> list[JobPosting]:
        if not self.api_token:
            return []

        query = ' OR '.join(keywords)
        url = f'{self.base_url}/profiles/v2/search/jobs'
        headers = {'Authorization': f'Bearer {self.api_token}'}
        params = {'q': query, 'paging': f'0;{limit}', 'sort': 'recency'}

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status >= 400:
                    return []
                payload = await response.json(content_type=None)

        jobs: list[JobPosting] = []
        for item in payload.get('jobs', []):
            jobs.append(
                JobPosting(
                    source='upwork',
                    remote_id=str(item.get('uid', '')),
                    title=str(item.get('title', '')),
                    url=str(item.get('url', '')),
                    budget=str(item.get('budget', item.get('hourly_budget', 'N/A'))),
                    description=str(item.get('snippet', '')),
                    posted_at=datetime.now(timezone.utc),
                )
            )
        return jobs
