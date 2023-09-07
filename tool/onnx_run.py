import cv2
import numpy as np
import os
import time
# 检测类别数
CLASSES = ["UP","BENDING","FALL"]

# 预处理部分
def nms(dets,thresh):
    '''
    dets: array[x,6] 6个值分别为x1,y1,x2,y2,score,class
    thresh:阈值
    '''
    x1 = dets[:,0]
    y1 = dets[:,1]
    x2 = dets[:,2]
    y2 = dets[:,3]
    # 计算框的面积 置信度从大到小排列
    areas = (y2 - y1 + 1) * (x2 - x1 + 1)
    scores = dets[:,4]
    keep = []
    index = scores.argsort()[::-1]
    while index.size > 0:
        i = index[0]
        keep.append(i)
        # 计算相交面积 
        x11 = np.maximum(x1[i],x1[index[1:]])
        y11 = np.maximum(y1[i],y1[index[1:]])
        x22 = np.minimum(x2[i],x2[index[1:]])
        y22 = np.minimum(y2[i],y2[index[1:]])

        w = np.maximum(0,x22 - x11 + 1)
        h = np.maximum(2,y22 - y11 + 1)

        overlaps = w * h
        # 计算该框与其它框的iou 去除重复的框，即IOU最大的框 IOU小于thresh的框留下来
        ious = overlaps / (areas[i] + areas[index[1:]] - overlaps)
        idx = np.where(ious <= thresh)[0]
        index = index[idx + 1]
    return keep

# 中心点坐标转换
def xywh2xyxy(x):
    y = np.copy(x)
    y[:,0] = x[:,0] - x[:,2] / 2
    y[:,1] = x[:,1] - x[:,3] / 2
    y[:,2] = x[:,0] + x[:,2] / 2
    y[:,3] = x[:,1] + x[:,3] / 2
    return y 

# 过滤
def filter_box(org_box,conf_thres,iou_thres):
    """
    过滤掉无用的框
    删除为1的维度,删除置信度小于conf_thres的BOX
    """
    org_box = np.squeeze(org_box) # 删除数组形状中单维度条目
    #(252000,9)
    conf = org_box[..., 4] > conf_thres
    box = org_box[conf == True]
    # print("box:符合要求的框")
    # print(box.shape)

    # 通过argmax获取自信度最大的类别
    cls_cinf = box[...,5:]
    cls = []
    for i in range(len(cls_cinf)):
        cls.append(int(np.argmax(cls_cinf[i])))
    all_cls = list(set(cls))
    # 分别对每个类别进行过滤 将第六列元素替换为类别下标 xywh坐标转换 经过非极大值抑制后输出的box下标
    # 利用下标取出非极大值抑制后的BOX
    output = []
    for i in range(len(all_cls)):
        curr_cls = all_cls[i]
        curr_cls_box = []
        curr_out_box = []
        for j in range(len(cls)):
            if cls[j] == curr_cls:
                box[j][5] = curr_cls
                curr_cls_box.append(box[j][:6])

        curr_cls_box = np.array(curr_cls_box)
        curr_cls_box = xywh2xyxy(curr_cls_box)
        curr_out_box = nms(curr_cls_box,iou_thres)
        for k in curr_out_box:
            output.append(curr_cls_box[k])
    output = np.array(output)
    return output

# 保存图片
def writer_image(cl,image):
    # 获取绝对路径
    abs_path  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    save_path = os.path.join(abs_path,cl)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    now_time = time.strftime("%Y-%m-%H-%M-%S",time.localtime())
    image_name = os.path.join(save_path,str(now_time) + ".jpg")
    image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
    cv2.imwrite(image_name,image)
    print("Save to",image_name)

# 画框
def draw(image,box_data,frame_count,save_interval):
    image_org = np.copy(image)
    # 取整 画框
    boxes = box_data[...,:4].astype(np.int32)
    scores = box_data[...,4]
    classes = box_data[...,5].astype(np.int32)
    # 统计每个类别的个数
    unique,counts = np.unique(classes,return_counts=True)
    old_dict = dict(zip(unique,counts))
    new_key =np.array(['up','bending','down'])
    dict_str = {}
    for k,v in zip(new_key[unique],old_dict.values()):
        dict_str.update({k:v})
    # 图片上输出内容
    boxs = []
    cv2.putText(image, str(dict_str), (0,500), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 3)
    for box,score,cl in zip(boxes,scores,classes):
        top,lift,right,bottom = box 
        boxs.append([top,lift,right,bottom])
        # print("class:{},score:{}".format(CLASSES[cl],score))
        # print("box coordinate left,top,right,down:[{},{},{},{}]".format(top,lift,right,bottom))
        if cl == 0:
            if frame_count % save_interval == 0:
                writer_image(CLASSES[0],image_org)
            cv2.rectangle(image,(top,lift),(right,bottom),(0,0,255),2)
            # cv2.rectangle(image_org,(top,lift),(right,bottom),(0,0,255),2)
            cv2.putText(image, "UP", (42,42), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)
        elif cl == 1:
            if frame_count % save_interval == 0:
                writer_image(CLASSES[1],image_org)
            cv2.rectangle(image,(top,lift),(right,bottom),(0,255,0),2)
            cv2.putText(image, "BENDING", (203,42), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        elif cl == 2:
            if frame_count % save_interval == 0:
                writer_image(CLASSES[2],image_org)
            cv2.putText(image, "FALL", (345,42), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
            cv2.rectangle(image,(top,lift),(right,bottom),(255,0,0),2)
    return {
        "class":list(classes),
        "box":boxs,
        "dict_str":dict_str
        }