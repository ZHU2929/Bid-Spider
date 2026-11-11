# models.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class BidItem:
    title: str
    url: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    site_name: str


class SiteUnreachable(Exception):
    """网站无法正常访问时抛出"""
    pass