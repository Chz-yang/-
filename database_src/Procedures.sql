use TakeOut;
go
/*
create or alter procedure Proc_Deliver(@order_id varchar(16), @rider_id varchar(16), @success int output)
as
declare @state varchar(10)
begin
	select @state = state
	from Orders
	where Orders.order_id = @order_id;
	if @state = 'delivering' begin
		set @success = 0;	-- 接单失败
	end
	else begin
		update Orders
		set Orders.state = 'delivering'
		where Orders.order_id = @order_id;
		set @success = 1;	-- 接单成功
		insert into Rider_Orders
		values(@rider_id, @order_id);
	end
end;
*/
