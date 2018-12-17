--this file is used to create TakeOut database and its tables
--DBMS: SQL server

----# create new data base: TakeOut
create database TakeOut

--use database
use TakeOut

----# create Customer table
create table Customer(
	cust_id varchar(20) primary key,
	password int,
	name nvarchar(20),
	identity_type int default 1
);

----# create contact table
create table Contact(
	contact_id varchar(16) primary key,
	telephone_no char(11),
	address nvarchar(50),
	receiver_name nvarchar(20),
);

----# create contact table between customer and contact
create table Cust_Contact(
	cust_id varchar(20) references Customer(cust_id),
	contact_id varchar(16) references Contact(contact_id),
	primary key(cust_id, contact_id)
);

----# create supplier table
create table Supplier(
	supp_id varchar(20) primary key,
	passsword int,
	name nvarchar(20),
	identity_type int default 0,
	avg_score numeric(2, 1)
);

----# create contact table between supplier and contact
create table Supp_Contact(
	supp_id varchar(20) references Supplier(supp_id),
	contact_id varchar(16) references Contact(contact_id),
	primary key(supp_id, contact_id)
);

----# create dishes table
create table Dishes(
	dishes_id varchar(16) primary key,
	dishes_name nvarchar(20),
	retailprice real,
	sales int,
	comment nvarchar(50),
);

----# create contact table between supplier and dishes
create table Supp_Dishes(
	supp_id varchar(20) references Supplier(supp_id),
	dishes_id varchar(16) references Dishes(dishes_id),
	primary key(supp_id, dishes_id)
);

----# create orders table
create table Orders(
	order_id varchar(16) primary key,
	date DATE,	 --https://docs.microsoft.com/zh-cn/sql/t-sql/functions/date-and-time-data-types-and-functions-transact-sql?view=sql-server-2017
	totalprice real,
	supp_contact_id varchar(16) references Contact(contact_id),
	cust_contact_id varchar(16) references Contact(contact_id),
	state varchar(10) not null,
	distribution_cost real,
	check(state in ('to_do', 'to_deliver', 'delivering', 'done'))
);

----# create contact table between orders and dishes
create table Orders_Dishes(
	order_id  varchar(16) references Orders(order_id),
	dishes_id varchar(16) references Dishes(dishes_id),
	primary key(order_id, dishes_id)
);

----# create comments table
create table Comments(
	order_id  varchar(16) primary key references Orders(order_id),
	rider_score int,
	supplier_score int,
	comment nvarchar(50),
);

----# create contact table between orders and suppliers
create table Supp_Orders(
	supp_id varchar(20) references Supplier(supp_id),
	order_id varchar(16) references Orders(order_id),
	primary key(supp_id, order_id)
);

----# create contact table between customers and orders
create table Cust_Orders(
	cust_id varchar(20) references Customer(cust_id),
	order_id varchar(16) references Orders(order_id),
	primary key(cust_id, order_id)
);

----# create riders table
create table Rider(
	rider_id varchar(16) primary key,
	password int,
	name nvarchar(20),
	telephone_no char(11),
	avg_score numeric(2, 1),
);

----# create contact table between riders and orders
create table Rider_Orders(
	rider_id varchar(16) references Rider(rider_id),
	order_id varchar(16) references Orders(order_id),
	primary key(rider_id, order_id)
);