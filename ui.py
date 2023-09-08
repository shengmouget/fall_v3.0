from PyQt5 import QtCore,QtGui,QtWidgets
import time 
import datetime
import sys
from PyQt5.QtWidgets import QWidget,QFileDialog
import cv2
from chiled_ui import Ui_Form
import pymysql
from tool.yolo_onnx import YOLO_ONNX
from tool.onnx_run import draw,filter_box

class Mywindow(QWidget,Ui_Form):
    def __init__(self):
        super(Mywindow,self).__init__()
        self.setupUi(self)
        self.setWindowTitle("跌倒检测系统")
        self.model = YOLO_ONNX("/home/neuedu/桌面/跌倒3.0/config/best-sim.onnx")  
        # 控制数据库连接
        self.conn = False
        self.flag_conn = False
        self.cap = cv2.VideoCapture()
        # 定时器
        self.timer = QtCore.QTimer()
        self.count = 0
        self.slot_init()

    def slot_init(self):
        self.connbtn.clicked.connect(self.connect_db)
        # 往数据库写数据
        # self.video_2.clicked.connect(self.save_sql)
        self.image_det.clicked.connect(self.open_img)
        self.video_2.clicked.connect(self.open_camera)
        self.timer.timeout.connect(self.show_camera)
        self.video_det.clicked.connect(self.open_video)
        self.closes.clicked.connect(app.exit)
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
    
    def save_sql(self,data):
        cursor = self.conn.cursor()
        now = datetime.datetime.now()
        time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        data = {
        "time":time_str,
        "coords":str(data["box"]),
        "status":str(data["class"]),
        }
        sql = "insert into falldata(time,coords,status) values(%(time)s,%(coords)s,%(status)s)"
        cursor.execute(sql,data)
        self.conn.commit()
        print("保存成功")

    # 打开图片
    def open_img(self):
        self.img , _= QtWidgets.QFileDialog.getOpenFileName(self, '选择图片', '.', '*.jpg;;*.png;;All Files(*)')
        print(self.img)
        if self.img:
            self.zhuangtai.setText("文件打开成功:\n" + self.img)
            if self.timer.isActive():
                self.cap.release()
                self.timer.stop()
                self.video.clear()
            img = QtGui.QPixmap(self.img).scaled(self.video.width(),self.video.height())
            print(img.size())
            self.video.setPixmap(QtGui.QPixmap(img))
        else:
            self.zhuangtai.setText("文件打开失败\n" )
    
    # 打开摄像头
    def open_camera(self):
        if self.timer.isActive() == False:
            flag = self.cap.open(0)
            if flag == False:
                QtWidgets.QMessageBox.warning(self,'warning',"未找到摄像头",buttons=QtWidgets.QMessageBox.Ok)
            else:
                self.timer.start(30)
                self.video_2.setText("关闭摄像头")
                self.image_det.setEnabled(False)
                self.video_det.setEnabled(False)
        else:
            self.timer.stop()
            self.cap.release()
            self.video.clear()
            self.count = 0
            self.video_2.setText("打开摄像头")
            self.image_det.setEnabled(True)
            self.video_det.setEnabled(True)
    # 展示
    def show_camera(self):
        self.label.setText("无跌倒目标")
        self.label_4.setText(" ")
        self.label.setStyleSheet("font: 18pt \"Ubuntu\";\n"
"background-color:rgb(52, 101, 164)")
        _,image = self.cap.read()
        self.count += 1 
        image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        image = cv2.resize(image,(640,640))
        output,_  = self.model.inference(image)
        outbox = filter_box(output,0.5,0.7)
        if outbox.shape[0] > 0:
            data = draw(image,outbox,self.count,200)
            if self.flag_conn:
                self.save_sql(data)
            if 2 in data["class"]:
                self.label.setText("有人跌倒啦")
                self.label.setStyleSheet("font: 18pt \"Ubuntu\";\n"
"background-color:rgb(255, 0, 0)")
            self.label_4.setText(str(data["dict_str"]))
        # 根据image创建pyQT中的图片
        showImage = QtGui.QImage(image.data,image.shape[1],image.shape[0],QtGui.QImage.Format_RGB888) #把读取到的视频数据变成QImage形式
        self.video.setPixmap(QtGui.QPixmap.fromImage(showImage))  #往显示视频的Label里 显示QImage
            

    # 打开视频文件
    def open_video(self):
        video_name,_ = QFileDialog.getOpenFileName(self, "打开视频", "C:/", "*.mp4;;*.avi;;All Files(*)")
        if video_name:
            self.zhuangtai.setText("视频打开成功" + video_name)
            flag = self.cap.open(video_name)
            if flag == False:
                QtWidgets.QMessageBox.warning(self, "warning", "打开视频失败",
                                              QtWidgets.QMessageBox.Yes)
            else:
                self.timer.start(1000)  # 视频播放
                self.timer.timeout.connect(self.show_video)
        else:
            self.zhuangtai.setText("视频打开失败")
    # 展示
    def show_video(self):
        ret,image = self.cap.read()
        if ret:
            image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
            image = cv2.resize(image,(640,640))
            # 根据image创建pyQT中的图片
            showImage = QtGui.QImage(image.data,image.shape[1],image.shape[0],QtGui.QImage.Format_RGB888) #把读取到的视频数据变成QImage形式
            self.video.setPixmap(QtGui.QPixmap.fromImage(showImage))  #往显示视频的Label里 显示QImage
        else:
            self.cap.release()
            self.timer.stop()
            self.zhuangtai.setText("视频播放结束")
           

        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = Mywindow()
    ui.show()
    sys.exit(app.exec_())