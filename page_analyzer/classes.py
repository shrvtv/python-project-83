import datetime
from dataclasses import dataclass
from typing import Final

import page_analyzer.utils as utils


@dataclass(slots=True)
class URL:
    """Dataclass for storing URL data."""
    id: Final[int]
    name: Final[str]
    created_at: Final[datetime.date]
    last_check: datetime.date
    last_status_code: int


@dataclass(frozen=True, slots=True)
class Check:
    """Immutable dataclass for storing results of a URL check."""
    id: int
    url_id: int
    status_code: int
    h1: str | None
    title: str | None
    description: str | None
    created_at: datetime.date


class Repository:
    """Abstraction for interaction with tables 'urls' and 'url_checks'
    in a specified database. Relies on connection and DictCursor provided by
    dict_cursor function from 'utils' module.
    """
    def __init__(self, dsn: str) -> None:
        """Create a Repository object with a specific Data Source Name
        for connecting to a database.
        """
        self.dsn: Final[str] = dsn
    
    def get_all_urls(self) -> list[URL]:
        """Extract all URLs data from the 'urls' table."""
        with utils.dict_cursor(self.dsn) as cur:
            cur.execute("""
                SELECT id, name, created_at, last_check, last_status_code
                FROM urls
                ORDER BY id DESC;
            """)
            return [URL(**row) for row in cur.fetchall()]

    def get_all_checks(self, url_id: int) -> list[Check]:
        """Extract all URL checks data from the 'url_checks' table."""
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
        """Save a URL to the 'urls' table and return a URL object."""
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
        """Save url check data to the 'url_checks' table and
        return a Check object.
        """
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
        """Find a URL in the 'urls' table by the former's name and
        return a URL object if such an entry exists or None if it doesn't.
        """
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
        """Find a URL in the 'urls' table by the former's id and
        return a URL object if such an entry exists or None if it doesn't.
        """
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
        """Update a URL in the 'urls' table with data from last check."""
        with utils.dict_cursor(self.dsn) as cur:
            cur.execute("""
                UPDATE urls
                SET last_check = %s, last_status_code = %s
                WHERE id = %s;
                """,
                (url.last_check, url.last_status_code, url.id)
            )
