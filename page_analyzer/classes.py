import datetime
from dataclasses import dataclass
from typing import Final

import page_analyzer.utils as utils


@dataclass(slots=True)
class URL:
    id: Final[int]
    name: Final[str]
    created_at: Final[datetime.date]
    last_check: datetime.date
    last_status_code: int


@dataclass(frozen=True, slots=True)
class Check:
    id: int
    url_id: int
    status_code: int
    h1: str | None
    title: str | None
    description: str | None
    created_at: datetime.date


class Repository:
    def __init__(self, dsn: str) -> None:
        self.dsn: Final[str] = dsn
    
    def get_all_urls(self) -> list[URL]:
        with utils.dict_cursor(self.dsn) as cur:
            cur.execute("""
                SELECT id, name, created_at, last_check, last_status_code
                FROM urls
                ORDER BY id DESC;
            """)
            return [URL(**row) for row in cur.fetchall()]

    def get_all_checks(self, url_id: int) -> list[Check]:
        with utils.dict_cursor(self.dsn) as cur:
            cur.execute("""
                SELECT id, url_id, status_code, h1,
                       title, description, created_at
                FROM url_checks
                WHERE url_id = %s
                ORDER BY id DESC;
                """,
                (url_id,)
            )
            return [Check(**row) for row in cur.fetchall()]

    def save_url(self, name: str) -> URL:
        with utils.dict_cursor(self.dsn) as cur:
            cur.execute("""
                INSERT INTO urls (name) VALUES (%s)
                RETURNING id, name, created_at, last_check, last_status_code;
                """,
                (name,)
            )
            return URL(**cur.fetchone())

    def save_check(
        self,
        url_id: int,
        status_code: int,
        h1: str | None,
        title: str | None,
        description: str | None
    ) -> Check:
        with utils.dict_cursor(self.dsn) as cur:
            cur.execute("""
                INSERT INTO url_checks
                    (url_id, status_code, h1, title, description)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, url_id, status_code, h1,
                          title, description, created_at;
                """,
                (url_id, status_code, h1, title, description)
            )
            return Check(**cur.fetchone())

    def find_url_by_name(self, name: str) -> URL | None:
        with utils.dict_cursor(self.dsn) as cur:
            cur.execute("""
                SELECT id, name, created_at, last_check, last_status_code
                FROM urls
                WHERE name = %s;
                """,
                (name,)
            )
            data = cur.fetchone()
            return URL(**data) if data else None
    
    def find_url_by_id(self, url_id: int) -> URL | None:
        with utils.dict_cursor(self.dsn) as cur:
            cur.execute("""
                SELECT id, name, created_at, last_check, last_status_code
                FROM urls
                WHERE id = %s;
                """,
                (url_id,)
            )
            data = cur.fetchone()
            return URL(**data) if data else None
        
    def update_url(self, url: URL) -> None:
        with utils.dict_cursor(self.dsn) as cur:
            cur.execute("""
                UPDATE urls
                SET name = %s, last_check = %s, last_status_code = %s
                WHERE id = %s;
                """,
                (url.name, url.last_check, url.last_status_code, url.id)
            )
