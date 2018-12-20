import pyodbc
import hashlib
import string

class Database():
    def __init__(self):
        self.conn = pyodbc.connect(
                                   'DRIVER={ODBC Driver 17 for SQL Server};\
                                    SERVER=127.0.0.1;port=1433;\
                                    DATABASE=TakeOut;UID=sa;PWD=Yy7758258')
        self.cursor = self.conn.cursor()
    
    def execute(self, sentence):
        try:
            self.cursor.execute(sentence)
        except:
            print("Invalid sentence")
            return None
    
    def query(self, sentence):
        self.execute(sentence)
        return self.cursor.fetchall()

class Customer():
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def showMenu(self):
        print("")

    @staticmethod
    def isValidIdFormat(id):
        database = Database()
        if (len(id) <= 20 and id.isalnum()):
            if len(database.query("SELECT cust_id FROM Customer WHERE cust_id = \'" + id + "\'")) == 0:
                return True
        return False
    
    @staticmethod
    def isValidIdInDatabase(id):
        database = Database()
        return len(database.query("SELECT cust_id FROM Customer WHERE cust_id = \'" + id + "\'")) != 0

    @staticmethod
    def addNewCustomer(id, password_hash, name):
        database = Database()
        database.execute("INSERT INTO Customer(cust_id, password, name) VALUES (\'" + id + "\', \'" + password_hash + "\', \'" + name + "\')")
        database.conn.commit()

    @staticmethod
    def isValidAccountInDatabase(id, password_hash):
        database = Database()
        return len(database.query("SELECT * FROM Customer WHERE cust_id = \'" + id + "\' AND password = \'" + password_hash + "\'")) != 0

    @staticmethod
    def getCustomerName(id):
        database = Database()
        return database.query("SELECT name FROM Customer WHERE cust_id = \'" + id + "\'")[0][0]

if __name__ == "__main__":
    print("***************************************")
    print("*************** O: 注册 ***************")
    print("*************** 1: 登录 ***************")
    print("*************** q: 退出 ***************")
    print("***************************************")
    print("请输入您的选项: ", end="")
    choice = input()
    while (choice != '0' and choice != '1' and choice != 'q'):
        print("输入非法，请重新输入: ", end="")
        choice = input()
    
    # register
    if (choice == '0'):
        id = input("请输入您的注册ID（只能使用数字和字母）: ")
        while (Customer.isValidIdFormat(id) == False):
            id = input("注册ID不合法或者已存在，请重新输入: ")
        password = input("请输入您的账号密码（只能使用数字和字母）: ")
        password_hash = hashlib.sha1(password.encode()).hexdigest()
        name = input("请输入您的账号名称: ")
        Customer.addNewCustomer(id, password_hash, name)
    # login
    elif (choice == '1'):
        id = input("请输入您的登录ID：")
        while (Customer.isValidIdInDatabase(id) == False):
            id = input("对不起，该ID不存在，请检查并重新输入：")
        password = input("请输入您的账号密码：")
        password_hash = hashlib.sha1(password.encode()).hexdigest()
        while (Customer.isValidAccountInDatabase(id, password_hash) == False):
            password = input("对不起，密码错误！请重新输入：")
            password_hash = hashlib.sha1(password.encode()).hexdigest()
        name = Customer.getCustomerName(id)
        print("\n")
        print("***************************************")
        print("************** 登录成功 ***************")
        print("***************************************")
        print("欢迎回来！ " + name + " 先生（小姐）～")
        customer = Customer(id, name)
