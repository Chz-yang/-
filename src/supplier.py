#!/usr/bin/python3
# !encoding=utf-8
import pyodbc
import hashlib
import time
import threading
import os
import json


class Supplier():
    ''' class of supplier '''
    def __init__(self, id, cursor):
        self.id = id
        self.cursor = cursor
        self.quit = False
        self.lock = threading.Lock()
        self.todoOrders = {}

    def updateSales(self, order_id):
        ''' update sales of dishes '''
        self.cursor.execute('''UPDATE Dishes
                               set Dishes.sales = Dishes.sales + 1
                               where Dishes.dishes_id in(
                                   select Orders_Dishes.dishes_id
                                   from Orders_Dishes
                                   where Orders_Dishes.order_id = ?
                               )
                            ''', order_id)
        self.cursor.commit()

    def activity(self):
        print(">> 请做出选择： ")
        while True:
            option = input("\n>> 处理订单请按 c， 添加菜式请按 d\n"
                           ">> 添加地址请按 a， 退出请按 q: ")
            if option == 'c':  # check orders
                self.handleOrders()

            elif option == 'd':   # add dishes
                self.addDishes()

            elif option == 'a':   # add contacts
                self.addContact()

            elif option == 'q':   # quit
                self.quit = True
                return False
        return True

    def handleOrders(self):
        ''' handle orders to to delivering '''
        self.lock.acquire()
        if len(self.todoOrders) == 0:
            print("\n>> 暂时没有订单需要处理！")
        else:
            for orders in self.todoOrders:
                # print(orders, orders[0], type(orders[0]))
                self.updateSales(orders[0])
                self.cursor.execute("UPDATE Orders set Orders.state = 'to_deliver' where Orders.order_id = " + orders[0])
                print('>> 处理订单', orders, '成功，订单待派送！')
                # self.cursor.execute('''
                #                     UPDATE Orders set Orders.state ='to_delivering'
                #                     where Orders.order_id = ? ''', orders[0])
                self.cursor.commit()
            self.todoOrders = []

        self.lock.release()
        pass

    def addDishes(self):
        ''' add dishes '''
        self.showDishes()

        while True:
            choice = input("\n>> 添加菜式请按：a; 退出请按 q :")
            if choice == 'a':
                features = ["菜名", "零售价", "备注"]  # 输入属性
                values = [None, None, None]  # 输入值(密码、姓名、电话号码)
                no = 0  # 输入顺序
                while no < 3:
                    values[no] = validInput(features[no], no)
                    if values[no] == 'b': # 回退到上一步
                        no = no - 1
                    elif values[no] == 'q':   # 退出输入
                        return
                    else:
                        no = no + 1

                self.cursor.execute("SELECT count(*) FROM Dishes")
                count = cursor.fetchone()
                dishes_id = str(count[0]) # 假设contact ID从0开始

                # print(dishes_id, values[0], float(values[1]), 0, values[2])
                self.cursor.execute('''
                                    insert into Dishes values
                                    (?, ?, ?, 0, ?)''',
                                    dishes_id, values[0], float(values[1]), values[2])
                self.cursor.commit()

                self.cursor.execute('''
                                    insert into Supp_Dishes values
                                    (?, ?)''', self.id, dishes_id)
                self.cursor.commit()
                print('>> 菜式', values[0], '已插入！')

            elif choice == 'q':
                return

    def addContact(self):
        self.showContact()
        while True:
            choice = input("\n>> 添加联系表请按 a; 退出请按 q:")
            if choice == 'a':
                features = ["电话", "地址", "联系人"]  # 输入属性
                values = [None, None, None]  # 输入值(密码、姓名、电话号码)
                no = 0  # 输入顺序
                while no < 3:
                    values[no] = validInput(features[no], no)
                    if values[no] == 'b': # 回退到上一步
                        no = no - 1
                    elif values[no] == 'q':   # 退出输入
                        return
                    else:
                        no = no + 1

                self.cursor.execute("SELECT count(*) FROM Contact")
                count = cursor.fetchone()
                contact_id = str(count[0]) # 假设contact ID从0开始

                self.cursor.execute('''
                                    insert into Contact values
                                    (?, ?, ?, ?)''',
                                    contact_id, values[0], values[1], values[2])
                self.cursor.commit()

                self.cursor.execute('''
                                    insert into Supp_Contact values
                                    (?, ?)''', self.id, contact_id)
                self.cursor.commit()
                print('>> 插入联系表成功！')

            elif choice == 'q':
                return

    def showDishes(self):
        ''' show current dishes '''
        self.cursor.execute('''
                            select *
                            from Dishes
                            where dishes_id in
                                (select dishes_id
                                from Supp_Dishes
                                where supp_id = ?)''', self.id)
        dishes = self.cursor.fetchall()
        if len(dishes) == 0:
            print("\n>> 您的商店目前没有菜式!")
        else:
            print('\n>> 您当前的菜式如下:')
            for dish in dishes:
                print('>>> 菜名:', dish[1], ', 零售价:', dish[2], ', 销量:', dish[3], ', 备注:', dish[4])

    def showContact(self):
        ''' show current contact '''

        self.cursor.execute('''
                            select * 
                            from Contact
                            where contact_id in
                                (select contact_id
                                from Supp_Contact
                                where supp_id = ?)''', self.id)
        contacts = self.cursor.fetchall()
        if len(contacts) == 0:
            print("\n>> 您目前还没有联系表!")
        else:
            print('\n>> 您当前的联系表如下:')
            for contact in contacts:
                print('>>> 电话:', contact[1], ', 地址:', contact[2], ', 收件人:', contact[3])

    def checkOrders(self):
        ''' check orders per 10 seconds '''
        while True:
            if self.quit is True:
                return
            # print('check orders')
            self.cursor.execute('''
                                select *
                                from Supp_Orders, Orders
                                where  Supp_Orders.supp_id = ? and
                                       Supp_Orders.order_id = Orders.order_id and
                                       Orders.state = 'to_do' ''', self.id)
            self.lock.acquire()
            self.todoOrders = self.cursor.fetchall()
            self.lock.release()
            time.sleep(5)


def validInput(feature, no):
    '''
    输入属性feature的合法值，序号（顺序）为no
    '''
    msg1 = ">> 请输入 " + feature + "， 想要退出请按 q.\n>> "
    msg2 = ">> 你的 " + feature + " 不能为空."

    while True:
        value = input(msg1)
        if value == '':
            print(msg2)
        else:
            return value


if __name__ == '__main__':
    conn = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server};SERVER=localhost\MSSQLSERVER01;DATABASE=TakeOut;Trusted_Connection=yes;')
    cursor = conn.cursor()
    login = False   # 登录状态
    while not login:
        try:
            option = input(">> 登录请按 1， 注册请按 2，退出请按 3。\n>> ")
            if option == '1':                
                supp_id = input(">> 请输入您的id:\n>> ")
                password = input(">> 请输入您的密码\n>> ")
                sha1 = hashlib.sha1()
                sha1.update(password.encode('utf-8'))
                hash_pwd = sha1.hexdigest() # 密码的哈希值
                cursor.execute("SELECT password FROM Supplier WHERE Supplier.supp_id = " + supp_id)
                if cursor.fetchall()[0][0] == hash_pwd:
                    print(">> 欢迎回来~ ")
                    login = True
                else:
                    print(">> 密码错误！ ")

            elif option == '2':
                cursor.execute("SELECT count(*) FROM Supplier")
                count = cursor.fetchone()
                supp_id = str(count[0]) # 假设ID从0开始
                # print(supp_id, type(supp_id))
                print(">> 您的id为: " + supp_id)

                features = ["密码", "姓名"] #输入属性
                values = [None, None] # 输入值(密码、姓名、电话号码)
                no = 0  # 输入顺序
                while no < 2:
                    values[no] = validInput(features[no], no)
                    if values[no] == 'b': # 回退到上一步
                        no = no - 1
                    elif values[no] == 'q':   # 退出程序
                        exit()
                    else:
                        no = no + 1

                sha1 = hashlib.sha1()
                sha1.update(values[0].encode('utf-8'))
                hash_pwd = sha1.hexdigest()  # 密码的哈希值
                try:
                    cursor.execute(''' 
                                    insert into Supplier values
                                    (?, ?, ?, 0, ?)
                                   ''', supp_id, hash_pwd, values[1], 5)
                    cursor.commit()
                    print(">> 注册成功. 请记住您的id: " + supp_id + " ，密码: " + values[0])    # 创建成功
                    login = True
                except Exception as e:
                    print(e)
                    print(">> 注册失败，请重试！ ")  # 创建失败
            elif option == '3':
                exit()
                    
        except IndexError:
            print(">> 账号不存在！ ")

    suppl = Supplier(supp_id, cursor)
    t = threading.Thread(target=suppl.checkOrders)
    t.start()
    while True:
        if not suppl.activity():    # 主线程
            print("\n>> 感谢使用！再见~. ")
            t.join()
            # print('bye')
            exit()
