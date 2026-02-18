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
        # 获取该 tag 的所有作者 ID
        c.execute('SELECT author_id FROM author_tags WHERE tag = ?', (tag,))
        author_ids = [r[0] for r in c.fetchall()]

        series = []
        for ts in timestamps:
            # 计算该时间点的指数值（使用每个作者在该时间点及之前的最新记录）
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

def generate_html():
    """生成前端 HTML"""
    FRONTEND_DIR.mkdir(exist_ok=True)

    index_data = generate_index_data()

    # 生成数据文件（保留，用于调试）
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
        }
        .header {
            text-align: center;
            padding: 20px;
            margin-bottom: 20px;
        }
        .header h1 {
            font-size: 32px;
            color: #58a6ff;
            margin-bottom: 8px;
        }
        .header p { color: #8b949e; }
        #chart {
            width: 100%;
            height: calc(100vh - 120px);
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>SocialDex</h1>
        <p>社会思潮指数 - 基于自媒体粉丝量的板块轮动观察</p>
    </div>
    <div id="chart"></div>

    <script>
        const data = {json_data};

        const chart = echarts.init(document.getElementById('chart'));

        const series = Object.keys(data).map(tag => ({
            name: tag,
            type: 'line',
            data: data[tag].map(d => [d.time, d.value]),
            smooth: true,
            symbol: 'none',
            lineStyle: { width: 2 }
        }));

        const option = {
            backgroundColor: '#0d1117',
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'cross' }
            },
            legend: {
                data: Object.keys(data),
                textStyle: { color: '#c9d1d9' },
                top: 10
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '15%',
                containLabel: true
            },
            dataZoom: [
                {
                    type: 'inside',
                    start: 0,
                    end: 100,
                    zoomOnMouseWheel: true,
                    moveOnMouseMove: true,
                    moveOnMouseWheel: false
                },
                {
                    start: 0,
                    end: 100,
                    handleIcon: 'M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23.1h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z',
                    handleSize: '80%',
                    handleStyle: {
                        color: '#fff',
                        shadowBlur: 3,
                        shadowColor: 'rgba(0, 0, 0, 0.6)',
                        shadowOffsetX: 2,
                        shadowOffsetY: 2
                    },
                    textStyle: { color: '#8b949e' },
                    borderColor: '#30363d',
                    fillerColor: 'rgba(88, 166, 255, 0.1)'
                }
            ],
            xAxis: {
                type: 'time',
                axisLine: { lineStyle: { color: '#30363d' } },
                axisLabel: { color: '#8b949e' }
            },
            yAxis: {
                type: 'value',
                axisLine: { lineStyle: { color: '#30363d' } },
                axisLabel: { color: '#8b949e' },
                splitLine: { lineStyle: { color: '#21262d' } }
            },
            series: series
        };

        chart.setOption(option);

        window.addEventListener('resize', () => chart.resize());
    </script>
</body>
</html>'''

    # 将数据注入到 HTML
    html_content = html_content.replace('{json_data}', json.dumps(index_data, ensure_ascii=False))

    with open(FRONTEND_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"前端文件已生成到 {FRONTEND_DIR}")

if __name__ == "__main__":
    generate_html()
