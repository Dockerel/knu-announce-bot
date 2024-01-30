from bs4 import BeautifulSoup
import requests, json
from datetime import datetime, timedelta, timezone
from discord_webhook import DiscordWebhook


class KnuCompCrawler:
    def __init__(self, option):
        self.base_url = "http://127.0.0.1:8000/api/v1"

        self.option = option

        self.GET_SECRET_KEY = "get-secret-@!*%&^*&B*&@*NFDNLKsal:JMI:JMg!!@&HN"
        self.POST_SECRET_KEY = "post-secret-!*%*NF@DN*&@LKsal:JMI:Mg!H@&NJ!"

        self.info_type = {
            "일반공지": "general",
            "학사": "bachelor",
            "장학": "scholarship",
            "심컴": "simcom",
            "글솝": "glsob",
            "인컴": "incom",
            "대학원": "graduate",
            "대학원 계약학과": "contract",
        }

    def start(self):
        results = self.knu_comp_crawling()
        if len(results) > 0:
            self.save_to_server(results)
            self.delete_request_to_server()
            self.send_to_links(results)
        else:
            self.print_complete_msg(200, "nothing to send today")
            self.send_to_links([])

    def today_date_of_korea(self):
        datetime_utc = datetime.utcnow()
        timezone_kst = timezone(timedelta(hours=9))
        datetime_kst = datetime_utc.astimezone(timezone_kst)
        today_year = str(datetime_kst.year).zfill(2)
        today_month = str(datetime_kst.month).zfill(2)
        today_day = str(datetime_kst.day).zfill(2)
        today = f"{today_year}-{today_month}-{today_day}"
        return today

    def print_complete_msg(self, status, msg):
        now = str(datetime.now()).split(".")[0]
        print(f"[{now}] {status} : {msg}")

    def knu_comp_crawling(self):
        dbs = []
        today = self.today_date_of_korea()
        print(today)

        comp_url = "https://computer.knu.ac.kr/bbs/board.php?bo_table=sub5_1&page="
        max_page_nb = 2

        for page_nb in range(max_page_nb):
            response = requests.get(f"{comp_url}{page_nb+1}")
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

                    if self.option == "today":
                        if today != date:
                            self.print_complete_msg(200, "crawling finished")
                            return dbs
                    dbs.append(data)
        self.print_complete_msg(200, "crawling finished")
        return dbs[::-1]

    def save_to_server(self, infos):
        try:
            if len(infos) > 0:
                post_secret_key = self.POST_SECRET_KEY
                for info in infos:
                    latest_response = requests.post(
                        f"{self.base_url}/infos/{post_secret_key}",
                        data={
                            "info_type": self.info_type[info[0]],
                            "title": info[1],
                            "href": info[2],
                            "date": info[3],
                        },
                    )
            self.print_complete_msg(200, "new infos saved")
        except:
            self.print_complete_msg(400, "bad requests")

    def infosFormatter(self, infos):
        # 날짜별로 나눠서 전송 - 날짜별로 딕셔너리 구성
        msgs = dict()
        for info in infos:
            if msgs.get(info[3]) == None:
                msgs[info[3]] = []
            msgs[info[3]].append(info[:3])
        return msgs

    def delete_error_link_users(self, error_links):
        # 오류난 링크 삭제 처리
        post_secret_key = self.POST_SECRET_KEY
        response = requests.post(
            f"{self.base_url}/users/delete-errorlink-users/{post_secret_key}",
            json=json.dumps(error_links),
        )
        now = str(datetime.now()).split(".")[0]
        self.print_complete_msg(response.status_code, "error users deleted")

    def send_to_links(self, infos):
        try:
            # 오류난 링크들 저장
            error_links = []
            get_secret_key = self.GET_SECRET_KEY
            res_links = requests.get(f"{self.base_url}/links/all/{get_secret_key}")
            datas = res_links.json()
            if len(infos) > 0:
                msgs = self.infosFormatter(infos)
                for k in msgs.keys():
                    temp_msg = ""

                    temp_msg += "=" * 10
                    for d in msgs[k]:
                        temp_msg += f"\n{k} | {d[0]}\n{d[1]}\n{d[2]}\n"
                    temp_msg += "=" * 10

                    for data in datas:
                        webhook = DiscordWebhook(url=data.get("link"), content=temp_msg)
                        response = webhook.execute()
                        if response.status_code != 200:
                            error_links.append(data)
                self.print_complete_msg(200, "new infos sended")
            else:
                for data in datas:
                    webhook = DiscordWebhook(
                        url=data.get("link"),
                        content="==========\n\nnothing to send today\n\n==========",
                    )
                    response = webhook.execute()
                    if response.status_code != 200:
                        error_links.append(data)
            if len(error_links) > 0:
                self.delete_error_link_users(error_links)
        except Exception as e:
            print(e)
            self.print_complete_msg(400, "bad requests")

    def delete_request_to_server(self):
        response = requests.get(f"{self.base_url}/infos/deleteInfos")
        self.print_complete_msg(response.status_code, "old infos deleted")


knu_crawler = KnuCompCrawler("today")
knu_crawler.start()
