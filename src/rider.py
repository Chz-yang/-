#!/usr/bin/python3
#!encoding=utf-8

import pyodbc
import hashlib
import time
import threading
import os
import json

# conn = pyodbc.connect('DSN=project; DATABASE=TakeOut; UID=sa; PWD=123456')
# cursor = conn.cursor()

class Rider():
    def __init__(self, id, password, cursor):
        self.id = id
        self.password = password
        self.cursor = cursor
        path = os.path.split(os.path.realpath(__file__))[0] + "\\ordersDelivering.json"
        with open(path, 'r') as f:
            string = f.read()
            self.ordersDelivering = json.loads(string)
        # self.ordersDelivering = []  # 正在配送的订单(ID)
        self.remind = True
        self.quit = False

    def getOrdersMessage(self):
        while True:
            self.cursor.execute("SELECT * FROM Orders")
            orders = self.cursor.fetchall()
            diliver = False
            self.ordersToDeliver = dict() # 待配送订单
            for row in orders:
                if row[5] == 'to_deliver':
                    self.ordersToDeliver[row[0]] = (row[3], row[4])    # (supp_contact_id, cust_contact_id)
                    diliver = True
            if diliver and self.remind:    # 有新订单而且骑手接收新订单提醒
                print("You have new Orders.\n>> ", end="")
            
            time.sleep(10)  # 每隔10秒执行1次
            if self.quit == True:   # 退出程序
                return
    
    def activity(self):
        print(">> Please input your option. ")
        while True:
            option = input(">> 'c' for check; 'd' for deliver; 'f' for finish; 'r' for remind; 'n' for do not remind; 'q' for quit\n>> ")
            if option == 'c':
                if len(self.ordersToDeliver.keys()) == 0:
                    print(">> There are no new orders now. ")
                else:
                    for order_id in self.ordersToDeliver.keys():
                        print(">> Order_id: " + order_id, end=', ')

                        # 根据商家联系表ID获取商家地址
                        self.cursor.execute("SELECT address FROM Contact WHERE Contact.contact_id = " + self.ordersToDeliver[order_id][0])
                        supp_addr = self.cursor.fetchall()[0][0]
                        print("Supllier's address: " + supp_addr, end=', ')

                        # 根据顾客联系表ID获取顾客地址
                        self.cursor.execute("SELECT address FROM Contact WHERE Contact.contact_id = " + self.ordersToDeliver[order_id][1])
                        cust_addr = self.cursor.fetchall()[0][0]
                        print("Customer's address: " + cust_addr)
                break
            elif option == 'd':
                order_id = input(">> Please input the order's ID:\n>> ")
                if order_id not in self.ordersToDeliver.keys():
                    print(">> Sorry, there is not such order to deliver. ")
                else:
                    try:
                        self.cursor.execute("declare @success int; EXEC Proc_Deliver " + order_id + ", " + self.id + ", @success output; create table Temp(success int primary key); insert into Temp values(@success)")
                        self.cursor.commit()
                        self.cursor.execute("SELECT success FROM Temp") # 临时表存储返回变量success
                        success = self.cursor.fetchall()[0][0]
                        if success:
                            self.ordersDelivering.append(order_id)
                            print(">> You have received the order. ")
                        else:
                            print(">> Sorry, the order have been received. ")
                        self.cursor.execute("DROP TABLE Temp")  # 删除临时表
                        self.cursor.commit()
                    except Exception as e:
                        print(repr(e))
                break
            elif option == 'f':
                print(">> Your orders'id: " + str(self.ordersDelivering))
                order_id = input(">> Please input the order's ID: \n>> ")
                if order_id not in self.ordersDelivering:
                    print(">> Sorry, you are not delivering this order. ")
                else:
                    self.cursor.execute("UPDATE Orders SET Orders.state = 'done' WHERE Order_id = " + order_id) # 更新订单状态为done
                    self.cursor.commit()
                    print(">> OK. You have finished this order. Thanks.")
                break
            elif option == 'r':
                self.remind = True  # 接收提醒
                break
            elif option == 'n':
                self.remind = False # 不接收提醒
                break
            elif option == 'q':
                self.quit = True    # 退出程序
                path = os.path.split(os.path.realpath(__file__))[0] + "\\ordersDelivering.json"
                with open(path, 'w') as f:
                    json.dump(self.ordersDelivering, f) 
                return False
        return True      

def validInput(feature, no):
    '''
    输入属性feature的合法值，序号（顺序）为no
    '''
    if no > 0:
        msg1 = ">> Please input your " + feature + ". Or input 'b' for backward or 'q' for quit.\n>> "
        msg2 = ">> Your " + feature + "cannot be empty."
    elif no == 0:
        msg1 = ">> Please input your " + feature + ". Or input 'q' for quit.\n>> "
        msg2 = ">> Your " + feature + " cannot be empty."

    while True:
        value = input(msg1)
        if value == '':
            print(msg2)
        else:
            return value


if __name__ == '__main__':
    conn = pyodbc.connect('DSN=project; DATABASE=TakeOut; UID=sa; PWD=123456')  # 连接服务器
    cursor = conn.cursor()
    login = False   # 登录状态
    while not login:
        try:
            option = input(">> Please input 1 for login or 2 for register or 3 for quit.\n>> ")
            if option == '1':                
                rider_id = input(">> Please input your id:\n>> ")
                password = input(">> Please input your password.\n>> ")
                sha1 = hashlib.sha1()
                sha1.update(password.encode('utf-8'))
                hash_pwd = sha1.hexdigest() # 密码的哈希值
                cursor.execute("SELECT password FROM Rider WHERE Rider.rider_id = " + rider_id)
                if cursor.fetchall()[0][0] == hash_pwd:
                    print(">> Welcome back. ")
                    login = True
                else:
                    print(">> Wrong Password! ")
            elif option == '2':
                cursor.execute("SELECT rider_id FROM Rider")
                RiderIDs = cursor.fetchall()
                rider_id = str(len(RiderIDs))   # 假设ID从0开始
                print(">> Your new ID: " + rider_id)
                # while True: # 输入密码
                #     password = input(">> Please input your password.\n>> ")
                #     if password == '':
                #         print(">> Your password cannot be empty. If you want to quit, please input 'q'. ")
                #     elif password == 'q':
                #         exit()
                #     else:
                #         break
                # while True: # 输入名字
                #     name = input(">> Please input your name.\n>> ")
                #     if name == '':
                #         print(">> Your name cannot be empty. If you want to quit, please input 'q'. ")
                #     elif name == 'q':
                #         exit()
                #     else:
                #         break
                # while True: # 输入电话号码
                #     telephone_no = input(">> PLease input your telephone number.\n>> ")
                #     if telephone_no == '':
                #         print(">> Your telephone number cannot be empty. If you want to quit, please input 'q'. ")
                #     elif telephone_no == 'q':
                #         exit()
                #     else:
                #         break
                features = ["password", "name", "telephone number"] #输入属性
                values = [None, None, None] # 输入值(密码、姓名、电话号码)
                no = 0  # 输入顺序
                while no < 3:
                    values[no] = validInput(features[no], no)
                    if values[no] == 'b': # 回退到上一步
                        no = no - 1
                    elif values[no] == 'q':   # 退出程序
                        exit()
                    else:
                        no = no + 1

                sha1 = hashlib.sha1()
                sha1.update(values[0].encode('utf-8'))
                hash_pwd = sha1.hexdigest() # 密码的哈希值
                try:
                    sql = "INSERT INTO Rider VALUES(\'" + rider_id + "\', \'" + hash_pwd + "\', \'" + values[1] + "\', \'" + values[2] + "\', 5);"
                    cursor.execute(sql)
                    cursor.commit()
                    print(">> Success. Please remember your ID: " + rider_id + " and password: " + values[0])    # 创建成功
                    login = True
                except Exception as e:
                    print(e)
                    print(">> Fail to register. Please try again. ")  # 创建失败
            elif option == '3':
                exit()
                    
        except IndexError:
            print(">> Nonexistent ID! ")

    rider = Rider(rider_id, password, cursor)
    t = threading.Thread(target=rider.getOrdersMessage) # 辅助线程
    t.start()
    while True:
        if not rider.activity():    # 主线程
            print(">> See you next time. ")
            break
    t.join()