"""SQLite history storage."""
import csv, io, os, sqlite3
from contextlib import contextmanager
from datetime import datetime
from .config import DB_PATH


@contextmanager
def _conn(path=None):
    path = path or DB_PATH
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    c = sqlite3.connect(path)
    c.row_factory = sqlite3.Row
    try:
        yield c
        c.commit()
    finally:
        c.close()


def init_db(path=None):
    with _conn(path) as c:
        c.execute("""CREATE TABLE IF NOT EXISTS history(
            id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, kind TEXT,
            src TEXT, tgt TEXT, source_text TEXT, result_text TEXT, tone TEXT)""")


def add(kind, src, tgt, source_text, result_text, tone="", path=None):
    with _conn(path) as c:
        c.execute("INSERT INTO history(ts,kind,src,tgt,source_text,result_text,tone) VALUES(?,?,?,?,?,?,?)",
                  (datetime.now().strftime("%Y-%m-%d %H:%M"), kind, src, tgt, source_text, result_text, tone))


def fetch(search="", kind="All", limit=200, path=None):
    q, args = "SELECT * FROM history WHERE 1=1", []
    if search:
        q += " AND (source_text LIKE ? OR result_text LIKE ?)"
        args += [f"%{search}%"] * 2
    if kind != "All":
        q += " AND kind=?"
        args.append(kind)
    q += " ORDER BY id DESC LIMIT ?"
    args.append(limit)
    with _conn(path) as c:
        return [dict(r) for r in c.execute(q, args)]


def delete(row_id, path=None):
    with _conn(path) as c:
        c.execute("DELETE FROM history WHERE id=?", (row_id,))


def clear(path=None):
    with _conn(path) as c:
        c.execute("DELETE FROM history")


def stats(path=None):
    with _conn(path) as c:
        total = c.execute("SELECT COUNT(*) FROM history").fetchone()[0]
        langs = c.execute("SELECT COUNT(DISTINCT tgt) FROM history").fetchone()[0]
        top = c.execute("SELECT tgt, COUNT(*) n FROM history GROUP BY tgt ORDER BY n DESC LIMIT 1").fetchone()
    return {"total": total, "langs": langs, "top": top["tgt"] if top else "-"}


def to_csv(rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=["id", "ts", "kind", "src", "tgt", "source_text", "result_text", "tone"])
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()
