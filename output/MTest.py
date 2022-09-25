import json

import requests


userUrl = 'https://live.douyin.com/webcast/user/?aid=6383&target_uid=86593551403'

Headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
result=requests.get(url=userUrl,headers=Headers)
jo = json.loads(result.content)
print(jo.get("data").get("share_qrcode_uri"))
print(jo.get("data").get("sec_uid"))

