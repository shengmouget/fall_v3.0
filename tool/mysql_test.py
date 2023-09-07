# 读入数据库
import pymysql
import datetime
# 连接数据库
try:
    conn = pymysql.connect(
        host='116.204.108.181',
        port=3306,
        user='root',
        passwd='shengwei',
        db='neuedu'
    )
except pymysql.Error as e :
    print("连接失败" + str(e))

def save_sql():
    # 创建游标
    cursor = conn.cursor()
    # 获取上一条数据
    cursor.execute("select time from falldata limit 1")
    last_time = cursor.fetchone()[0]
    print(last_time)
    # 获取当前时间
    now = datetime.datetime.now()
    time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    # 获取时间差
    delta = now - last_time
    print(delta.seconds)
    # print(now)
    # 数据
    # data = {
    #     "time":time_str,
    #     "coords":'[2.34,5.67]',
    #     "status":'01',
    # }
    # # 插入数据
    # sql = "insert into falldata(time,coords,status) values(%(time)s,%(coords)s,%(status)s)"

    # cursor.execute(sql,data)
    # # 提交事务
    # conn.commit()

    # 关闭游标  
    conn.close()

save_sql()