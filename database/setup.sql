-- =============================================================
--  database/setup.sql
--  Desktop Based Taxi Booking System
--  Tribhuvan University — Patan Multiple Campus
--
--  Run this ONCE in MySQL Workbench or the MySQL CLI:
--      mysql -u root -p < database/setup.sql
-- =============================================================

-- ── 1. Database ───────────────────────────────────────────────
DROP DATABASE IF EXISTS taxi_booking_db;
CREATE DATABASE taxi_booking_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE taxi_booking_db;


-- ── 2. Users table (customers, drivers, admins all here) ──────
CREATE TABLE users (
    id          INT          AUTO_INCREMENT PRIMARY KEY,
    full_name   VARCHAR(120) NOT NULL,
    email       VARCHAR(120) NOT NULL UNIQUE,
    phone       VARCHAR(20)  NOT NULL,
    password    VARCHAR(64)  NOT NULL,   -- SHA-256 hex
    role        ENUM('customer', 'driver', 'admin') NOT NULL DEFAULT 'customer',
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP
);


-- ── 3. Drivers table (extra info linked to a driver user) ─────
CREATE TABLE drivers (
    id              INT          AUTO_INCREMENT PRIMARY KEY,
    user_id         INT          NOT NULL UNIQUE,
    license_number  VARCHAR(50)  NOT NULL UNIQUE,
    vehicle_type    ENUM('Mini', 'Sedan', 'SUV', 'Luxury') NOT NULL,
    vehicle_number  VARCHAR(30)  NOT NULL,
    vehicle_model   VARCHAR(80)  NOT NULL,
    availability    ENUM('Available', 'On Trip', 'Offline') DEFAULT 'Available',
    rating          DECIMAL(3,2) DEFAULT 5.00,
    total_trips     INT          DEFAULT 0,
    created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_driver_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
);


-- ── 4. Bookings table ─────────────────────────────────────────
CREATE TABLE bookings (
    id                INT          AUTO_INCREMENT PRIMARY KEY,
    customer_id       INT          NOT NULL,
    driver_id         INT,                           -- assigned later by admin
    pickup_location   VARCHAR(200) NOT NULL,
    dropoff_location  VARCHAR(200) NOT NULL,
    vehicle_type      ENUM('Mini', 'Sedan', 'SUV', 'Luxury') NOT NULL,
    booking_date      DATE         NOT NULL,
    booking_time      TIME         NOT NULL,
    fare              DECIMAL(10,2) NOT NULL,
    distance_km       DECIMAL(10,2) DEFAULT 5.00,
    status            ENUM('Pending','Confirmed','Completed','Cancelled')
                        DEFAULT 'Pending',
    notes             TEXT,
    created_at        DATETIME     DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_booking_customer
        FOREIGN KEY (customer_id) REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_booking_driver
        FOREIGN KEY (driver_id) REFERENCES drivers(id)
        ON DELETE SET NULL
);


-- ── 5. Fare table (reference rates) ──────────────────────────
CREATE TABLE fare_rates (
    id           INT          AUTO_INCREMENT PRIMARY KEY,
    vehicle_type ENUM('Mini', 'Sedan', 'SUV', 'Luxury') NOT NULL UNIQUE,
    base_fare    DECIMAL(10,2) NOT NULL,
    per_km_rate  DECIMAL(10,2) NOT NULL,
    updated_at   DATETIME      DEFAULT CURRENT_TIMESTAMP
                               ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO fare_rates (vehicle_type, base_fare, per_km_rate) VALUES
    ('Mini',   50.00, 12.00),
    ('Sedan',  80.00, 15.00),
    ('SUV',   120.00, 20.00),
    ('Luxury',200.00, 30.00);


-- ── 6. Default Admin account ──────────────────────────────────
--  Email:    admin@taxisystem.com
--  Password: Admin@123
--  SHA-256 of "Admin@123"
INSERT INTO users (full_name, email, phone, password, role) VALUES
(
    'System Admin',
    'admin@taxisystem.com',
    '9800000000',
    'e86f78a8a3caf0b60d8e74e5942aa6d86dc150cd3c03338aef25b7d2d7e3acc7',
    'admin'
);


-- ── 7. Sample customers ───────────────────────────────────────
--  Password for all sample users: Password@1
--  SHA-256 of "Password@1"
INSERT INTO users (full_name, email, phone, password, role) VALUES
('Barsana Nakarmi', 'barsana@example.com', '9841000001',
 '9cc3e5abdfaee198a6b74b97ea91e306e1744ddf49876d3dcf6cb936dfd5c9d7', 'customer'),
('Roney Maharjan',  'roney@example.com',   '9851000002',
 '9cc3e5abdfaee198a6b74b97ea91e306e1744ddf49876d3dcf6cb936dfd5c9d7', 'customer'),
('Yunisha Shakya',  'yunisha@example.com', '9861000003',
 '9cc3e5abdfaee198a6b74b97ea91e306e1744ddf49876d3dcf6cb936dfd5c9d7', 'customer');


-- ── 8. Sample drivers ─────────────────────────────────────────
INSERT INTO users (full_name, email, phone, password, role) VALUES
('Ram Bahadur Tamang', 'ram.driver@example.com',   '9801100001',
 'b03ddf3ca2e714a6548e7495e2a03f5e824eaac9837cd7f159c67b90fb4b7342', 'driver'),
('Shyam Prasad Shrestha', 'shyam.driver@example.com', '9801100002',
 'b03ddf3ca2e714a6548e7495e2a03f5e824eaac9837cd7f159c67b90fb4b7342', 'driver'),
('Krishna Magar', 'krishna.driver@example.com', '9801100003',
 'b03ddf3ca2e714a6548e7495e2a03f5e824eaac9837cd7f159c67b90fb4b7342', 'driver');


-- ── 9. Driver profiles ────────────────────────────────────────
INSERT INTO drivers
    (user_id, license_number, vehicle_type, vehicle_number, vehicle_model, availability, rating, total_trips)
VALUES
    (5, 'BA-01-PA-0012', 'Mini',   'BA 1 PA 2012', 'Maruti Suzuki Alto', 'Available', 4.80, 120),
    (6, 'BA-02-PA-0034', 'Sedan',  'BA 2 CHA 3456','Toyota Vios',        'Available', 4.90, 200),
    (7, 'BA-03-KA-0099', 'SUV',    'BA 3 KA 9900', 'Hyundai Creta',      'Offline',   4.70, 85);


-- ── 10. Sample bookings ───────────────────────────────────────
INSERT INTO bookings
    (customer_id, driver_id, pickup_location, dropoff_location,
     vehicle_type, booking_date, booking_time, fare, distance_km, status)
VALUES
    (2, 1, 'Thamel, Kathmandu',  'Patan Durbar Square',  'Mini',  '2026-01-10','10:00:00', 110.00, 5.0,  'Completed'),
    (2, 2, 'New Baneshwor',      'Bhaktapur Bus Park',    'Sedan', '2026-01-15','14:30:00', 230.00, 10.0, 'Completed'),
    (3, 1, 'Maharajgunj',        'Boudha Stupa',          'Mini',  '2026-02-01','09:00:00', 110.00, 5.0,  'Confirmed'),
    (4, NULL,'Swayambhunath',    'Tribhuvan Airport',     'SUV',   '2026-02-20','07:00:00', 220.00, 5.0,  'Pending'),
    (3, NULL,'Kalanki',          'Ratnapark, Kathmandu',  'Sedan', '2026-02-22','11:00:00', 155.00, 5.0,  'Cancelled');


-- ── 11. Verify ────────────────────────────────────────────────
SELECT '✅ Database setup complete!' AS Result;
SELECT CONCAT('Users: ', COUNT(*))    AS Info FROM users;
SELECT CONCAT('Drivers: ', COUNT(*))  AS Info FROM drivers;
SELECT CONCAT('Bookings: ', COUNT(*)) AS Info FROM bookings;
