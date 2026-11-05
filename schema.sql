CREATE DATABASE IF NOT EXISTS ecosort CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'ecosort_user'@'localhost' IDENTIFIED BY 'ecosort_password';
GRANT ALL PRIVILEGES ON ecosort.* TO 'ecosort_user'@'localhost';
FLUSH PRIVILEGES;
USE ecosort;

CREATE TABLE IF NOT EXISTS waste_scans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(120) NOT NULL,
    material_category VARCHAR(80) NOT NULL,
    confidence DECIMAL(5,4) NOT NULL,
    disposal_bin VARCHAR(120) NOT NULL,
    city VARCHAR(80) NOT NULL DEFAULT 'Dortmund',
    notes VARCHAR(500) NOT NULL DEFAULT '',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT confidence_range CHECK (confidence >= 0 AND confidence <= 1),
    INDEX idx_material_category (material_category),
    INDEX idx_created_at (created_at)
);

INSERT INTO waste_scans (item_name, material_category, confidence, disposal_bin, city, notes)
SELECT 'Water bottle', 'Plastic', 0.94, 'Yellow bin', 'Dortmund', 'Demo record'
WHERE NOT EXISTS (SELECT 1 FROM waste_scans WHERE item_name = 'Water bottle');

INSERT INTO waste_scans (item_name, material_category, confidence, disposal_bin, city, notes)
SELECT 'Glass jar', 'Glass', 0.88, 'Glass container', 'Dortmund', 'Sort by glass colour'
WHERE NOT EXISTS (SELECT 1 FROM waste_scans WHERE item_name = 'Glass jar');
