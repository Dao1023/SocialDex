import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from database import DB_PATH

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


def _build_series(c, author_ids, timestamps):
    """For a list of author_ids, build aggregated follower time series"""
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
    return series


def _build_author_series(c, author_id, timestamps):
    """For a single author, get their follower history directly"""
    series = []
    for ts in timestamps:
        c.execute('''
            SELECT h.followers_count
            FROM follower_history h
            WHERE h.author_id = ?
            AND h.recorded_at = (
                SELECT MAX(recorded_at)
                FROM follower_history h2
                WHERE h2.author_id = h.author_id AND h2.recorded_at <= ?
            )
        ''', (author_id, ts))

        count = c.fetchone()
        if count:
            series.append({
                "time": ts,
                "value": round(count[0] / 10000, 2)
            })
        else:
            series.append({
                "time": ts,
                "value": 0
            })
    return series


def _find_base(pts, latest_time, days):
    """Find the value from N days ago (closest data point after cutoff)"""
    if not pts:
        return None

    # Parse latest time
    latest_dt = datetime.strptime(latest_time, "%Y-%m-%d %H:%M:%S")
    cutoff = latest_dt - timedelta(days=days)

    # Find the first data point after cutoff
    for pt in pts:
        pt_dt = datetime.strptime(pt["time"], "%Y-%m-%d %H:%M:%S")
        if pt_dt >= cutoff:
            return pt["value"]

    # If no point found, use the oldest available
    return pts[0]["value"]


def _safe_pct(current, base):
    """Calculate percentage change safely (avoid div by zero)"""
    if base is None or base == 0:
        return 0
    return round((current - base) / base * 100, 2)


def generate_meta(c):
    """Generate meta section with tags and authors"""
    # Get tags
    c.execute('SELECT DISTINCT tag FROM author_tags ORDER BY tag')
    tags = [r[0] for r in c.fetchall()]

    # Get authors with their info
    c.execute('''
        SELECT a.id, a.name, a.platform, GROUP_CONCAT(t.tag) as tags
        FROM authors a
        LEFT JOIN author_tags t ON a.id = t.author_id
        GROUP BY a.id
        ORDER BY a.id
    ''')

    authors = []
    for r in c.fetchall():
        author_id, name, platform, tags_str = r
        authors.append({
            "id": author_id,
            "name": name,
            "platform": platform,
            "tags": tags_str.split(',') if tags_str else []
        })

    # Get updated_at (latest timestamp)
    c.execute('SELECT MAX(recorded_at) FROM follower_history')
    updated_at = c.fetchone()[0]

    return {
        "updated_at": updated_at,
        "tags": tags,
        "authors": authors
    }


def generate_series(c, timestamps, tags, author_ids):
    """Generate series section with tag, author, and index series"""
    series = {}

    # Tag series
    for tag in tags:
        c.execute('SELECT author_id FROM author_tags WHERE tag = ?', (tag,))
        tag_author_ids = [r[0] for r in c.fetchall()]

        if tag_author_ids:
            series[f"tag:{tag}"] = _build_series(c, tag_author_ids, timestamps)

    # Author series
    for author_id in author_ids:
        c.execute('SELECT name FROM authors WHERE id = ?', (author_id,))
        name = c.fetchone()[0]
        series[f"author:{name}"] = _build_author_series(c, author_id, timestamps)

    # Blue chip 100 index
    c.execute('''
        SELECT a.id
        FROM authors a
        JOIN follower_history h ON a.id = h.author_id
        WHERE h.recorded_at = (SELECT MAX(recorded_at) FROM follower_history)
        ORDER BY h.followers_count DESC
        LIMIT 100
    ''')
    blue_chip_ids = [r[0] for r in c.fetchall()]

    if blue_chip_ids:
        series["index:蓝筹100"] = _build_series(c, blue_chip_ids, timestamps)

    return series


def generate_summary(series_data):
    """Generate summary section with latest values and changes"""
    summary = {}

    for key, pts in series_data.items():
        if not pts:
            continue

        latest = pts[-1]["value"]
        latest_time = pts[-1]["time"]

        base_1d = _find_base(pts, latest_time, 1)
        base_7d = _find_base(pts, latest_time, 7)

        change_1d = round(latest - base_1d, 2) if base_1d is not None else 0
        change_1d_pct = _safe_pct(latest, base_1d)

        change_7d = round(latest - base_7d, 2) if base_7d is not None else 0
        change_7d_pct = _safe_pct(latest, base_7d)

        summary[key] = {
            "latest": latest,
            "change_1d": change_1d,
            "change_1d_pct": change_1d_pct,
            "change_7d": change_7d,
            "change_7d_pct": change_7d_pct
        }

    return summary


def generate_data():
    """Generate complete data.json with meta, series, and summary"""
    FRONTEND_DIR.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Get all timestamps
    c.execute('SELECT DISTINCT recorded_at FROM follower_history ORDER BY recorded_at')
    timestamps = [r[0] for r in c.fetchall()]

    # Get all tags
    c.execute('SELECT DISTINCT tag FROM author_tags ORDER BY tag')
    tags = [r[0] for r in c.fetchall()]

    # Get all author IDs
    c.execute('SELECT DISTINCT id FROM authors ORDER BY id')
    author_ids = [r[0] for r in c.fetchall()]

    # Generate meta section
    meta = generate_meta(c)

    # Generate series section
    series = generate_series(c, timestamps, tags, author_ids)

    # Generate summary section
    summary = generate_summary(series)

    conn.close()

    # Combine all sections
    data = {
        "meta": meta,
        "series": series,
        "summary": summary
    }

    # Write to file
    with open(FRONTEND_DIR / "data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"数据已生成到 {FRONTEND_DIR / 'data.json'}")


if __name__ == "__main__":
    generate_data()
