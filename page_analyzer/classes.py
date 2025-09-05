from psycopg2.extras import NamedTupleCursor

class URL:
    def __init__(self, row):
        self.id = row.id
        self.name = row.name
        self.last_check = row.last_check
        self.last_status_code = row.last_status_code

class URLRepository:
    def __init__(self, conn):
        self.conn = conn
    
    def get_all_urls(self):
        with self.conn, self.conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute("""
                SELECT id, name, last_check, last_status_code
                FROM urls
                ORDER BY id DESC;
            """)
            rows = cur.fetchall()
        return [URL(row) for row in rows]

    def find_by_name(self, name):
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
    
    def find_by_id(self, url_id):
        with self.conn, self.conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute("""
                SELECT id, name, last_check, last_status_code
                FROM urls
                WHERE id = %s;
                """,
                (url_id,)
            )
            return URL(cur.fetchone())

    def save(self, name):
        with self.conn, self.conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute("""
                INSERT INTO urls (name) VALUES (%s)
                RETURNING id, name, created_at, last_check, last_status_code;
                """,
                (name,)
            )
            return URL(cur.fetchone())
        
    def update(self, url):
        with self.conn, self.conn.cursor() as cur:
            cur.execute("""
                UPDATE urls
                SET name = %s, last_check = %s, last_status_code = %s
                WHERE id = %s;
                """,
                (url.name, url.last_check, url.last_status_code, url.id)
            )
        return None
