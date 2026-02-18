import time
import requests
from database import get_authors_for_crawl, save_follower

def get_bilibili_followers(uid):
    """获取 B 站用户粉丝数"""
    url = f"https://api.bilibili.com/x/web-interface/card?mid={uid}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        if data.get("code") == 0:
            return data["data"]["card"]["fans"]
        else:
            print(f"获取 UID {uid} 失败: {data.get('message')}")
            return None
    except Exception as e:
        print(f"请求 UID {uid} 出错: {e}")
        return None

def crawl_all():
    """爬取所有作者的粉丝数"""
    authors = get_authors_for_crawl()
    print(f"开始爬取 {len(authors)} 个作者的粉丝数")

    for i, author in enumerate(authors):
        platform = author["platform"]
        uid = author["uid"]
        name = author["name"]

        print(f"[{i+1}/{len(authors)}] 爬取 {name} ({uid})...")

        if platform == "bilibili":
            followers = get_bilibili_followers(uid)
        else:
            print(f"不支持的平台: {platform}")
            continue

        if followers is not None:
            save_follower(author["id"], followers)
            print(f"  -> {followers} 粉丝")

        # 延迟 1 秒，避免触发反爬
        time.sleep(1)

    print("爬取完成")

if __name__ == "__main__":
    crawl_all()
