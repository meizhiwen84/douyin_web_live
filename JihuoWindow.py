import json
import os
import sys
import uuid

import requests
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget

from CollectWindow import CollectWindow


class JihuoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUi()

    def initUi(self):
        filePath=os.path.join(os.path.dirname(os.path.abspath(os.path.relpath(sys.argv[0]))),"ui","auth.ui")

        self.ui = uic.loadUi(filePath)
        self.ui.jihuo_btn.clicked.connect(self.jihuo)

    def jihuo(self):
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]

        rs = requests.get(url="http://tk.laobayou.cn/refdgertregfxgfd?macaddress=" + mac)
        jo = json.loads(rs.content)
        if jo.get("code") == str(200):
            self.ui.hide()
            self.window = CollectWindow()
            self.window.ui.show()

        else:
            print("请输入正确的授权码")