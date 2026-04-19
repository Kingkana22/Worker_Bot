from __future__ import annotations

from typing import Sequence

from core.task_models import JobPosting
from integrations.upwork_api import UpworkAPI


class FreelanceScoutAgent:
    def __init__(self, upwork_api: UpworkAPI) -> None:
        self.upwork_api = upwork_api

    async def find_jobs(self, keywords: Sequence[str], limit: int) -> list[JobPosting]:
        jobs = await self.upwork_api.search_jobs(keywords=keywords, limit=limit)
        normalized_keywords = {k.lower() for k in keywords}
        for job in jobs:
            haystack = f"{job.title} {job.description}".lower()
            job.matched_keywords = [k for k in normalized_keywords if k in haystack]
        return jobs
