

DROP DATABASE TAKEOUT;
GO

-- USE master
-- GO

-- -- CREATE DATABASE TAKEOUT;
-- -- GO

-- USE TAKEOUT;
-- GO

-- DECLARE @tmp int;
-- SELECT @tmp = (
--     SELECT langid 
--     FROM master.dbo.syslanguages 
--     WHERE alias = 'Simplified Chinese'); 
-- EXEC sp_configure 'default language', @tmp; 
-- GO  

-- RECONFIGURE ;  
-- GO

-- -- set sort as Chinese for echo Chinese
-- -- but it only work for the new created table
-- ALTER DATABASE TPCH COLLATE Chinese_PRC_90_CI_AS
-- GO