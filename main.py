import json
import sys
import uuid

import requests
from PyQt5.QtWidgets import QApplication

from CollectWindow import CollectWindow

# 主线程
from JihuoWindow import JihuoWindow


if __name__ == "__main__":

    application = QApplication(sys.argv)

    # 获取本地mac地址，发送请求校验是否经过授权  本地为：da2660bf36f4

    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    print(mac)
    rs = requests.get(url="http://tk.laobayou.cn/refdgertregfxgfd?macaddress=" + mac)
    jo = json.loads(rs.content)
    if jo.get("code") == str(200):
        window = CollectWindow()
        window.ui.show()

    else:
        # 弹出一个激活框
        jw = JihuoWindow()
        jw.ui.show()
        print("未授权")

    application.exec_()
