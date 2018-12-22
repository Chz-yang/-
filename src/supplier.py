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
        self.todoOrders = {}

    def activity(self):
        print(">> Please input your option. ")
        while True:
            option = input("\n>> 'c' to check Orders; 'd' to add dishes\n"
                           ">>  'a' to add contact; 'q' to quit: ")
            if option == 'c':  # check orders
                if len(self.todoOrders) == 0:
                    print("\n>> There are no orders to handle now.")
                else:
                    pass

            elif option == 'd':   # add dishes
                pass

            elif option == 'a':   # add contacts
                self.addContact()

            elif option == 'q':   # quit
                self.quit = True
                return False
        return True

    def addContact(self):
        self.showContact()
        while True:
            choice = input("\n>> 'a' to add new contact; 'q' to quit:")
            if choice == 'a':
                features = ["telephone", "address", "reciver_name"]  # 输入属性
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

            elif choice == 'q':
                return

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
            print("\n>> You don't have any contact now!")
        else:
            print('\n>> Here are you current contact:')
            for contact in contacts:
                print('>>> tele:', contact[1], 'addr:', contact[2], 'recvName:', contact[3])

    # def getContact(self):
    #     ''' get supplier's contact '''
    #     self.cursor.execute(''' 
    #                         select contact_id
    #                         from Supp_Contact
    #                         where supp_id = ?''', self.id)

    def checkOrders(self):
        # while True:
        #     self.cursor.execute('''
        #                         select * 
        #                         from Orders
        #                         where ''')
        pass


def validInput(feature, no):
    '''
    输入属性feature的合法值，序号（顺序）为no
    '''
    msg1 = ">> Please input your " + feature + ". Or input 'q' for quit.\n>> "
    msg2 = ">> Your " + feature + " cannot be empty."

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
            option = input(">> Please input 1 for login or 2 for register or 3 for quit.\n>> ")
            if option == '1':                
                supp_id = input(">> Please input your id:\n>> ")
                password = input(">> Please input your password.\n>> ")
                sha1 = hashlib.sha1()
                sha1.update(password.encode('utf-8'))
                hash_pwd = sha1.hexdigest() # 密码的哈希值
                cursor.execute("SELECT password FROM Supplier WHERE Supplier.supp_id = " + supp_id)
                if cursor.fetchall()[0][0] == hash_pwd:
                    print(">> Welcome back. ")
                    login = True
                else:
                    print(">> Wrong Password! ")

            elif option == '2':
                cursor.execute("SELECT count(*) FROM Supplier")
                count = cursor.fetchone()
                supp_id = str(count[0]) # 假设ID从0开始
                # print(supp_id, type(supp_id))
                print(">> Your new ID is: " + supp_id)

                features = ["password", "name"] #输入属性
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
                    print(">> Success. Please remember your ID: " + supp_id + " and password: " + values[0])    # 创建成功
                    login = True
                except Exception as e:
                    print(e)
                    print(">> Fail to register. Please try again. ")  # 创建失败
            elif option == '3':
                exit()
                    
        except IndexError:
            print(">> Nonexistent ID! ")

    suppl = Supplier(supp_id, cursor)
    t = threading.Thread(target=suppl.checkOrders)
    t.start()
    while True:
        if not suppl.activity():    # 主线程
            print("\n>> See you next time. ")
            break
    t.join()
