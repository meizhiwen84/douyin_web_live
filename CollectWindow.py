import asyncio
import csv
import os
import signal
import threading
import time
from datetime import datetime

import pandas as pd

from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QMessageBox, QDesktopWidget

# 采集主界面
# from CollectThread import CollectThread
# import DouyinSpider as ds
from collectmain import DyCollectService
from collectmain import terminate


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
        self.ui=uic.loadUi("./ui/dy1.ui")
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

        # self.dyScrapy=DyScrapy(self.)

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
        columnHeaders = ["UID","账号","等级","昵称","蓝V","粉丝数","关注数","获赞数","作品数","性别","ip归属地","发言次数","发言内容"]
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
        # data = self.con.selectData('select * from userManagement')
        for i in range(len(data)):
            row_count = self.ui.datalist.rowCount()  # 返回当前行数(尾部)
            self.ui.datalist.insertRow(row_count)  # 尾部插入一行
            for j in range(0, len(data[i])):
                self.ui.datalist.setItem(row_count, j , QtWidgets.QTableWidgetItem(str(data[i][j])))
                self.ui.datalist.scrollToBottom()
                # self.ui.repaint()


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

        # coroutine1=ds.main(self.tableSingal,self.rootUrl)
        # self.new_loop = asyncio.new_event_loop();
        # t = threading.Thread(target=self.get_loop, args=(self.new_loop,))
        # t.start()
        #
        # asyncio.run_coroutine_threadsafe(coroutine1, self.new_loop)
        # asyncio.run(coroutine1)

        print(1)
        # 给采集线程的自定义线程发事件通知
        # self.collectThread.startCollectSignal.emit(self.rootUrl)