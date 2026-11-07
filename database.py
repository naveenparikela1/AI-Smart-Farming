import os
import sqlite3
import hashlib
import hmac
import secrets
from pathlib import Path

DB_PATH = Path(os.environ.get("SMARTFARM_DB", Path(__file__).with_name("smartfarm.db")))

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with connect() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            language TEXT NOT NULL DEFAULT 'English',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS farms(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name TEXT NOT NULL, village TEXT, area REAL NOT NULL CHECK(area > 0),
            soil TEXT NOT NULL, irrigation TEXT NOT NULL,
            latitude REAL, longitude REAL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS crops(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            farm_id INTEGER NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
            crop TEXT NOT NULL, variety TEXT, area REAL NOT NULL CHECK(area > 0),
            stage TEXT NOT NULL, planting_date TEXT NOT NULL, expected_harvest TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS expenses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            crop_id INTEGER REFERENCES crops(id) ON DELETE SET NULL,
            category TEXT NOT NULL, amount REAL NOT NULL CHECK(amount >= 0),
            spent_on TEXT NOT NULL, description TEXT
        );
        CREATE TABLE IF NOT EXISTS activities(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            crop_id INTEGER REFERENCES crops(id) ON DELETE SET NULL,
            activity_type TEXT NOT NULL, activity_date TEXT NOT NULL, notes TEXT
        );
        CREATE TABLE IF NOT EXISTS harvests(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            crop_id INTEGER NOT NULL REFERENCES crops(id) ON DELETE CASCADE,
            quantity_kg REAL NOT NULL CHECK(quantity_kg > 0),
            grade TEXT, harvest_date TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sales(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            crop_id INTEGER NOT NULL REFERENCES crops(id) ON DELETE CASCADE,
            quantity_kg REAL NOT NULL CHECK(quantity_kg > 0),
            price_per_quintal REAL NOT NULL CHECK(price_per_quintal >= 0),
            buyer TEXT, market TEXT, transport_cost REAL NOT NULL DEFAULT 0,
            other_cost REAL NOT NULL DEFAULT 0, sale_date TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS reminders(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title TEXT NOT NULL, category TEXT NOT NULL, due_date TEXT NOT NULL,
            is_done INTEGER NOT NULL DEFAULT 0
        );
        CREATE INDEX IF NOT EXISTS idx_farms_user ON farms(user_id);
        CREATE INDEX IF NOT EXISTS idx_crops_user ON crops(user_id);
        CREATE INDEX IF NOT EXISTS idx_expenses_user ON expenses(user_id);
        CREATE INDEX IF NOT EXISTS idx_reminders_user ON reminders(user_id);
        """)
        # Backward-compatible migration for existing SQLite databases.
        farm_columns = {row[1] for row in c.execute("PRAGMA table_info(farms)").fetchall()}
        if "latitude" not in farm_columns:
            c.execute("ALTER TABLE farms ADD COLUMN latitude REAL")
        if "longitude" not in farm_columns:
            c.execute("ALTER TABLE farms ADD COLUMN longitude REAL")

def _hash(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 240000).hex()

def create_user(name, phone, password):
    salt=secrets.token_hex(16)
    try:
        with connect() as c:
            c.execute("INSERT INTO users(name,phone,password_hash,salt) VALUES(?,?,?,?)",
                      (name,phone,_hash(password,salt),salt))
        return True, "Account created"
    except sqlite3.IntegrityError:
        return False, "phone_exists"

def authenticate(phone,password):
    with connect() as c:
        row=c.execute("SELECT * FROM users WHERE phone=?",(phone,)).fetchone()
    if not row or not hmac.compare_digest(row["password_hash"],_hash(password,row["salt"])):
        return None
    return dict(row)

def get_user(uid):
    with connect() as c:
        row=c.execute("SELECT id,name,phone,language FROM users WHERE id=?",(uid,)).fetchone()
    return dict(row) if row else None

def update_profile(uid,name,language):
    with connect() as c:
        c.execute("UPDATE users SET name=?,language=? WHERE id=?",(name,language,uid))

def _rows(sql,args=()):
    with connect() as c:
        return [dict(r) for r in c.execute(sql,args).fetchall()]

def _exec(sql,args=()):
    with connect() as c:
        cur=c.execute(sql,args)
        return cur.lastrowid

def list_farms(uid):
    return _rows("SELECT * FROM farms WHERE user_id=? ORDER BY id DESC",(uid,))
def add_farm(uid,name,village,area,soil,irrigation,latitude=None,longitude=None):
    return _exec("INSERT INTO farms(user_id,name,village,area,soil,irrigation,latitude,longitude) VALUES(?,?,?,?,?,?,?,?)",
                 (uid,name,village,area,soil,irrigation,latitude,longitude))
def delete_farm(uid,rid):
    return _exec("DELETE FROM farms WHERE user_id=? AND id=?",(uid,rid))

def list_crops(uid):
    return _rows("""SELECT c.*,f.name AS farm_name FROM crops c JOIN farms f ON f.id=c.farm_id
                    WHERE c.user_id=? ORDER BY c.id DESC""",(uid,))
def add_crop(uid,farm_id,crop,variety,area,stage,planting,expected):
    return _exec("""INSERT INTO crops(user_id,farm_id,crop,variety,area,stage,planting_date,expected_harvest)
                    SELECT ?,id,?,?,?,?,?,? FROM farms WHERE id=? AND user_id=?""",
                 (uid,crop,variety,area,stage,planting,expected,farm_id,uid))
def delete_crop(uid,rid):
    return _exec("DELETE FROM crops WHERE user_id=? AND id=?",(uid,rid))

def list_expenses(uid):
    return _rows("""SELECT e.*,c.crop AS crop_name FROM expenses e LEFT JOIN crops c ON c.id=e.crop_id
                    WHERE e.user_id=? ORDER BY e.spent_on DESC,e.id DESC""",(uid,))
def add_expense(uid,category,amount,spent,description,crop_id):
    return _exec("INSERT INTO expenses(user_id,category,amount,spent_on,description,crop_id) VALUES(?,?,?,?,?,?)",
                 (uid,category,amount,spent,description,crop_id))
def delete_expense(uid,rid):
    return _exec("DELETE FROM expenses WHERE user_id=? AND id=?",(uid,rid))

def list_activities(uid):
    return _rows("""SELECT a.*,c.crop AS crop_name FROM activities a LEFT JOIN crops c ON c.id=a.crop_id
                    WHERE a.user_id=? ORDER BY a.activity_date DESC""",(uid,))
def add_activity(uid,typ,d,notes,crop_id):
    return _exec("INSERT INTO activities(user_id,activity_type,activity_date,notes,crop_id) VALUES(?,?,?,?,?)",(uid,typ,d,notes,crop_id))
def delete_activity(uid,rid):
    return _exec("DELETE FROM activities WHERE user_id=? AND id=?",(uid,rid))

def list_harvests(uid):
    return _rows("""SELECT h.*,c.crop AS crop_name FROM harvests h JOIN crops c ON c.id=h.crop_id
                    WHERE h.user_id=? ORDER BY h.harvest_date DESC""",(uid,))
def add_harvest(uid,crop_id,qty,grade,d):
    return _exec("INSERT INTO harvests(user_id,crop_id,quantity_kg,grade,harvest_date) VALUES(?,?,?,?,?)",(uid,crop_id,qty,grade,d))
def delete_harvest(uid,rid):
    return _exec("DELETE FROM harvests WHERE user_id=? AND id=?",(uid,rid))

def list_sales(uid):
    return _rows("""SELECT s.*,c.crop AS crop_name FROM sales s JOIN crops c ON c.id=s.crop_id
                    WHERE s.user_id=? ORDER BY s.sale_date DESC""",(uid,))
def add_sale(uid,crop_id,qty,price,buyer,market,transport,other,d):
    return _exec("""INSERT INTO sales(user_id,crop_id,quantity_kg,price_per_quintal,buyer,market,transport_cost,other_cost,sale_date)
                    VALUES(?,?,?,?,?,?,?,?,?)""",(uid,crop_id,qty,price,buyer,market,transport,other,d))
def delete_sale(uid,rid):
    return _exec("DELETE FROM sales WHERE user_id=? AND id=?",(uid,rid))

def list_reminders(uid):
    return _rows("SELECT * FROM reminders WHERE user_id=? ORDER BY is_done,due_date",(uid,))
def add_reminder(uid,title,category,due):
    return _exec("INSERT INTO reminders(user_id,title,category,due_date) VALUES(?,?,?,?)",(uid,title,category,due))
def complete_reminder(uid,rid):
    return _exec("UPDATE reminders SET is_done=1 WHERE user_id=? AND id=?",(uid,rid))
def delete_reminder(uid,rid):
    return _exec("DELETE FROM reminders WHERE user_id=? AND id=?",(uid,rid))

def dashboard_totals(uid):
    with connect() as c:
        area=c.execute("SELECT COALESCE(SUM(area),0) FROM farms WHERE user_id=?",(uid,)).fetchone()[0]
        active=c.execute("SELECT COUNT(*) FROM crops WHERE user_id=?",(uid,)).fetchone()[0]
        expenses=c.execute("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE user_id=?",(uid,)).fetchone()[0]
        harvest=c.execute("SELECT COALESCE(SUM(quantity_kg),0) FROM harvests WHERE user_id=?",(uid,)).fetchone()[0]
        sales=c.execute("SELECT COALESCE(SUM(quantity_kg*price_per_quintal/100),0) FROM sales WHERE user_id=?",(uid,)).fetchone()[0]
        costs=c.execute("SELECT COALESCE(SUM(transport_cost+other_cost),0) FROM sales WHERE user_id=?",(uid,)).fetchone()[0]
        pending=c.execute("SELECT COUNT(*) FROM reminders WHERE user_id=? AND is_done=0",(uid,)).fetchone()[0]
    return {"area":area,"active_crops":active,"expenses":expenses,"harvest_kg":harvest,
            "revenue":sales,"selling_costs":costs,"profit":sales-expenses-costs,"pending_reminders":pending}
