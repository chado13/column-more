from typing import List, Dict


import datetime
import requests
from bs4 import BeautifulSoup


def convert_str_to_datetime(dt: str) -> datetime.datetime:
    return datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M")


def hk_scrape() -> List[Dict[str, str]]:
    url = "https://www.hankyung.com/opinion/0002"
    page = 1
    headers = {"Referer": "https://www.hankyung.com/opinion/0002"}
    params = {"page": str(page)}
    res = requests.get(url=url, params=params, headers=headers)
    html = BeautifulSoup(res.content, "lxml")
    columns = []
    data = html.select("ul.list_basic.v2 > li > div.article")
    for each in data:
        dt = each.select("div.article_info > span.time").text.strip()
        dt = convert_str_to_datetime(dt)
        if dt < datetime.datetime.now().replace(hour=0, minute=0, second=0):
            continue
        title = each.select_one("div.article > h3.tit > a").text.strip()
        link = each.select_one("div.article > h3.tit > a").get("href").strip()
        columns.append(dict(title=title, link=link))
    return columns


if __name__ == "__main__":
    hk_scrape()
