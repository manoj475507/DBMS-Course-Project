DROP DATABASE IF EXISTS ColdStorageDB;

CREATE DATABASE ColdStorageDB;

USE ColdStorageDB;

CREATE TABLE Customer (

Customer_ID INT PRIMARY KEY,

Customer_Name VARCHAR(100) NOT NULL,

Phone VARCHAR(15) NOT NULL,

Email VARCHAR(100),

Address VARCHAR(200),

City VARCHAR(50) NOT NULL

);

CREATE TABLE Commodity (

Commodity_ID INT PRIMARY KEY,

Commodity_Name VARCHAR(50) NOT NULL UNIQUE,

Category VARCHAR(50) NOT NULL,

Unit VARCHAR(20) NOT NULL,

Minimum_Storage_Temperature DECIMAL(5,2) NOT NULL,

Maximum_Storage_Temperature DECIMAL(5,2) NOT NULL,

CHECK (Minimum_Storage_Temperature < Maximum_Storage_Temperature)

);

CREATE TABLE Chamber (

Chamber_ID INT PRIMARY KEY,

Chamber_Name VARCHAR(50) NOT NULL UNIQUE,

Chamber_Type VARCHAR(50) NOT NULL,

Capacity INT NOT NULL,

Minimum_Temperature DECIMAL(5,2) NOT NULL,

Maximum_Temperature DECIMAL(5,2) NOT NULL,

Status VARCHAR(20) NOT NULL DEFAULT 'Active',

CHECK (Minimum_Temperature < Maximum_Temperature),

CHECK (Capacity > 0)

);

CREATE TABLE Rate (

Rate_ID INT PRIMARY KEY,

Commodity_ID INT NOT NULL,

Chamber_Type VARCHAR(50) NOT NULL,

Rate_Per_Unit_Per_Day DECIMAL(10,2) NOT NULL,

Effective_From DATE NOT NULL,

Effective_To DATE,

FOREIGN KEY (Commodity_ID) REFERENCES Commodity(Commodity_ID),

CHECK (Rate_Per_Unit_Per_Day > 0)

);

CREATE TABLE Lot (

Lot_ID VARCHAR(10) PRIMARY KEY,

Customer_ID INT NOT NULL,

Commodity_ID INT NOT NULL,

Quantity DECIMAL(10,2) NOT NULL,

Arrival_Date DATE NOT NULL,

Status VARCHAR(20) NOT NULL DEFAULT 'Stored',

FOREIGN KEY (Customer_ID) REFERENCES Customer(Customer_ID),

FOREIGN KEY (Commodity_ID) REFERENCES Commodity(Commodity_ID),

CHECK (Quantity > 0)

);

CREATE TABLE Location (

Location_ID INT PRIMARY KEY,

Chamber_ID INT NOT NULL,

Location_Code VARCHAR(20) NOT NULL,

Capacity INT NOT NULL,

FOREIGN KEY (Chamber_ID) REFERENCES Chamber(Chamber_ID),

UNIQUE (Chamber_ID, Location_Code),

CHECK (Capacity > 0)

);

CREATE TABLE Allocation (

Allocation_ID INT PRIMARY KEY,

Lot_ID VARCHAR(10) NOT NULL,

Chamber_ID INT NOT NULL,

Location_ID INT NOT NULL,

Start_Date DATE NOT NULL,

End_Date DATE,

Status VARCHAR(20) NOT NULL DEFAULT 'Active',

FOREIGN KEY (Lot_ID) REFERENCES Lot(Lot_ID),

FOREIGN KEY (Chamber_ID) REFERENCES Chamber(Chamber_ID),

FOREIGN KEY (Location_ID) REFERENCES Location(Location_ID)

);

CREATE TABLE Temperature_Log (

Log_ID INT PRIMARY KEY,

Allocation_ID INT NOT NULL,

Recorded_DateTime DATETIME NOT NULL,

Temperature DECIMAL(5,2) NOT NULL,

Remarks VARCHAR(200),

FOREIGN KEY (Allocation_ID) REFERENCES Allocation(Allocation_ID)

);

CREATE TABLE Inspection (

Inspection_ID INT PRIMARY KEY,

Allocation_ID INT NOT NULL,

Inspection_Date DATE NOT NULL,

Inspector_Name VARCHAR(100) NOT NULL,

`Condition` VARCHAR(50) NOT NULL,

Remarks VARCHAR(200),

FOREIGN KEY (Allocation_ID) REFERENCES Allocation(Allocation_ID)

);

CREATE TABLE `Release` (

Release_ID INT PRIMARY KEY,

Lot_ID VARCHAR(10) NOT NULL,

Release_Date DATE NOT NULL,

Quantity_Released DECIMAL(10,2) NOT NULL,

Remarks VARCHAR(200),

FOREIGN KEY (Lot_ID) REFERENCES Lot(Lot_ID),

CHECK (Quantity_Released > 0)

);

CREATE TABLE Invoice (

Invoice_ID INT PRIMARY KEY,

Release_ID INT NOT NULL UNIQUE,

Invoice_Date DATE NOT NULL,

Total_Amount DECIMAL(12,2) NOT NULL,

Invoice_Status VARCHAR(20) NOT NULL DEFAULT 'Unpaid',

FOREIGN KEY (Release_ID) REFERENCES `Release`(Release_ID),

CHECK (Total_Amount >= 0)

);

CREATE TABLE Payment (

Payment_ID INT PRIMARY KEY,

Invoice_ID INT NOT NULL,

Payment_Date DATE NOT NULL,

Amount DECIMAL(12,2) NOT NULL,

Payment_Mode VARCHAR(30) NOT NULL,

Transaction_Reference VARCHAR(50),

Payment_Status VARCHAR(20) NOT NULL DEFAULT 'Completed',

FOREIGN KEY (Invoice_ID) REFERENCES Invoice(Invoice_ID),

CHECK (Amount > 0)

);

INSERT INTO Customer (Customer_ID, Customer_Name, Phone, Email, Address, City) VALUES

(1, 'Kohli', '9876543210', 'kohli@email.com', '12 Market Road', 'Nagpur'),

(2, 'Pawan', '9123456780', 'pawan@email.com', '45 Industrial Area', 'Pune'),

(3, 'Vijay', '9988776655', 'vijay@email.com', '78 Wholesale Lane', 'Hyderabad'),

(4, 'Rahul', '9012345678', 'rahul@email.com', '23 Farm Road', 'Nashik'),

(5, 'Kumari', '8899001122', 'kumari@email.com', '56 Cold Street', 'Mumbai');

INSERT INTO Commodity (Commodity_ID, Commodity_Name, Category, Unit, Minimum_Storage_Temperature, Maximum_Storage_Temperature) VALUES

(1, 'Himachal Apples', 'Fruit', 'Kg', 0.00, 4.00),

(2, 'Alphonso Mangoes', 'Fruit', 'Kg', 10.00, 13.00),

(3, 'Nashik Grapes', 'Fruit', 'Kg', 0.00, 2.00),

(4, 'Frozen Green Peas', 'Frozen', 'Kg', -18.00, -15.00),

(5, 'Pomegranates', 'Fruit', 'Kg', 5.00, 7.00);

INSERT INTO Chamber (Chamber_ID, Chamber_Name, Chamber_Type, Capacity, Minimum_Temperature, Maximum_Temperature, Status) VALUES

(1, 'CH01', 'Chilled', 5000, 0.00, 5.00, 'Active'),

(2, 'CH02', 'Frozen', 3000, -20.00, -15.00, 'Active'),

(3, 'CH03', 'Chilled', 4000, 0.00, 5.00, 'Active'),

(4, 'CH04', 'Ambient-Controlled', 6000, 8.00, 15.00, 'Active');

INSERT INTO Rate (Rate_ID, Commodity_ID, Chamber_Type, Rate_Per_Unit_Per_Day, Effective_From, Effective_To) VALUES

(1, 1, 'Chilled', 0.50, '2025-01-01', NULL),

(2, 2, 'Ambient-Controlled', 0.40, '2025-01-01', NULL),

(3, 3, 'Chilled', 0.55, '2025-01-01', NULL),

(4, 4, 'Frozen', 0.80, '2025-01-01', NULL),

(5, 5, 'Chilled', 0.45, '2025-01-01', NULL);

INSERT INTO Lot (Lot_ID, Customer_ID, Commodity_ID, Quantity, Arrival_Date, Status) VALUES

('L001', 1, 1, 500.00, '2026-01-10', 'Released'),

('L002', 2, 2, 300.00, '2026-01-12', 'Released'),

('L003', 3, 3, 800.00, '2026-01-15', 'Stored'),

('L004', 1, 5, 200.00, '2026-02-01', 'Stored'),

('L005', 4, 4, 450.00, '2026-02-05', 'Released'),

('L006', 5, 1, 600.00, '2026-02-10', 'Stored'),

('L007', 2, 3, 350.00, '2026-02-12', 'Stored'),

('L008', 3, 2, 250.00, '2026-02-15', 'Stored');

INSERT INTO Location (Location_ID, Chamber_ID, Location_Code, Capacity) VALUES

(1, 1, 'RACK-A01', 1000),

(2, 1, 'RACK-A02', 1000),

(3, 1, 'RACK-B01', 1500),

(4, 2, 'RACK-F01', 800),

(5, 2, 'RACK-F02', 800),

(6, 3, 'RACK-C01', 1200),

(7, 3, 'RACK-C02', 1200),

(8, 4, 'RACK-D01', 1500),

(9, 4, 'RACK-D02', 1500);

INSERT INTO Allocation (Allocation_ID, Lot_ID, Chamber_ID, Location_ID, Start_Date, End_Date, Status) VALUES

(1, 'L001', 1, 1, '2026-01-10', '2026-02-20', 'Completed'),

(2, 'L002', 4, 8, '2026-01-12', '2026-03-01', 'Completed'),

(3, 'L003', 1, 2, '2026-01-15', NULL, 'Active'),

(4, 'L004', 1, 3, '2026-02-01', NULL, 'Active'),

(5, 'L005', 2, 4, '2026-02-05', '2026-03-10', 'Completed'),

(6, 'L006', 3, 6, '2026-02-10', NULL, 'Active'),

(7, 'L007', 3, 7, '2026-02-12', NULL, 'Active'),

(8, 'L008', 4, 9, '2026-02-15', NULL, 'Active');

INSERT INTO Temperature_Log (Log_ID, Allocation_ID, Recorded_DateTime, Temperature, Remarks) VALUES

(1, 1, '2026-01-11 08:00:00', 2.50, 'Normal'),

(2, 1, '2026-01-12 08:00:00', 3.00, 'Normal'),

(3, 1, '2026-01-13 08:00:00', 2.80, 'Normal'),

(4, 1, '2026-01-20 08:00:00', 5.50, 'Slightly high'),

(5, 2, '2026-01-13 09:00:00', 11.50, 'Normal'),

(6, 3, '2026-01-16 08:30:00', 1.20, 'Normal'),

(7, 4, '2026-02-02 08:00:00', 6.00, 'Normal'),

(8, 5, '2026-02-06 10:00:00', -16.50, 'Normal'),

(9, 5, '2026-02-07 10:00:00', -14.00, 'Above limit'),

(10, 6, '2026-02-11 08:00:00', 2.00, 'Normal');

INSERT INTO Inspection (Inspection_ID, Allocation_ID, Inspection_Date, Inspector_Name, `Condition`, Remarks) VALUES

(1, 1, '2026-01-15', 'Mohith', 'Good', 'No damage observed'),

(2, 1, '2026-02-05', 'Suresh Patil', 'Good', 'Ready for release'),

(3, 2, '2026-01-20', 'Anita Deshmukh', 'Good', 'Quality maintained'),

(4, 3, '2026-01-25', 'Rajesh Kumar', 'Average', 'Minor moisture'),

(5, 5, '2026-02-10', 'Suresh Patil', 'Good', 'Frozen state intact');

INSERT INTO `Release` (Release_ID, Lot_ID, Release_Date, Quantity_Released, Remarks) VALUES

(1, 'L001', '2026-02-20', 500.00, 'Full release as requested'),

(2, 'L002', '2026-03-01', 300.00, 'Full release'),

(3, 'L005', '2026-03-10', 450.00, 'Full release after inspection');

INSERT INTO Invoice (Invoice_ID, Release_ID, Invoice_Date, Total_Amount, Invoice_Status) VALUES

(1, 1, '2026-02-20', 10250.00, 'Paid'),

(2, 2, '2026-03-01',  4800.00, 'Paid'),

(3, 3, '2026-03-10',  8640.00, 'Unpaid');

INSERT INTO Payment (Payment_ID, Invoice_ID, Payment_Date, Amount, Payment_Mode, Transaction_Reference, Payment_Status) VALUES

(1, 1, '2026-02-21', 10250.00, 'Bank Transfer', 'TXN987654321', 'Completed'),

(2, 2, '2026-03-02',  4800.00, 'UPI',          'UPI445566778', 'Completed'),

(3, 3, '2026-03-12',  4000.00, 'Cash',         'CASH001122',   'Completed'),

(4, 3, '2026-03-15',  4640.00, 'Bank Transfer', 'TXN112233445', 'Completed');

SELECT * FROM allocation;

SELECT * FROM chamber;

SELECT * FROM commodity;

SELECT * FROM customer;

SELECT * FROM inspection;

SELECT * FROM invoice;

SELECT * FROM location;

SELECT * FROM lot;

SELECT * FROM payment;

SELECT * FROM rate;

SELECT * FROM `release`;

SELECT * FROM temperature_log;
