from psycopg2.extras import NamedTupleCursor

class URL:
    def __init__(self, row):
        self.id = row.id
        self.name = row.name
        self.last_check = row.last_check
        self.last_status_code = row.last_status_code


class Check:
    def __init__(self, row):
        self.id = row.id
        self.url_id = row.url_id
        self.status_code = row.status_code
        self.h1 = row.h1
        self.title = row.title
        self.description = row.description
        self.created_at = row.created_at


class Repository:
    def __init__(self, conn):
        self.conn = conn
    
    def get_all_urls(self):
        with self.conn, self.conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute("""
                SELECT id, name, last_check, last_status_code
                FROM urls
                ORDER BY id DESC;
            """)
            return [URL(row) for row in cur.fetchall()]

    def get_all_checks(self, url_id):
        with self.conn, self.conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute("""
                SELECT id, url_id, status_code, h1,
                       title, description, created_at
                FROM url_checks
                WHERE url_id = %s
                ORDER BY id DESC;
                """,
                (url_id,)
            )
            return [Check(row) for row in cur.fetchall()]

    def save_url(self, name):
        with self.conn, self.conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute("""
                INSERT INTO urls (name) VALUES (%s)
                RETURNING id, name, created_at, last_check, last_status_code;
                """,
                (name,)
            )
            return URL(cur.fetchone())

    def save_check(self, url_id, status_code, h1, title, description):
        with self.conn, self.conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute("""
                INSERT INTO url_checks
                    (url_id, status_code, h1, title, description)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, url_id, status_code, h1, title, description, created_at;
                """,
                (url_id, status_code, h1, title, description)
            )
            return Check(cur.fetchone())

    def find_url_by_name(self, name):
        with self.conn, self.conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute("""
                SELECT id, name, last_check, last_status_code
                FROM urls
                WHERE name = %s;
                """,
                (name,)
            )
            data = cur.fetchone()
            return URL(data) if data else None
    
    def find_url_by_id(self, url_id):
        with self.conn, self.conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute("""
                SELECT id, name, last_check, last_status_code
                FROM urls
                WHERE id = %s;
                """,
                (url_id,)
            )
            return URL(cur.fetchone())

    
        
    def update_url(self, url):
        with self.conn, self.conn.cursor() as cur:
            cur.execute("""
                UPDATE urls
                SET name = %s, last_check = %s, last_status_code = %s
                WHERE id = %s;
                """,
                (url.name, url.last_check, url.last_status_code, url.id)
            )
        return None
