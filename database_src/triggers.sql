CREATE TRIGGER TRI_Comment_Score_INSERT
ON Comments
    AFTER INSERT
AS 
    DECLARE @new_order_id INTEGER,
            @supp_id INTEGER,
            @rider_id INTEGER,
            @supp_sum_score REAL,
            @rider_sum_score REAL,
            @supp_order_count INTEGER,
            @rider_order_count INTEGER;
BEGIN
    SELECT @new_order_id = order_id FROM inserted;
    SELECT @supp_id = supp_id FROM Supp_Orders WHERE order_id = @new_order_id;
    SELECT @rider_id = rider_id FROM Rider_Orders WHERE order_id = @new_order_id;
    SELECT @supp_sum_score = SUM(supplier_score), @supp_order_count = COUNT(supplier_score)
    FROM Supp_Orders, Comments
    WHERE Supp_Orders.supp_id = @supp_id and Comments.order_id = Supp_Orders.order_id;
    SELECT @rider_sum_score = SUM(rider_score), @rider_order_count = COUNT(rider_score)
    FROM Rider_Orders, Comments
    WHERE Rider_Orders.rider_id = @rider_id and Comments.order_id = Rider_Orders.order_id;
    UPDATE Supplier
    SET avg_score = @supp_sum_score / @supp_order_count
    WHERE Supplier.supp_id = @supp_id;
    UPDATE Rider
    SET avg_score = @rider_sum_score / @rider_order_count
    WHERE Rider.rider_id = @rider_id;
END
GO

CREATE TRIGGER TRI_Orders_Dishes_INSERT
on Orders
    AFTER UPDATE
AS
    DECLARE @dishes_totalprice REAL;
BEGIN
    SELECT @dishes_totalprice = SUM(retailprice)
    FROM inserted i, Orders_Dishes OD, Dishes D
    WHERE i.order_id = OD.order_id and OD.dishes_id = D.dishes_id;
    UPDATE Orders
    SET totalprice = @dishes_totalprice + distribution_cost
    FROM Orders O, inserted i
    WHERE O.order_id = i.order_id;
END
GO