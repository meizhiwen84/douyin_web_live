import asyncio
import csv
import io
import os
import signal
import ssl
import sys
import threading
import time
import urllib
from datetime import datetime

import pandas as pd
import qrcode as qrcode

from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QMessageBox, QDesktopWidget, QHeaderView

# 采集主界面
# from CollectThread import CollectThread
# import DouyinSpider as ds
from collectmain import DyCollectService
from collectmain import terminate

ssl._create_default_https_context = ssl._create_unverified_context

class CollectWindow(QWidget):

    tableSingal=pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.initUi()
        self.center()

    def center(self):
        # 获取屏幕的尺寸信息
        screen = QDesktopWidget().screenGeometry()
        # 获取窗口的尺寸信息
        size = self.geometry()
        # 将窗口移动到指定位置
        self.move(int((screen.width() - size.width()) / 2), int((screen.height() - size.height()) / 2))


    def initUi(self):
        filePath=os.path.join(os.path.dirname(os.path.abspath(os.path.relpath(sys.argv[0]))),"ui","dy1.ui")
        self.ui=uic.loadUi(filePath)
        # # 启动线程
        # self.collectThread=CollectThread(self.tableSingal)
        # self.collectThread.start()

        self.ui.stopCollect.setEnabled(False)
        # 开始按钮绑定点击事件
        self.ui.startCollect.clicked.connect(self.startCollect)
        # 停止
        self.ui.stopCollect.clicked.connect(self.stopCollect)
        # 清空
        self.ui.clearData.clicked.connect(self.clearData)
        # 导出
        self.ui.exportData.clicked.connect(self.exportData)
        # 查看
        self.ui.lookData.clicked.connect(self.lookData)

        # 表格给自定义信号绑定事件函数
        self.tableSingal.connect(self.collectCallback)

        self.ui.datalist.itemClicked.connect(self.show_data)
        self.ui.datalist.setStyleSheet("selection-background-color: red")
        self.ui.datalist.setSelectionBehavior(self.ui.datalist.SelectRows)
        self.ui.datalist.setColumnHidden(9, True);
        self.ui.datalist.setColumnHidden(10, True);
        self.ui.datalist.setColumnWidth(8,500)

        self.ui.entryRoom_check.stateChanged.connect(self.entryRoomSetting)
        self.ui.comment_check.stateChanged.connect(self.commentSetting)
        self.ui.like_check.stateChanged.connect(self.likeSetting)
        self.ui.gift_check.stateChanged.connect(self.giftSetting)

        self.dataType=[1,3,4,5] #进入是1，发言是3 ，送礼是：5，点赞是：4

    def entryRoomSetting(self,statusValue):
        self.baseSetting(1,statusValue)

    def commentSetting(self,statusValue):
        self.baseSetting(3,statusValue)

    def likeSetting(self,statusValue):
        self.baseSetting(4,statusValue)

    def giftSetting(self,statusValue):
        self.baseSetting(5,statusValue)

    def baseSetting(self,dataType,statusValue):
        if (dataType in self.dataType):
            if (statusValue == 0):
                self.dataType.remove(dataType)
        else:
            if (statusValue == 2):
                self.dataType.append(dataType)

    def show_data(self, Item):
        try:
            row = Item.row()  # 获取行数
            col = Item.column()  # 获取列数 注意是column而不是col哦
            text = Item.text()  # 获取内容
            print(row)
            print(col)
            print(text)

            secUid=self.ui.datalist.item(row, 11).text()
            print(secUid)

            qr = qrcode.QRCode(
                version=2,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=1
            )  # 设置二维码的大小
            qr.add_data("https://www.douyin.com/user/"+secUid)
            qr.make(fit=True)
            qr_img = qr.make_image()

            fp = io.BytesIO()
            qr_img.save(fp, "BMP")

            pixmap=QPixmap()
            pixmap.loadFromData(fp.getvalue())
            self.ui.zb_qr.setPixmap(pixmap)
            self.ui.zb_qr.setScaledContents(True)
        except Exception as e:
            pass

    def stopCollect(self):
        print("停止")
        # self.collectThread.puaseCollect()
        self.ui.startCollect.setEnabled(True)
        self.ui.stopCollect.setEnabled(False)
        self.ui.exportData.setEnabled(True)

        # self.new_loop.stop()

        terminate()


    def clearData(self):
        print("清空")
        self.ui.datalist.setRowCount(0)

    def exportData(self):
        self.ui.exportData.setEnabled(False)
        self.ui.startCollect.setEnabled(False)
        self.ui.clearData.setEnabled(False)
        print("导出")
        # wb = openpyxl.Workbook()
        columnHeaders = ["UID","账号","等级","昵称","粉丝数","关注数","性别","ip归属地","发言内容","secuid"]
        df = pd.DataFrame(columns=columnHeaders)
        print(df)

        rowcnt=self.ui.datalist.rowCount()
        if rowcnt<=0:
            QMessageBox.about(self,"消息提示","暂无数据，请先采集数据")
            self.ui.exportData.setEnabled(True)
            self.ui.startCollect.setEnabled(True)
            self.ui.clearData.setEnabled(True)
            return

        # create dataframe object recordset
        for row in range(self.ui.datalist.rowCount()):
            for col in range(self.ui.datalist.columnCount()):
                print(str(row)+"-"+str(col))
                item = self.ui.datalist.item(row, col)
                print(item)
                df.at[row, columnHeaders[col]] = item.text() if item is not None else ""

        date_date = datetime.strftime(datetime.now(), '%Y-%m-%d-%H:%M:%S')

        filename='./data/data_'+self.rootUrl+'_'+date_date+'.csv'
        df.to_csv(filename, index=True)

        writer=open('./data/readme','w')
        writer.write(filename)
        writer.close()

        # 好像不起作用
        while not os.path.exists(filename):
            print("等待写文件完成")
            time.sleep(1)

        QMessageBox.about(self, "消息提示", "导出成功，您可以点击右边->查看数据")
        self.ui.exportData.setEnabled(True)
        self.ui.startCollect.setEnabled(True)
        self.ui.clearData.setEnabled(True)

    def lookData(self):
        print("查看数据")

    # 接收子线路采集到的函数发过来的信号通知
    def collectCallback(self,data):
        # 将采集到的评论的填充到表格
        for i in range(len(data)):
            dt=data[i][10]
            if(dt in self.dataType):
                row_count = self.ui.datalist.rowCount()  # 返回当前行数(尾部)
                self.ui.datalist.insertRow(row_count)  # 尾部插入一行
                for j in range(0, len(data[i])):
                    self.ui.datalist.setItem(row_count, j , QtWidgets.QTableWidgetItem(str(data[i][j])))
                    if(self.ui.autoScroll.isChecked()):
                        self.ui.datalist.scrollToBottom()


    def get_loop(self,loop):
        self.loop=loop
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    # 点击采集按钮的调的函数，给子线路的信号发事件通知
    def startCollect(self):
        self.rootUrl=self.ui.lineEdit.text()
        if len(self.rootUrl) == 0 or self.rootUrl.isspace() == True:
            QMessageBox.about(self,"消息提示","先请输入直播间地址")
            return;
        self.ui.startCollect.setEnabled(False)
        self.ui.stopCollect.setEnabled(True)
        self.ui.exportData.setEnabled(False)

        self._thread = threading.Thread(target=DyCollectService, args=(self.tableSingal,self.rootUrl))
        self._thread.start()