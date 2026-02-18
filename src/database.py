import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "social_dex.db"
CONFIG_PATH = Path(__file__).parent.parent / "data" / "config.json"

def init_db():
    """初始化数据库"""
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 作者表
    c.execute('''
        CREATE TABLE IF NOT EXISTS authors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            uid TEXT NOT NULL,
            name TEXT NOT NULL,
            avatar TEXT,
            blue_chip BOOLEAN DEFAULT 0,
            UNIQUE(platform, uid)
        )
    ''')

    # 标签表（多对多）
    c.execute('''
        CREATE TABLE IF NOT EXISTS author_tags (
            author_id INTEGER,
            tag TEXT NOT NULL,
            FOREIGN KEY (author_id) REFERENCES authors(id),
            PRIMARY KEY (author_id, tag)
        )
    ''')

    # 粉丝历史表
    c.execute('''
        CREATE TABLE IF NOT EXISTS follower_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author_id INTEGER,
            followers_count INTEGER NOT NULL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES authors(id)
        )
    ''')

    conn.commit()
    conn.close()

def load_config():
    """从 config.json 加载配置"""
    if not CONFIG_PATH.exists():
        return {"authors": []}
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def sync_authors():
    """同步 config.json 到数据库"""
    config = load_config()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    for author in config.get("authors", []):
        # 插入或更新作者
        c.execute('''
            INSERT INTO authors (platform, uid, name, avatar, blue_chip)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(platform, uid) DO UPDATE SET
                name = excluded.name,
                avatar = excluded.avatar,
                blue_chip = excluded.blue_chip
        ''', (
            author.get("platform", "bilibili"),
            author["uid"],
            author["name"],
            author.get("avatar", ""),
            author.get("blue_chip", False)
        ))

        # 获取 author_id
        c.execute('SELECT id FROM authors WHERE platform = ? AND uid = ?',
                  (author.get("platform", "bilibili"), author["uid"]))
        author_id = c.fetchone()[0]

        # 删除旧标签
        c.execute('DELETE FROM author_tags WHERE author_id = ?', (author_id,))

        # 插入新标签
        for tag in author.get("tags", []):
            c.execute('INSERT OR IGNORE INTO author_tags (author_id, tag) VALUES (?, ?)',
                      (author_id, tag))

    conn.commit()
    conn.close()

def save_follower(author_id, followers_count):
    """保存粉丝数记录"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO follower_history (author_id, followers_count)
        VALUES (?, ?)
    ''', (author_id, followers_count))
    conn.commit()
    conn.close()

def get_authors_for_crawl():
    """获取需要爬取的作者列表"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT a.id, a.platform, a.uid, a.name, GROUP_CONCAT(t.tag) as tags
        FROM authors a
        LEFT JOIN author_tags t ON a.id = t.author_id
        GROUP BY a.id
    ''')
    rows = c.fetchall()
    conn.close()

    return [{
        "id": r[0],
        "platform": r[1],
        "uid": r[2],
        "name": r[3],
        "tags": r[4].split(',') if r[4] else []
    } for r in rows]

def get_index_data():
    """获取指数计算所需数据"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 获取最新粉丝数据
    c.execute('''
        SELECT a.id, a.name, h.followers_count, t.tag
        FROM authors a
        JOIN follower_history h ON a.id = h.author_id
        JOIN author_tags t ON a.id = t.author_id
        WHERE h.recorded_at = (
            SELECT MAX(recorded_at) FROM follower_history WHERE author_id = a.id
        )
    ''')

    rows = c.fetchall()
    conn.close()

    # 按 tag 分组
    tag_data = {}
    for row in rows:
        author_id, name, followers, tag = row
        if tag not in tag_data:
            tag_data[tag] = []
        tag_data[tag].append({
            "name": name,
            "followers": followers
        })

    return tag_data

if __name__ == "__main__":
    init_db()
    sync_authors()
    print("数据库初始化完成")
