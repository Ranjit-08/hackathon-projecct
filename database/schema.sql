CREATE DATABASE IF NOT EXISTS walkin_platform;
USE walkin_platform;

CREATE TABLE companies (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  name          VARCHAR(255) NOT NULL,
  email         VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  phone         VARCHAR(20),
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  name          VARCHAR(255) NOT NULL,
  email         VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  phone         VARCHAR(20),
  skills        TEXT,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE interviews (
  id                  INT AUTO_INCREMENT PRIMARY KEY,
  company_id          INT NOT NULL,
  role                VARCHAR(255) NOT NULL,
  job_description     TEXT,
  package             VARCHAR(100),
  interview_date      DATE NOT NULL,
  location            VARCHAR(255),
  candidates_required INT DEFAULT 1,
  status              ENUM('active','closed','expired') DEFAULT 'active',
  created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE time_slots (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  interview_id   INT NOT NULL,
  slot_time      VARCHAR(30) NOT NULL,
  total_capacity INT DEFAULT 10,
  booked_count   INT DEFAULT 0,
  FOREIGN KEY (interview_id) REFERENCES interviews(id)
);

CREATE TABLE bookings (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  user_id      INT NOT NULL,
  interview_id INT NOT NULL,
  slot_id      INT NOT NULL,
  status       ENUM('confirmed','completed','cancelled') DEFAULT 'confirmed',
  booked_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id)      REFERENCES users(id),
  FOREIGN KEY (interview_id) REFERENCES interviews(id),
  FOREIGN KEY (slot_id)      REFERENCES time_slots(id),
  UNIQUE KEY unique_user_interview (user_id, interview_id)
);