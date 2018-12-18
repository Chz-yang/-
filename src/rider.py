#!/usr/bin/python3
#!encoding=utf-8

import pyodbc
import time
import threading

# conn = pyodbc.connect('DSN=project; DATABASE=TakeOut; UID=sa; PWD=123456')
# cursor = conn.cursor()

class Rider():
    def __init__(self, id, password, cursor):
        self.id = id
        self.password = password
        self.cursor = cursor
        self.ordersDelivering = []  # 正在配送的订单(ID)
        self.remind = True
        self.quit = False

    def getOrdersMessage(self):
        while True:
            if self.remind:    # 接受新订单提醒
                self.cursor.execute("SELECT * FROM Orders")
                orders = self.cursor.fetchall()
                diliver = False
                self.ordersToDeliver = dict() # 待配送订单
                for row in orders:
                    if row[5] == 'to_deliver':
                        self.ordersToDeliver[row[0]] = (row[3], row[4])    # (supp_contact_id, cust_contact_id)
                        diliver = True
                if diliver:
                    print("You have new Orders.\n>> ", end="")
                
                time.sleep(10)  # 每隔10秒执行1次
            if self.quit == True:   # 退出程序
                return
    
    def activity(self):
        print(">> Please input your option. ")
        while True:
            option = input(">> 'c' for check; 'd' for deliver; 'f' for finish; ‘r' for remind; 'n for do not remind; ''q' for quit\n>> ")
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
                    # self.cursor.execute("")
                    # self.cursor.commit()
                    try:
                        self.cursor.execute("declare @success int; EXEC Proc_Deliver " + order_id + ", " + self.id + ", @success output; create table Temp(success int primary key);insert into Temp values(@success)")
                        self.cursor.commit()
                        self.cursor.execute("SELECT success FROM Temp") # 临时表存储返回变量success
                        success = self.cursor.fetchall()[0][0]
                        if success:
                            self.ordersDelivering.append(order_id)
                            print(">> You have received the order. ")
                        else:
                            print(">> Sorry, the order have been received. ")
                        self.cursor.execute("DROP TABLE Temp")  # 删除临时表
                    except Exception as e:
                        print(repr(e))
                break
            elif option == 'f':
                order_id = input(">> Please input the order's ID: \n>> ")
                if order_id not in self.ordersDelivering:
                    print(">> Sorry, you are not delivering this order. ")
                else:
                    self.cursor.execute("UPDATE Orders SET Orders.state = 'done'")
                    self.cursor.commit()
                    print(">> OK. You have finished this order. Thanks.")
                break
            elif option == 'r':
                self.remind = True  # 接收提醒
                break
            elif option == 'n':
                self.remind = False  # 不接受提醒
                break
            elif option == 'q':
                self.quit = True    # 退出程序
                return False
        return True      

if __name__ == '__main__':
    conn = pyodbc.connect('DSN=project; DATABASE=TakeOut; UID=sa; PWD=123456')
    cursor = conn.cursor()
    while True:
        try:
            rider_id = input(">> Please input your id:\n>> ")
            password = int(input(">> Please input your password.\n>> "))
            cursor.execute("SELECT password FROM Rider WHERE Rider.rider_id = " + rider_id)
            if cursor.fetchall()[0][0] == password:
                print(">> Welcome back. ")
                break
            else:
                print(">> Wrong id or wrong password. ")
        except ValueError:
            continue

    rider = Rider(rider_id, password, cursor)
    t = threading.Thread(target=rider.getOrdersMessage) # 辅助线程
    t.start()
    while True:
        if not rider.activity():    # 主线程
            print(">> See you next time. ")
            break
    t.join()