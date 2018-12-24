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
                print("您有新订单可以配送。\n>> ", end="")
            
            time.sleep(10)  # 每隔10秒执行1次
            if self.quit == True:   # 退出程序
                return
    
    def activity(self):
        print(">> 请输入您的选择")
        while True:
            option = input(">> 'c'：查看订单; 'd'：配送订单; 'f'：完成订单; 'r'：接收提醒; 'n'：关闭提醒; 'q'：退出系统\n>> ")
            if option == 'c':
                if len(self.ordersToDeliver.keys()) == 0:
                    print(">> 现在没有新订单。")
                else:
                    for order_id in self.ordersToDeliver.keys():
                        print(">> 订单号：" + order_id, end=', ')

                        # 根据商家联系表ID获取商家地址
                        self.cursor.execute("SELECT address FROM Contact WHERE Contact.contact_id = " + self.ordersToDeliver[order_id][0])
                        supp_addr = self.cursor.fetchall()[0][0]
                        print("商家地址：" + supp_addr, end=', ')

                        # 根据顾客联系表ID获取顾客地址
                        self.cursor.execute("SELECT address FROM Contact WHERE Contact.contact_id = " + self.ordersToDeliver[order_id][1])
                        cust_addr = self.cursor.fetchall()[0][0]
                        print("顾客地址：" + cust_addr)
                break
            elif option == 'd':
                order_id = input(">> 请输入订单号：\n>> ")
                if order_id not in self.ordersToDeliver.keys():
                    print(">> 对不起，您所选择的订单没有配送请求。")
                else:
                    try:
                        self.cursor.execute("declare @success int; EXEC Proc_Deliver " + order_id + ", " + self.id + ", @success output; create table Temp(success int primary key); insert into Temp values(@success)")
                        self.cursor.commit()
                        self.cursor.execute("SELECT success FROM Temp") # 临时表存储返回变量success
                        success = self.cursor.fetchall()[0][0]
                        if success:
                            self.ordersDelivering.append(order_id)
                            print(">> 您已成功接单。")
                        else:
                            print(">> 对不起，您所选择的订单已被配送。")
                        self.cursor.execute("DROP TABLE Temp")  # 删除临时表
                        self.cursor.commit()
                    except Exception as e:
                        print(repr(e))
                break
            elif option == 'f':
                print(">> 您所配送的订单号：" + str(self.ordersDelivering))
                order_id = input(">> 请输入您已完成配送的订单号：\n>> ")
                if order_id not in self.ordersDelivering:
                    print(">> 对不起，这不是您所配送的订单。")
                else:
                    self.cursor.execute("UPDATE Orders SET Orders.state = 'done' WHERE Order_id = " + order_id) # 更新订单状态为done
                    self.cursor.commit()
                    print(">> 您已成功送达该订单，谢谢。")
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
            option = input(">> 请输入您的选择  '1'：登录账户；'2'：注册账户；'3'：推出系统\n>> ")
            if option == '1':                
                rider_id = input(">> 请输入您的ID：\n>> ")
                password = input(">> 请输入您的密码：\n>> ")
                sha1 = hashlib.sha1()
                sha1.update(password.encode('utf-8'))
                hash_pwd = sha1.hexdigest() # 密码的哈希值
                cursor.execute("SELECT password FROM Rider WHERE Rider.rider_id = " + rider_id)
                if cursor.fetchall()[0][0] == hash_pwd:
                    print(">> 欢迎回来。")
                    login = True
                else:
                    print(">> 密码错误！")
            elif option == '2':
                cursor.execute("SELECT rider_id FROM Rider")
                RiderIDs = cursor.fetchall()
                rider_id = str(len(RiderIDs))   # 假设ID从0开始
                print(">> 您的ID：" + rider_id)
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
                    print(">> 成功。请记住您的账户ID：" + rider_id + " ；密码：" + values[0])    # 创建成功
                    login = True
                except Exception as e:
                    print(e)
                    print(">> 注册失败，请重新尝试。")  # 创建失败
            elif option == '3':
                exit()
                    
        except IndexError:
            print(">> 账户ID不存在！ ")

    rider = Rider(rider_id, password, cursor)
    t = threading.Thread(target=rider.getOrdersMessage) # 辅助线程
    t.start()
    while True:
        if not rider.activity():    # 主线程
            print(">> 下回见。")
            break
    t.join()