from PyQt5 import QtCore,QtGui,QtWidgets
import time 
import datetime
import sys
from PyQt5.QtWidgets import QWidget
import cv2
from chiled_ui import Ui_Form
import pymysql

class Mywindow(QWidget,Ui_Form):
    def __init__(self):
        super(Mywindow,self).__init__()
        self.setupUi(self)
        self.setWindowTitle("跌倒检测系统")
        # 控制数据库连接
        self.conn = False
        self.flag_conn = False
        self.slot_init()

    def slot_init(self):
        self.connbtn.clicked.connect(self.connect_db)
        # 往数据库写数据
        # self.video_2.clicked.connect(self.save_sql)
    # 数据库连接函数
    def connect_db(self):
        if self.flag_conn == False:
            try:
                self.conn = pymysql.connect(
                    host='116.204.108.181',
                    port=3306,
                    user='root',
                    passwd='shengwei',
                    db='neuedu'
                    )
                self.connbtn.setText("关闭通信")
                self.zhuangtai.setText("通道信息开放")
                self.flag_conn = True
            except pymysql.Error as e :
                msg = QtWidgets.QMessageBox.warning(self,'warning',"请检查数据库",buttons=QtWidgets.QMessageBox.Ok)
        else:
            # self.conn.close()
            self.connbtn.setText("开启通信")
            self.zhuangtai.setText("关闭通道信息成功")
            self.conn = False
            self.flag_conn = False
    
    def save_sql(self):
        cursor = self.conn.cursor()
        now = datetime.datetime.now()
        time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        data = {
        "time":time_str,
        "coords":'[2.34,5.67]',
        "status":'01',
        }
        sql = "insert into falldata(time,coords,status) values(%(time)s,%(coords)s,%(status)s)"
        cursor.execute(sql,data)
        self.conn.commit()
        print("保存成功")






if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = Mywindow()
    ui.show()
    sys.exit(app.exec_())