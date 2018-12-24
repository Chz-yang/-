import pyodbc
import hashlib
import string

class Database():
    def __init__(self):
        self.conn = pyodbc.connect('DSN=project; DATABASE=TakeOut; UID=sa; PWD=123456')  # 连接服务器
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

    def commit(self):
        self.cursor.commit()

class Customer():
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def showMenu(self):
        print("\n***************************************")
        print("************* 1：查看商家 *************")
        print("************* 2：查看订单 *************")
        print("************* 3：个人设置 *************")
        print("************* q：退出    **************")
        print("***************************************")
        valid_input = ['1', '2', '3', 'q']
        print("请输入您的选项: ", end="")
        choice = input()
        while (choice not in valid_input):
            print("输入非法，请重新输入: ", end="")
            choice = input()
        if (choice == '1'):
            self.dealWithRequestShowSupplier()
        elif (choice == '2'):
            self.dealWithRequestShowOrders()
        elif (choice == '3'):
            self.dealWithRequestSetting()
        else:
            exit(0)

    def dealWithRequestShowSupplier(self):
        suppliers = Customer.getSuppliers()
        print("\n***************************************")
        print("目前一共有" + str(len(suppliers)) + "家商家注册：")
        index = 1
        for (supp_id, name, score) in suppliers:
            print(str(index) + ". \"" + name + "\", 评分：" + str(score))
            index += 1
        print("***************************************\n")
        print("请选择需要查看商家的所有菜式（'q'：返回上一层）：")
        choice = input()
        while (choice != 'q' and choice.isalnum() == False and int(choice) > len(suppliers)):
            print("输入非法，请重新输入: ", end="")
            choice = input()
        if (choice == 'q'):
            self.showMenu()
            return
        supplier = suppliers[int(choice) - 1]
        print("\n***************************************")
        dishes = Customer.getSupplierDishes(supplier[0])
        print("\"" + supplier[1] + "\"商家一共有" + str(len(dishes)) + "款菜式：")
        index = 1
        for dish in dishes:
            print(str(index) + ". 名字：" + dish[1] + "，单价：" + str(dish[1]) + "，销售量：" + str(dish[3]) + "，描述：" + dish[4])
            index += 1
        order_dishes = []
        choice = '2'
        while (choice == '2'):
            print("***************************************")
            print("请选择你想要订购的快餐（%d 到 %d）：" % (1, index  -1))
            choice = input()
            while (choice.isalnum() == False or int(choice) >= index):
                choice = input("你所选快餐不存在，请检查并重新输入：")
            order_dishes.append(dishes[int(choice) - 1])
            print("添加 \"" + dishes[int(choice) - 1][2] + "\" 成功！")
            print("***************************************")
            print("************* 1：结账    **************")
            print("************* 2：继续添加 **************")
            print("************* q：退出    ***************")
            print("***************************************")
            valid_input = ['1', '2', 'q']
            choice = input()
            while (choice not in valid_input):
                choice = input("输入非法，请重新输入：")
            if (choice == '1'):
                db = Database()
                contacts = db.query("SELECT * FROM Contact, Cust_Contact WHERE cust_id = \'" + str(self.cust_id) + "\' and Cust_Contact.contact_id = Contact.contact_id")
                if (len(contacts) == 0):
                    print("对不起，你还没有配送地址，请先增加配送地址：")
                contacts = db.query("SELECT * FROM Contact, Cust_Contact WHERE cust_id = \'" + str(self.cust_id) + "\' and Cust_Contact.contact_id = Contact.contact_id")
                index = 1
                for contact in contacts:
                    print(str(index) + ". 联系人名字：" + contact[3] + "，联系电话：" + contact[1] + "，配送地址：" + contact[2])
                    index += 1
                choice = input("请选择配送地址：")
                while (choice.isalnum() == False or int(choice) >= index):
                    choice = input("输入非法，请重新输入：")
                contact = contacts[int(choice) - 1]
                print("\n***************************************")
                print("你一共选购了" + str(len(order_dishes)) + "样快餐：")
                index = 1
                total_cost = 0
                for dish in order_dishes:
                    print(str(index) + ". 名字：" + dish[1] + "，单价：" + str(dish[1]))
                    index += 1
                    total_cost += dish[2]
                print("一共需要支付 " + str(total_cost + 2) + "(2元配送费) 元：")
                print("***************************************")
                print("************* 1：确认订单 **************")
                print("************* 2：取消订单 **************")
                print("************* q：退出    ***************")
                print("***************************************")
                valid_input = ['1', '2', 'q']
                choice = input()
                while (choice not in valid_input):
                    choice = input("输入非法，请重新输入：")
                if (choice == '1'):
                    print("\n***************************************")
                    print("支付成功！请耐心等待商家的配送。")
                    self.addOrder(supplier, contact, order_dishes, total_cost, 2)
                    self.showMenu()
                    return
                elif (choice == '2'):
                    self.showMenu()
                    return
                elif (choice == 'q'):
                    exit(0)
            elif (choice == 'q'):
                exit(0)

    def dealWithRequestShowOrders(self):
        orders = Database().query("SELECT * FROM Cust_Orders, Orders WHERE cust_id = \'" + str(self.id) + "\' and Cust_Orders.order_id = Orders.order_id")
        index = 1
        print("***************************************")
        for order in orders:
            contact = Database().query("SELECT * FROM Contact WHERE contact_id = " + str(order[4]))
            date = str(order[1])
            total_price = str(order[2])
            state = str(order[5])
            distribution_cost = str(order[6])
            print(str(index) + ". 时间：" + date + "，联系人：" + str(contact[-1]) + "，总价：" + str(total_price) + "，配送费：" + str(distribution_cost) + "，状态：" + Customer.stateMap(state) + "。")
            index += 1
        print("\n***************************************")
        print("********** 1：评价订单     ************")
        print("********** q：返回上一层   ************")
        valid_input = ['1', 'q']
        choice = input("请输入你的选项：")
        while (choice not in valid_input):
            choice = input("输入非法，请重新输入：")
        if (choice == '1'):
            print("\n***************************************")
            choice = input("请输入你要进行评价的订单：")
            if (choice.isalnum() == False or int(choice) > len(orders)):
                choice = input("所选订单不存在，请重新输入：")
            order = orders[int(choice) - 1]
            supp_score = float(input("请给商家打分："))
            rider_score = float(input("请给骑手打分："))
            comments = input("是否需要进行评论（是：直接输入评论内容；否：输入小写“n”并按回车）：")
            if (comments == 'n'):
                comments = "空"
            db = Database()
            db.execute("INSERT INTO Comments VALUES(\'" + str(order[0]) + "\', " + str(rider_score) + "\', \'" + str(supp_score) + "\', \'" + comments + "\')")
            db.commit()
            print("评价成功！")
        self.showMenu()

    def dealWithRequestSetting(self):
        print("\n***************************************")
        print("名字：" + str(self.name))
        print("********** 1：更改名字     ************")
        print("********** 2：更改密码     ************")
        print("********** 3：添加配送地址 ************")
        print("********** q：返回上一层   ************")
        valid_input = ['1', '2', '3', 'q']
        choice = input("请输入选项：")
        while (choice not in valid_input):
            choice = input("非法输入，请重新输入：")
        if (choice == '1'):
            print("\n***************************************")
            db = Database()
            new_name = input("请输入新名字：")
            print("更改成功！")
            self.name = new_name
            db.execute("UPDATE Customer SET name = \'" + new_name + "\' WHERE cust_id = \'" + str(self.id) + "\'")
            db.commit()
            self.dealWithRequestSetting()

        elif (choice == '2'):
            print("\n***************************************")
            db = Database()
            password = input("请输入原始密码：")
            password_hash = hashlib.sha1(password.encode()).hexdigest()
            count = 0
            while (Customer.isValidAccountInDatabase(self.id, password_hash) == False):
                password = input("密码错误，请重新输入（连续错误三次将强制退出）：")
                count += 1
                if (count == 3):
                    print("\n***************************************")
                    print("密码连续输错三次，你已被强制登出！")
                    exit(0)
            new_password = input("请输入新密码：")
            new_password_hash = hashlib.sha1(new_password.encode()).hexdigest()
            print("密码更改成功！")
            db.execute("UPDATE Customer SET password = \'" + str(new_password_hash) + "\' WHERE cust_id = \'" + str(self.id) + "\'")
            db.commit()
            self.dealWithRequestSetting()

        elif (choice == '3'):
            self.addContacts()
            self.dealWithRequestSetting()

        elif (choice == 'q'):
            self.showMenu()

    def addContacts(self):
        db = Database()
        contact_id = len(db.query("SELECT * FROM Contact")) + 1
        phone = input("请输入联系电话：")
        address = input("请输入配送地址：")
        name = input("请输入联系人名字：")
        db.execute("INSERT INTO Contact VALUES(\'" + str(contact_id) + "\', \'" + phone + "\', \'" + address + "\', \'" + name + "\')")
        db.execute("INSERT INTO Cust_Contact VALUES(\'" + str(self.id) + "\', \'" + str(contact_id) + "\')")
        
        db.commit()
        print("增加成功！\n")

    def addOrder(self, supplier, contact, order_dishes, total_cost, distribution_cost):
        db = Database()
        order_id = len(db.query("SELECT * FROM Orders")) + 1
        date = db.query("SELECT GETDATE()")[0][0]
        supp_contact_id = db.query("SELECT contact_id FORM Supp_Contact WHERE supp_id = " + str(supplier[0]))[0][0]
        db.execute("INSERT INTO Cust_Orders VALUES(" + str(self.cust_id) + ", " + str(order_id) + ")")
        db.execute("INSERT INTO Supp_Orders VALUES(" + str(supplier[0]) + ", " + str(order_id) + ")")
        db.execute("INSERT INTO Orders VALUES(" + str(order_id) + ", " + str(date) + ", " + str(total_cost + distribution_cost) + ", " + str(supp_contact_id) + ", " + str(contact[0]) + ", \'to_do\', " + str(distribution_cost) + ")")
        for dish in order_dishes:
            db.execute("INSERT INTO Orders_Dishes VALUES(" + str(order_id) + ", " + str(dish[0]))
        db.commit(0)

    @staticmethod
    def stateMap(state):
        'to_do', 'to_deliver', 'delivering', 'done'
        if (state == "to_do"):
            return "待接单"
        elif (state == "to_deliver"):
            return "待配送"
        elif (state == "delivering"):
            return "配送中"
        elif (state == "done"):
            return "已完成"

    @staticmethod
    def getSupplierDishes(supp_id):
        db = Database()
        return db.query("SELECT * FROM Dishes, Supp_Dishes WHERE supp_id = " + str(id))

    @staticmethod
    def getSuppliers():
        db = Database()
        return db.query("SELECT supp_id, name, avg_score FROM Supplier")

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
    print("*************** 1: 注册 ***************")
    print("*************** 2: 登录 ***************")
    print("*************** q: 退出 ***************")
    print("***************************************")
    print("请输入您的选项: ", end="")
    choice = input()
    while (choice != '1' and choice != '2' and choice != 'q'):
        print("输入非法，请重新输入: ", end="")
        choice = input()
    
    # register
    if (choice == '1'):
        id = input("请输入您的注册ID（只能使用数字和字母）: ")
        while (Customer.isValidIdFormat(id) == False):
            id = input("注册ID不合法或者已存在，请重新输入: ")
        password = input("请输入您的账号密码（只能使用数字和字母）: ")
        password_hash = hashlib.sha1(password.encode()).hexdigest()
        name = input("请输入您的账号名称: ")
        Customer.addNewCustomer(id, password_hash, name)
    # login
    elif (choice == '2'):
        id = input("请输入您的登录ID：")
        while (Customer.isValidIdInDatabase(id) == False):
            id = input("对不起，该ID不存在，请检查并重新输入：")
        password = input("请输入您的账号密码：")
        password_hash = hashlib.sha1(password.encode()).hexdigest()
        while (Customer.isValidAccountInDatabase(id, password_hash) == False):
            password = input("对不起，密码错误！请重新输入：")
            password_hash = hashlib.sha1(password.encode()).hexdigest()
    # exit
    elif (choice == 'q'):
        exit(0)
    name = Customer.getCustomerName(id)
    print("\n")
    print("***************************************")
    print("************** 登录成功 ***************")
    print("***************************************")
    print("欢迎回来！ " + name + " 先生（小姐）～")
    customer = Customer(id, name)
    customer.showMenu()
