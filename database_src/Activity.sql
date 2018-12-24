use TakeOut;
go
/*
insert into Customer
values(0, 12345, 'Ñî³ÂÔó', 1);

insert into Supplier
values(0, 12345, 'ÑîîñÕÂ', 0, 5);

insert into Dishes
values(0, 'ºìÉÕÒ¶¹ãÖÇ', 10, 0, 'É«ÏãÎ¶¾ãÈ«');

insert into Contact
values(0, '15626229847', 'Ğ¡¹ÈÎ§', 'ÖÓ·²±¼');

insert into Contact
values(1, '15626229847', 'Ğ¡¹ÈÎ§', 'ÖÓ·²±¼');

insert into Orders
values(0, '2018-12-17', 10, 0, 1, 'to_deliver', 1);
insert into Orders
values(1, '2018-12-18', 10, 0, 1, 'to_deliver', 1);
*/

insert into Supp_Dishes
values(0, 0);

select *
from Orders;

select *
from Rider_Orders;

select *
from Rider;
/*
update Orders
set state = 'to_deliver'
where order_id = 0 or order_id = 1;

select *
from Orders

delete Rider_Orders;
*/
