#!/usr/bin/env python
"""
SocialDex 主运行脚本
执行完整流程：初始化数据库 -> 爬取数据 -> 生成前端
"""

from src.database import init_db, sync_authors
from src.crawler import crawl_all
from src.generate import generate_html

def main():
    print("=" * 50)
    print("SocialDex - 社会思潮指数更新")
    print("=" * 50)

    # 1. 初始化数据库
    print("\n[1/3] 初始化数据库...")
    init_db()

    # 2. 同步配置
    print("[2/3] 同步 config.json 到数据库...")
    sync_authors()

    # 3. 爬取数据
    print("[3/3] 爬取最新粉丝数据...")
    crawl_all()

    # 4. 生成前端
    print("\n[4/4] 生成前端页面...")
    generate_html()

    print("\n" + "=" * 50)
    print("完成！前端文件已生成到 frontend/index.html")
    print("=" * 50)

if __name__ == "__main__":
    main()
