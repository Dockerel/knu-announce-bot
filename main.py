from requests import get
from bs4 import BeautifulSoup
import requests, os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

load_dotenv()

base_url = "https://computer.knu.ac.kr/bbs/board.php?bo_table=sub5_1&page="
max_page_nb = 2

info_type = {
    "일반공지": "general",
    "학사": "bachelor",
    "장학": "scholarship",
    "심컴": "simcom",
    "글솝": "glsob",
    "인컴": "incom",
    "대학원": "graduate",
    "대학원 계약학과": "contract",
}

datetime_utc = datetime.utcnow()
timezone_kst = timezone(timedelta(hours=9))
datetime_kst = datetime_utc.astimezone(timezone_kst)
today = f"{datetime_kst.year}-{datetime_kst.month}-{datetime_kst.day}"
# yesterday = f"{datetime_kst.year}-{datetime_kst.month}-{datetime_kst.day-1}"


def knu_comp_crawling(option):
    dbs = []

    for page_nb in range(max_page_nb):
        response = get(f"{base_url}{page_nb+1}")
        soup = BeautifulSoup(response.text, "html.parser")
        infos = soup.find_all("tr")
        for info in infos:
            data = []
            tds = info.find_all("td")
            if len(tds) > 0:
                datas = tds[1].find_all("a")
                for i in range(2):
                    d = datas[i].text.strip()
                    data.append(d)
                    if i == 1:
                        links = datas[i].attrs["href"]
                        data.append(links)
                date = tds[4].text
                data.append(date)

                if option == "today":
                    if today != date:
                        return dbs
                dbs.append(data)

    return dbs


# initial info setting
# datas = knu_comp_crawling("all")
# post_secret_key = os.environ.get("POST_SECRET_KEY")
# for data in knu_comp_crawling():
#     requests.post(
#         f"http://127.0.0.1:8000/api/v1/infos/all/{post_secret_key}",
#         data={
#             "info_type": info_type[data[0]],
#             "title": data[1],
#             "href": data[2],
#             "date": data[3],
#         },
#     )

results = knu_comp_crawling("today")
if len(results) > 0:
    save_to_server(results)
    send_to_links(results)
