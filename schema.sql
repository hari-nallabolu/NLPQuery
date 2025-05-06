DROP TABLE IF EXISTS Customer;
DROP TABLE IF EXISTS Product;
DROP TABLE IF EXISTS "Order";

CREATE TABLE Customer (
    customer_id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT
);

CREATE TABLE Product (
    product_id INTEGER PRIMARY KEY,
    name TEXT,
    category TEXT,
    price REAL
);

CREATE TABLE "Order" (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    product_id INTEGER,
    order_date DATE,
    quantity INTEGER,
    total_amount REAL
);

-- Sample Data
INSERT INTO Customer VALUES (1, 'John Doe', 'john.doe@example.com');
INSERT INTO Customer VALUES (2, 'Alice Smith', 'alice@example.com');
INSERT INTO Customer VALUES (3, 'Bob Johnson', 'bob.johnson@example.com');
INSERT INTO Customer VALUES (4, 'Emily Davis', 'emily.davis@example.com');

INSERT INTO Product VALUES (101, 'iPhone 14', 'Electronics', 999.99);
INSERT INTO Product VALUES (102, 'AirPods Pro', 'Electronics', 249.99);
INSERT INTO Product VALUES (103, 'MacBook Air M2', 'Electronics', 1199.99);
INSERT INTO Product VALUES (104, 'Apple Watch 8', 'Electronics', 399.99);

INSERT INTO "Order" VALUES (5001, 1, 101, '2024-03-15', 2, 1999.98);
INSERT INTO "Order" VALUES (5002, 2, 102, '2024-01-20', 1, 249.99);
INSERT INTO "Order" VALUES (5003, 3, 103, '2024-02-10', 1, 1199.99);
INSERT INTO "Order" VALUES (5004, 1, 104, '2024-04-01', 1, 399.99);
INSERT INTO "Order" VALUES (5005, 4, 102, '2024-03-25', 2, 499.98);
