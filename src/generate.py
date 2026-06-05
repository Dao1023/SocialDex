import json
import sqlite3
from pathlib import Path
from database import DB_PATH

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

def generate_index_data():
    """生成指数历史数据"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 获取所有记录时间点
    c.execute('SELECT DISTINCT recorded_at FROM follower_history ORDER BY recorded_at')
    timestamps = [r[0] for r in c.fetchall()]

    # 蓝筹100成分（取最新时间点的粉丝前100）
    c.execute('''
        SELECT a.id
        FROM authors a
        JOIN follower_history h ON a.id = h.author_id
        WHERE h.recorded_at = (SELECT MAX(recorded_at) FROM follower_history)
        ORDER BY h.followers_count DESC
        LIMIT 100
    ''')
    blue_chip_ids = [r[0] for r in c.fetchall()]

    # 获取所有 tag
    c.execute('SELECT DISTINCT tag FROM author_tags')
    tags = [r[0] for r in c.fetchall()]

    # 为每个指数生成时间序列
    index_series = {}

    for tag in tags:
        c.execute('SELECT author_id FROM author_tags WHERE tag = ?', (tag,))
        author_ids = [r[0] for r in c.fetchall()]

        series = []
        for ts in timestamps:
            c.execute('''
                SELECT SUM(h.followers_count)
                FROM follower_history h
                WHERE h.author_id IN ({})
                AND h.recorded_at = (
                    SELECT MAX(recorded_at)
                    FROM follower_history h2
                    WHERE h2.author_id = h.author_id AND h2.recorded_at <= ?
                )
            '''.format(','.join('?' * len(author_ids))), author_ids + [ts])

            total = c.fetchone()[0] or 0
            series.append({
                "time": ts,
                "value": round(total / 10000, 2)
            })

        index_series[tag] = series

    # 蓝筹100指数时间序列
    series = []
    for ts in timestamps:
        c.execute('''
            SELECT SUM(h.followers_count)
            FROM follower_history h
            WHERE h.author_id IN ({})
            AND h.recorded_at = (
                SELECT MAX(recorded_at)
                FROM follower_history h2
                WHERE h2.author_id = h.author_id AND h2.recorded_at <= ?
            )
        '''.format(','.join('?' * len(blue_chip_ids))), blue_chip_ids + [ts])

        total = c.fetchone()[0] or 0
        series.append({
            "time": ts,
            "value": round(total / 10000, 2)
        })

    index_series["蓝筹100"] = series

    conn.close()
    return index_series

def generate_data():
    """只生成 data.json，不再生成 HTML"""
    FRONTEND_DIR.mkdir(exist_ok=True)

    index_data = generate_index_data()

    with open(FRONTEND_DIR / "data.json", "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

    print(f"数据已生成到 {FRONTEND_DIR / 'data.json'}")

if __name__ == "__main__":
    generate_data()
