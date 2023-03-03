import abc
import datetime
import re
from typing import TypedDict

import bs4
import requests
from bs4 import BeautifulSoup


class Column(TypedDict):
    title: str
    link: str


class Scraper(abc.ABC):
    def _convert_str_to_datetime(self, dt: str, dt_format: str) -> datetime.datetime:
        return datetime.datetime.strptime(dt, dt_format)

    def _clean_text(self, text: str) -> str:
        clean_text = text.replace("\xa0", " ")
        return clean_text

    def _is_today(self, dt: datetime.datetime) -> bool:
        today = datetime.datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        if dt >= today:
            return True
        else:
            return False

    @abc.abstractclassmethod
    def get_url_params_headers(self) -> tuple[str, dict[str, str], dict[str, str]]:
        ...

    def get_html(self) -> BeautifulSoup:
        url, params, headers = self.get_url_params_headers()
        res = requests.get(url=url, params=params, headers=headers)
        html = BeautifulSoup(res.content, "lxml")
        return html

    @abc.abstractclassmethod
    def parse(self, html: bs4.element) -> list[Column]:
        ...

    def scrape(self) -> list[Column]:
        html = self.get_html()
        columns = self.parse(html)
        return columns


class HKScraper(Scraper):
    def get_url_params_headers(self) -> tuple[str, dict[str, str], dict[str, str]]:
        url = "https://www.hankyung.com/opinion/0002"
        headers = {"Referer": "https://www.hankyung.com/opinion/0002"}
        params = {"page": "1"}
        return url, params, headers

    def parse(self, html: bs4.element) -> list[Column]:
        columns = []
        data = html.select("ul.list_basic.v2 > li > div.article")
        for each in data:
            dt = each.select("div.article_info > span.time").text.strip()
            dt = self._convert_str_to_datetime(dt, "%Y-%m-%d %H:%M")
            if not self._is_today(dt):
                break
            title = each.select_one("div.article > h3.tit > a").text.strip()
            link = each.select_one("div.article > h3.tit > a").get("href").strip()
            columns.append(dict(title=title, link=link))
        return columns  # type: ignore


class MTDScarper(Scraper):
    def get_url_params_headers(self):
        url = "https://news.mt.co.kr/column/opinion_list.html"
        params = {
            "code": "column6",
        }
        headers = {
            "Referer": "https://news.mt.co.kr/column/opinion_inside.html?code=06"
        }
        return url, params, headers

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
            dt = self._convert_str_to_datetime(dt, "%Y.%m.%d %H:%M")
            if not self._is_today(dt):
                break
            columns.append(dict(title=title, link=link))
        return columns


class SeoulScraper(Scraper):
    def get_url_params_headers(self):
        url = "https://www.seoul.co.kr/news/newslist.php"
        params = {"section": "column"}
        headers = {
            "Referer": "https://www.seoul.co.kr/news/newslist.php?section=column"
        }
        return url, params, headers

    def parse(self, html):
        columns = []
        data = html.select("div#articlelistDiv > ul.listType_ > li")
        for each in data:
            title = each.select_one("div.tit.lineclamp2 > a").get("title")
            link = "https://www.seoul.co.kr" + each.select_one(
                "div.tit.lineclamp2 > a"
            ).get("href")
            dt = each.select_one("div.date").text.strip()
            dt = self._convert_str_to_datetime(dt, "%Y-%m-%d")
            if not self._is_today(dt):
                break
            columns.append(dict(title=title, link=link))
        return columns
