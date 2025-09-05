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
        with self.conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute("""
                SELECT id, name, last_check, last_status_code
                FROM urls
            """)
            rows = cur.fetchall()
        print(rows)
        return [URL(row) for row in rows]

    def find_by_name(self, name):
        with self.conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute("""
                SELECT id, name, last_check, last_status_code
                FROM urls
                WHERE name = %s;
                """,
                (name,)
            )
            data = cur.fetchone()
            return URL(data) if data else None

    def save(self, name):
        with self.conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute("""
                INSERT INTO urls
                VALUES (%s)
                RETURNING id, name, last_check, last_status_code
                """,
                (name,)
            )
            return URL(cur.fetchone())
        