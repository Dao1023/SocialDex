#!/usr/bin/env python
"""
SocialDex 主运行脚本
执行完整流程：初始化数据库 -> 爬取数据 -> 生成前端
"""

from src.database import init_db, sync_authors
from src.crawler import crawl_all
from src.generate import generate_data

def main():
    print("=" * 50)
    print("SocialDex - 社会思潮指数更新")
    print("=" * 50)

    # 1. 初始化数据库
    print("\n[1/4] 初始化数据库...")
    init_db()

    # 2. 同步配置
    print("[2/4] 同步 config.json 到数据库...")
    sync_authors()

    # 3. 爬取数据
    print("[3/4] 爬取最新粉丝数据...")
    crawl_all()

    # 4. 生成数据
    print("[4/4] 生成 data.json...")
    generate_data()

    print("\n" + "=" * 50)
    print("完成！数据已生成到 frontend/data.json")
    print("=" * 50)

if __name__ == "__main__":
    main()
