import abc
import datetime
import re
from tokenize import String
from typing import List, TypedDict

import requests
from bs4 import BeautifulSoup


class Column(TypedDict):
    title: String
    link: String


class Scraper(abc.ABC):
    def _convert_str_to_datetime(self, dt: str, dt_format: str) -> datetime.datetime:
        return datetime.datetime.strptime(dt, dt_format)

    def _clean_text(self, text: str) -> str:
        clean_text = text.replace("\xa0", " ")
        return clean_text

    @abc.abstractclassmethod
    def get_html(self) -> BeautifulSoup:
        ...

    @abc.abstractclassmethod
    def parse(self, html) -> List[Column]:
        ...

    def scrape(self) -> List[Column]:
        html = self.get_html()
        columns = self.parse(html)
        return columns


class HKScraper(Scraper):
    def get_html(self):
        url = "https://www.hankyung.com/opinion/0002"
        headers = {"Referer": "https://www.hankyung.com/opinion/0002"}
        params = {"page": "1"}
        res = requests.get(url=url, params=params, headers=headers)
        html = BeautifulSoup(res.content, "lxml")
        return html

    def parse(self, html):
        columns = []
        data = html.select("ul.list_basic.v2 > li > div.article")
        for each in data:
            dt = each.select("div.article_info > span.time").text.strip()
            dt = self._convert_str_to_datetime(dt, "%Y-%m-%d %H:%M")
            if dt < datetime.datetime.now().replace(hour=0, minute=0, second=0):
                continue
            title = each.select_one("div.article > h3.tit > a").text.strip()
            link = each.select_one("div.article > h3.tit > a").get("href").strip()
            columns.append(dict(title=title, link=link))
        return columns


class MTDScarper(Scraper):
    def get_html(self):
        url = "https://news.mt.co.kr/column/opinion_list.html"
        params = {
            "code": "column6",
        }
        headers = {"Referer": "https://news.mt.co.kr/column/opinion_inside.html?code=06"}
        res = requests.get(url=url, params=params, headers=headers)
        html = BeautifulSoup(res.content, "lxml")
        return html

    def parse(self, html):
        data = html.select("div#content > ul.conlist_p1.mgt25 > li.bundle ")
        columns = []
        for each in data:
            title = each.select_one("div.con > strong.subject > a").text.strip()
            link = each.select_one("div.con > strong.subject > a").get("href")
            dt_txt = each.select_one("div.con > p.txt > span.etc").text
            dt = re.search(
                r"\d{4}\.(0[1-9]|1[0-2])\.(0[1-9]|[1-2][0-9]|3[0-1])\s*(0[0-9]|1[0-9]|2[0-3]):(0[0-9]|[1-5][0-9])",
                dt_txt,
            ).group()
            dt = self._clean_text(dt)
            now = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            if self._convert_str_to_datetime(dt, "%Y.%m.%d %H:%M") < now:
                break
            columns.append(dict(title=title, link=link))
        return columns
