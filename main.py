from requests import get
from bs4 import BeautifulSoup
import requests, os, json
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from discord_webhook import DiscordWebhook

load_dotenv()


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


def today_date_of_korea():
    datetime_utc = datetime.utcnow()
    timezone_kst = timezone(timedelta(hours=9))
    datetime_kst = datetime_utc.astimezone(timezone_kst)
    today = f"{datetime_kst.year}-{datetime_kst.month}-{datetime_kst.day}"
    return today


def knu_comp_crawling(option):
    dbs = []
    today = today_date_of_korea()

    base_url = "https://computer.knu.ac.kr/bbs/board.php?bo_table=sub5_1&page="
    max_page_nb = 2

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

    return dbs[::-1]


def save_to_server(infos):
    if len(infos) > 0:
        post_secret_key = os.environ.get("POST_SECRET_KEY")
        for info in infos:
            requests.post(
                f"http://127.0.0.1:8000/api/v1/infos/all/{post_secret_key}",
                data={
                    "info_type": info_type[info[0]],
                    "title": info[1],
                    "href": info[2],
                    "date": info[3],
                },
            )


def send_to_links(infos):
    if len(infos) >= 0:
        # 오류난 링크들 저장
        error_links = []
        get_secret_key = os.environ.get("GET_SECRET_KEY")
        res_links = requests.get(
            f"http://127.0.0.1:8000/api/v1/links/all/{get_secret_key}"
        )
        datas = res_links.json()

        for data in datas:
            webhook = DiscordWebhook(url=data.get("link"), content="hi")
            response = webhook.execute()
            if response.status_code != 200:
                error_links.append(data)

        delete_error_link_users(error_links)


def delete_error_link_users(error_links):
    # 오류난 링크 삭제 처리
    post_secret_key = os.environ.get("POST_SECRET_KEY")
    requests.post(
        f"http://127.0.0.1:8000/api/v1/users/delete-errorlink-users/{post_secret_key}",
        json=json.dumps(error_links),
    )


# results = knu_comp_crawling("all")
results = knu_comp_crawling("today")
save_to_server(results)
send_to_links(results)
