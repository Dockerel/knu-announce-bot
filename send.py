import requests, os
from dotenv import load_dotenv

load_dotenv()
discord_url = os.environ.get("web_hook_url")


# 디스코드 채널로 메세지 전송
def discord_send_message(text):
    message = {"content": f"{str(text)}"}
    requests.post(discord_url, data=message)
    print(message)


discord_send_message("!new_announcement")
