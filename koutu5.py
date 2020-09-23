# 作者：教室工作室 
# 可以用来做二次开发，但请署名源代码出处
import os
import cv2
import sys
import numpy as np
from PIL import Image


from PyQt5.QtWidgets import *
from PyQt5 import QtGui, QtWidgets

import face_recognition


# 在百度云中申请，每天各接口有 50000 次调用限制.
from aip import AipBodyAnalysis
import requests
import base64

""" 你的 APPID AK SK """
APP_ID = '21664164'
API_KEY = '6BmoqUL4LMeGqDPXu3PQgI7p'  # 需要替换成你自己的 
SECRET_KEY = 'lkA3paiFbDCfDFE3bApeLhowg5MafWrH'  # 需要替换成你自己的 
client = AipBodyAnalysis(APP_ID, API_KEY, SECRET_KEY)

fileName_choose=""
dir_choose=""
font = QtGui.QFont()
font.setFamily('微软雅黑')
font.setBold(True)
font.setPointSize(13)
font.setWeight(75)
wob=True


def GetWhiteScreen(width, height,wpath):
    canvasbg  = np.zeros([width, height, 3], np.uint8)+255
    #cv2.imwrite(wpath, canvasbg)
    cv2.imencode('.jpg', canvasbg)[1].tofile(wpath)

def GetBlueScreen(width,height,wpath):
    canvasbg  = np.zeros([width, height, 3], np.uint8)
    canvasbg[:, :, 0] = np.zeros([width, height]) + 255
   # cv2.imwrite(wpath, canvasbg)
    cv2.imencode('.jpg', canvasbg)[1].tofile(wpath)

def Getface(source,output):
    image = face_recognition.load_image_file(source)
    # Find all the faces in the image using the default HOG-based model.
    # This method is fairly accurate, but not as accurate as the CNN model and not GPU accelerated.
    face_locations = face_recognition.face_locations(image)
    # face_locations = face_recognition.face_locations(image, number_of_times_to_upsample=0, model="cnn")
    print("I found {} face(s) in this photograph.".format(len(face_locations)))
    for face_location in face_locations:
        # Print the location of each face in this image
        top, right, bottom, left = face_location
        print("A face is located at pixel location Top: {}, Left: {}, Bottom: {}, Right: {}".format(top, left, bottom, right))
        # You can access the actual face itself like this:
        image=cv2.imdecode(np.fromfile(source,dtype=np.uint8),-1)
        #image = cv2.imread(source)      #从指定路径读取图像
        imagen = image[top-top//2-top//3:bottom+bottom//4,left-left//2:right+right//5] #获取感兴趣区域
      #  cv2.imwrite(output, imagen)
        cv2.imencode('.jpg', imagen)[1].tofile(output)


def BlendImg(fore_image, base_image, output_path):
    """
    将抠出的人物图像换背景
    fore_image: 前景图片，抠出的人物图片
    base_image: 背景图片
    """
    print("blend:")
    # 读入图片
    base_image = Image.open(base_image).convert('RGB')
    fore_image = Image.open(fore_image).resize(base_image.size)
    # 图片加权合成
    scope_map = np.array(fore_image)[:,:,-1] / 255
    scope_map = scope_map[:,:,np.newaxis]
    scope_map = np.repeat(scope_map, repeats=3, axis=2)
    res_image = np.multiply(scope_map, np.array(fore_image)[:,:,:3]) + np.multiply((1-scope_map), np.array(base_image))
    
    #保存图片
    res_image = Image.fromarray(np.uint8(res_image))
    res_image.save(output_path)

#  获取 access_token，通行证
def get_access_token():
    """
    获取 access_token
    """
    # 注*意 SK 与 AK
    # client_id 为官网获取的AK， client_secret 为官网获取的SK,其实就是API_KEY和SECRET_KEY
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=6BmoqUL4LMeGqDPXu3PQgI7p&client_secret=lkA3paiFbDCfDFE3bApeLhowg5MafWrH'
    response = requests.get(host)
    if response:
        return response.json()['access_token']

# 人像分割处理部分
def get_foreground(originalImagePath,outputpath):
    """
    人像分割
    """
    # 二进制方式打开图片文件
    f = open(originalImagePath, 'rb')
    img = base64.b64encode(f.read())
    # 请求 百度 AI 开放平台
    request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v1/body_seg?access_token=" + get_access_token()
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    params = {"image": img}
    response = requests.post(request_url, data=params, headers=headers)
    # 保存照片
    try:
        foreground = response.json()['foreground']
        img_data = base64.b64decode(foreground)
        img_path = outputpath # 保存照片地址和名称，修改处
        with open(img_path, 'wb') as f:
            f.write(img_data)
    except:
        pass
def koutu():
        global wob
        
        # 图片路径
        path = dir_choose
        
        # 判断路径是否存在
        if os.path.exists(path):
            files = os.listdir(path)
            for item in files:
                get_foreground(path + "/"+item,str(fileName_choose)+"/"+item)
            # 批量抠图
            print("---- 程序结束 ----")
        else:
            print("输入的路径不存在！！！")
            print("---- 程序结束 ----")
        
                # 图片路径
        
        path = fileName_choose
        
        # 判断路径是否存在
        if os.path.exists(path):
            files = os.listdir(path)
            #imgs = []
            for item in files:
                #img=cv2.imread(path + "/"+item,-1)
                img=cv2.imdecode(np.fromfile(path + "/"+item,dtype=np.uint8),cv2.IMREAD_UNCHANGED)
                print(item)
                #img_copy=img.copy()
                    # 第三步：生成绿幕并合成
                if wob==True:
                   print("white")
                   GetWhiteScreen(img.shape[0],img.shape[1],path+"/"+"白底"+item)
                   BlendImg(path + "/"+item,path+"/"+"白底"+item,path+"/"+"合成"+item)
                   Getface(path+"/"+"合成"+item,path+"/"+"最终"+item)
                   os.remove(path+"/"+"白底"+item)
                else:
                   print("blue")
                   GetBlueScreen(img.shape[0],img.shape[1],path+"/"+"蓝底"+item)
                   BlendImg(path + "/"+item,path+"/"+"蓝底"+item,path+"/"+"合成"+item)
                   try:
                       Getface(path+"/"+"合成"+item,path+"/"+"最终"+item)
                   except:
                       pass
                   os.remove(path+"/"+"白底"+item)
        
        print("完成!!!")

class MainForm(QWidget):
    def __init__(self, name = 'MainForm'):
        super(MainForm,self).__init__()
        self.setWindowTitle(name)
        self.cwd = os.getcwd() # 获取当前程序文件位置
        self.resize(700,400)   # 设置窗体大小
        # btn 1
        self.btn_chooseDir = QPushButton(self)  
        self.btn_chooseDir.setObjectName("btn_chooseDir")  
        self.btn_chooseDir.setText("选择源文件夹")
        self.btn_chooseDir.setFont(font)
        # btn 2
        self.btn_koutu = QPushButton(self)  
        self.btn_koutu.setObjectName("btn_chooseFile")  
        self.btn_koutu.setText("开始抠图")
        self.btn_koutu.setFont(font)
        # btn 4
        self.btn_saveFile = QPushButton(self)  
        self.btn_saveFile.setObjectName("btn_saveFile")  
        self.btn_saveFile.setText("选择文件保存目录")
        self.btn_saveFile.setFont(font)
        # btn 5
        self.btn1 = QRadioButton("白底")          #实例化一个选择的按钮
        self.btn1.setChecked(True)                   #设置按钮点点击状态
        self.btn1.toggled.connect(lambda:self.btnstate(self.btn1))   #绑定点击事件
        # btn 6
        self.btn2 =QRadioButton("蓝底")   
        #实例化第二个按钮
        self.btn2.toggled.connect(lambda:self.btnstate(self.btn2))    #绑定按钮事件
        # 设置布局
        layout = QVBoxLayout()
        layout.addWidget(self.btn_chooseDir)
       # layout.addWidget(self.btn_chooseMutiFile)
        layout.addWidget(self.btn_saveFile)
        layout.addWidget(self.btn_koutu)

        layout_h=QHBoxLayout()
        layout.addLayout(layout_h)
        layout_h.addWidget(self.btn1)                  #布局添加组件
        layout_h.addWidget(self.btn2)                  #布局添加第二个按钮
        self.setLayout(layout)
        # 设置信号
        self.btn_chooseDir.clicked.connect(self.slot_btn_chooseDir)
        self.btn_koutu.clicked.connect(self.slot_btn_koutu)
        #self.btn_chooseMutiFile.clicked.connect(self.slot_btn_chooseMutiFile)
        self.btn_saveFile.clicked.connect(self.slot_btn_saveFile) 
         

    def btnstate(self,btn):       #自定义点击事件函数
            global wob
            if btn.text()=="白底":
                if btn.isChecked() == True:
                    print( btn.text() + " is selected" )
                    wob=True
                else:
                    print( btn.text() + " is deselected" )
                    wob=False
            if btn.text()=="蓝底":
                if btn.isChecked()== True :
                    print( btn.text() + " is selected" )
                    wob=False
                else:
                    print( btn.text() + " is deselected" )
                    wob=True


    def slot_btn_chooseDir(self):
        global dir_choose
        dir_choose = QFileDialog.getExistingDirectory(self,  
                                    "选取文件夹",  
                                    self.cwd) # 起始路径

        if dir_choose == "":
            print("\n取消选择")
            return

        print("\n你选择的文件夹为:")
        print(dir_choose)


    def slot_btn_koutu(self):
        try:
            koutu()
        except Exception as e:
            print(e)

    def slot_btn_saveFile(self):
        global fileName_choose
        fileName_choose= QFileDialog.getExistingDirectory(self,  
                                    "选取文件夹",  
                                    self.cwd) # 输出路径

        if fileName_choose == "":
            print("\n取消选择")
            return

        print("\n你选择的文件夹为:")
        print(fileName_choose)



if __name__=="__main__":
    app = QApplication(sys.argv)
    mainForm = MainForm('自动批量抠图——教室工作室')
    mainForm.show()
    sys.exit(app.exec_())
