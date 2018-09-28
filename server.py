'''
name 
data 2018-9-28
modules:
python3.5
This is a dict project for AID
'''
from socket import *
from signal import *
from mysqlpython import *
import sys,os,traceback,time
import pymysql
# 流程控制
def main():
    # 创建数据库连接
    db = pymysql.connect\
    ("localhost",'root','123456',"dict")
    # 创建套接字
    s = socket()
    s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    s.bind(("0.0.0.0",8000))
    s.listen(5)
    # 忽略子进程信号
    signal(SIGCHLD,SIG_IGN)
    while True:
        try:
            # 客户端连接
            c,addr = s.accept()
            print("连接到",addr)
        except KeyboardInterrupt:
            s.close()
            sys.exit("服务器退出")
        except Exception:
            traceback.print_exc()
            continue
        # 创建父子进程
        pid = os.fork()
        if pid == 0:
            s.close()
            do_child(c,db)
        else:
            c.close()
            continue
def do_child(c,db):
    # 循环接收客户端请求
    while True:
        data = c.recv(1024).decode()
        if data[0] == "L":
            do_login(c,db,data)
        elif data[0] == "H":
            do_hist(c,db,data)
        elif data[0] == "Q":
            c.close()
            sys.exit("客户端退出")
        elif data[0] == "R":
            do_register(c,db,data)
        elif data[0] == "q":
            do_query(c,db,data)

# 用户登录
def do_login(c,db,data):
    l = data.split(" ")
    name = l[1]　#用户名
    passwd = l[2] #密码
    cursor = db.cursor()
    sql = "select name,passwd from user where name='%s'" % name
    cursor.execute(sql)
    r = cursor.fetchone()
    if r == None:
        # 没有查找到这个用户名
        c.send(b"FALSE")
        # 查到到用户名进行密码匹配
    elif r[1] == passwd:
        c.send(b"OK")
        # 密码匹配失败
    else:
        c.send(b"AILL")

# 用户注册
def do_register(c,db,data):
    l = data.split(' ')
    name = l[1]
    passwd = l[2]
    cursor = db.cursor()
    sql = "select name from user where name='%s'" % name
    cursor.execute(sql)
    r = cursor.fetchone()
    if r != None:
        c.send(b"EXISTS")
        return
    sql = "insert into user(name,passwd) values ('%s','%s')" % (name,passwd)
    # 进行异常判断
    try:
        cursor.execute(sql)
        db.commit()
        c.send(b"OK")
    except:
        db.rollback()
        c.send(b"False")

# 单词查询
def do_query(c,db,data):
    l = data.split(' ')
    name = l[1]
    word = l[2]
    cursor = db.cursor()
    # 查询记录插入
    def insert_history():
        tm = time.ctime()
        sql = "insert into hist (name,word,time) values ('%s','%s','%s')" % (name,word,tm)
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback

    # 数据库查询
    while True:
        sql = "select * from words where word='%s'" % word
        cursor.execute(sql)
        r = cursor.fetchone()
        if not r:
            c.send(b"FALL")
            return
        else:
            c.send(b"OK")
            time.sleep(0.1)
            c.send(str(r[2]).encode())
            insert_history()
            return


# 历史记录查询
def do_hist(c,db,data):
    l = data.split(' ')
    name = l[1]
    cursor = db.cursor() 
    sql = "select * from hist where name = '%s' order by time desc limit 5" % name
    cursor.execute(sql)
    r = cursor.fetchall()
    if not r:
        c.send(b"FALL")
    else:
        c.send(b"OK")
        time.sleep(0.1)
    for i in r:
        time.sleep(0.01)
        msg = "%s  %s  %s" % (i[1],i[2],i[3])
        c.send(msg.encode())
    time.sleep(0.1)
    c.send(b"##")

if __name__ == "__main__":
    main()