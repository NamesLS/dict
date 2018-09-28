#!/usr/bin/python3
#coding = utf-8
from socket import *
from main import *
import traceback,sys,getpass
def main():
    if len(sys.argv) < 3:
        print("error")
        return
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    ADDR = (HOST,PORT)
    s = socket()
    try:
        s.connect(ADDR)
    except:
        print("连接服务器失败")
        traceback.print_exc()
    while True:
        menu()
        try:
            cmd = input("请选择>>:")
        except KeyboardInterrupt:
            s.send(b"Q")
            sys.exit("退出")
        except Exception as e:
            print("命令错误")
            continue
        if cmd == "1":
            # 调用注册函数
            r = do_register(s)
            if r == 0:
                print("注册成功")
            elif r == 1:
                print("用户已存在")
            elif r == 2:
                print("注册失败")
        elif cmd == "2":
            # 调用登录函数
            name = do_login(s)
            if name:
                print("登录成功")
                while True:
                    menu1()
                    try:
                        cm = input("请输入>>:")
                    except KeyboardInterrupt:
                        s.send(b"Q")
                        sys.exit("退出")
                    except Exception as e:
                        print("命令错误")
                        continue
                    if cm == "1":
                        do_query(s,name)
                    elif cm == "2":
                        do_hist(s,name)
                    elif cm == "3":
                        break
                    else:
                        print("输入不合法")
            elif name == None:
                print("密码不正确")
            elif name == False:
                print("用户名不存在,请先注册")
                # 用户名不存在调用注册函数进行注册
                r = do_register(s)
                if r == 0:
                    print("注册成功")
                elif r == 1:
                    print("用户已存在")
                elif r == 2:
                    print("注册失败")
        elif cmd == "3":
            s.send(b"Q")
            sys.exit("谢谢使用")
        else:
            print("请输入正确选项")
            sys.stdin.flush() #清除标准输入
# 注册操作
def do_register(s):
    while True:
        name = input("请输入注册的用户名:")
        passwd = getpass.getpass("请输入密码:")
        passwd1 = getpass.getpass("确认输入密码:")
        if (" " in name) or (" " in passwd):
            print("用户名和密码不能有空格")
            continue
        if passwd != passwd1:
            print("两次输入密码不一致")
            continue
        msg = "R {} {}".format(name,passwd)
        s.send(msg.encode())
        data = s.recv(128).decode()
        if data == "OK":
            return 0
        elif data == "EXISTS":
            return 1
        else:
            return 2
# 登录操作
def do_login(s):
    while True:
        name = input("请输入用户名:")
        passwd = getpass.getpass("请输入密码:")
        msg = "L {} {}".format(name,passwd)
        s.send(msg.encode())
        data = s.recv(1024).decode()
        if data == "OK":
            return name
        elif data == "FALSE":
            return False
        elif data == "AILL":
            return None
# 单词查询
def do_query(s,name):
    while True:
        word = input("请输入单词:")
        if not word:
            break
        msg = "q {} {}".format(name,word)
        s.send(msg.encode())
        data = s.recv(128).decode()
        if data == "OK":
            data = s.recv(2048).decode()
            print(data)
        else:
            print("没有查到该单词")
            continue
# 历史记录
def do_hist(s,name):
    msg = "H {}".format(name)
    s.send(msg.encode())
    data = s.recv(1024).decode()
    if data == "OK":
        while True:
            data = s.recv(1024).decode()
            if data == "##":
                break
            print(data)
    else:
        print("没有历史记录")
    
if __name__ == "__main__":
    main()
