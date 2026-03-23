CREATE DATABASE IF NOT EXISTS walkin_platform;
USE walkin_platform;

-- ── Companies ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS companies (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  name          VARCHAR(255) NOT NULL,
  email         VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  phone         VARCHAR(20),
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── Users ──────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  name          VARCHAR(255) NOT NULL,
  email         VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  phone         VARCHAR(20),
  skills        TEXT,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── Interviews ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS interviews (
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
  FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- ── Time Slots ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS time_slots (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  interview_id   INT NOT NULL,
  slot_time      VARCHAR(50) NOT NULL,
  total_capacity INT DEFAULT 10,
  booked_count   INT DEFAULT 0,
  FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE
);

-- ── Bookings ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bookings (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  user_id      INT NOT NULL,
  interview_id INT NOT NULL,
  slot_id      INT NOT NULL,
  status       ENUM('confirmed','completed','cancelled') DEFAULT 'confirmed',
  booked_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id)      REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE,
  FOREIGN KEY (slot_id)      REFERENCES time_slots(id) ON DELETE CASCADE,
  UNIQUE KEY unique_user_interview (user_id, interview_id)
);

-- ── OTP Store (DB-based — fixes multi-worker issue) ────────────────────────
CREATE TABLE IF NOT EXISTS otp_store (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  key_name   VARCHAR(255) UNIQUE NOT NULL,
  otp        VARCHAR(10) NOT NULL,
  data       TEXT NOT NULL,
  expires_at DATETIME NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);