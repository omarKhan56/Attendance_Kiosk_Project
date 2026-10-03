"""SQLite queue: records are stored here when the network/backend is down, then synced later."""
import sqlite3, json, threading
class OfflineQueue:
    def __init__(self, path):
        self.path=path; self.lock=threading.Lock()
        with self._c() as c: c.execute("CREATE TABLE IF NOT EXISTS q(id INTEGER PRIMARY KEY AUTOINCREMENT, payload TEXT NOT NULL)")
    def _c(self): return sqlite3.connect(self.path)
    def push(self, payload):
        with self.lock, self._c() as c: c.execute("INSERT INTO q(payload) VALUES(?)",(json.dumps(payload),))
    def pending(self):
        with self.lock, self._c() as c: return [(i,json.loads(p)) for i,p in c.execute("SELECT id,payload FROM q ORDER BY id")]
    def remove(self, i):
        with self.lock, self._c() as c: c.execute("DELETE FROM q WHERE id=?",(i,))
    def size(self):
        with self.lock, self._c() as c: return c.execute("SELECT COUNT(*) FROM q").fetchone()[0]
