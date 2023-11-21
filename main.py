from requests import get
from bs4 import BeautifulSoup

base_url = "https://computer.knu.ac.kr/bbs/board.php?bo_table=sub5_1&page="
page_nb = 1

response = get(f"{base_url}{page_nb}")
soup = BeautifulSoup(response.text, "html.parser")
infos = soup.find_all("tr")
for info in infos:
    tds = info.find_all("td")
    if len(tds) > 0:
        datas = tds[1].find_all("a")
        for data in datas:
            print(data.text.strip())
        print(tds[4].text)
        print("--------------------")
