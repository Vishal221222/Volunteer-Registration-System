CREATE DATABASE IF NOT EXISTS volunteer_db;
USE volunteer_db;

CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS volunteers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    age INT NOT NULL,
    gender VARCHAR(20),
    address TEXT,
    skills VARCHAR(255),
    availability VARCHAR(100),
    interest_area VARCHAR(100),
    status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
