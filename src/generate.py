import json
import sqlite3
from pathlib import Path
from database import DB_PATH

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

def calculate_index_value(authors_data, divisor=10000):
    """计算指数值"""
    total = sum(a["followers"] for a in authors_data)
    return round(total / divisor, 2)

def generate_index_data():
    """生成指数数据"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 获取所有 tag
    c.execute('SELECT DISTINCT tag FROM author_tags')
    tags = [r[0] for r in c.fetchall()]

    index_data = {}

    for tag in tags:
        # 获取该 tag 下所有作者的最新粉丝数
        c.execute('''
            SELECT a.name, h.followers_count
            FROM authors a
            JOIN author_tags t ON a.id = t.author_id
            JOIN follower_history h ON a.id = h.author_id
            WHERE t.tag = ? AND h.recorded_at = (
                SELECT MAX(recorded_at) FROM follower_history WHERE author_id = a.id
            )
        ''', (tag,))

        rows = c.fetchall()
        if rows:
            authors = [{"name": r[0], "followers": r[1]} for r in rows]
            index_data[tag] = {
                "value": calculate_index_value(authors),
                "count": len(authors),
                "authors": authors
            }

    conn.close()
    return index_data

def generate_html():
    """生成前端 HTML"""
    FRONTEND_DIR.mkdir(exist_ok=True)

    index_data = generate_index_data()

    # 生成数据文件
    with open(FRONTEND_DIR / "data.json", "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

    html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SocialDex - 社会思潮指数</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #0d1117;
            color: #c9d1d9;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 28px;
            color: #58a6ff;
            margin-bottom: 8px;
        }
        .header p { color: #8b949e; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }
        .card {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 20px;
        }
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .tag-name {
            font-size: 18px;
            font-weight: 600;
            color: #f0f6fc;
        }
        .tag-count {
            font-size: 12px;
            color: #8b949e;
            background: #21262d;
            padding: 4px 8px;
            border-radius: 4px;
        }
        .index-value {
            font-size: 32px;
            font-weight: 700;
            color: #3fb950;
            margin-bottom: 5px;
        }
        .index-label {
            font-size: 12px;
            color: #8b949e;
        }
        .author-list {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #30363d;
        }
        .author-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            font-size: 14px;
        }
        .author-name { color: #c9d1d9; }
        .author-followers { color: #8b949e; }
        .update-time {
            text-align: center;
            margin-top: 40px;
            color: #6e7681;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>SocialDex</h1>
        <p>社会思潮指数 - 基于自媒体粉丝量的板块轮动观察</p>
    </div>
    <div class="grid" id="indexGrid"></div>
    <div class="update-time">更新时间: <span id="updateTime"></span></div>

    <script>
        fetch('data.json')
            .then(r => r.json())
            .then(data => {
                const grid = document.getElementById('indexGrid');
                const updateTime = new Date().toLocaleString('zh-CN');
                document.getElementById('updateTime').textContent = updateTime;

                Object.entries(data).forEach(([tag, info]) => {
                    const card = document.createElement('div');
                    card.className = 'card';

                    const topAuthors = info.authors
                        .sort((a, b) => b.followers - a.followers)
                        .slice(0, 5);

                    card.innerHTML = `
                        <div class="card-header">
                            <span class="tag-name">${tag}</span>
                            <span class="tag-count">${info.count} 位UP主</span>
                        </div>
                        <div class="index-value">${info.value.toLocaleString()}</div>
                        <div class="index-label">指数值</div>
                        <div class="author-list">
                            ${topAuthors.map(a => `
                                <div class="author-item">
                                    <span class="author-name">${a.name}</span>
                                    <span class="author-followers">${(a.followers/10000).toFixed(1)}万</span>
                                </div>
                            `).join('')}
                        </div>
                    `;
                    grid.appendChild(card);
                });
            });
    </script>
</body>
</html>'''

    with open(FRONTEND_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"前端文件已生成到 {FRONTEND_DIR}")

if __name__ == "__main__":
    generate_html()
