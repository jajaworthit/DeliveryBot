<?php
// Database setup script
define('DB_HOST', 'localhost');
define('DB_USER', 'root');
define('DB_PASS', '');

// Create connection without selecting database
$conn = new mysqli(DB_HOST, DB_USER, DB_PASS);

if ($conn->connect_error) {
    die('Database connection failed: ' . $conn->connect_error);
}

// Create database
$db_name = 'delivery_bot_db';
$sql = "CREATE DATABASE IF NOT EXISTS $db_name";

if ($conn->query($sql) === TRUE) {
    echo "Database created successfully<br>";
} else {
    die('Error creating database: ' . $conn->error);
}

// Select database
$conn->select_db($db_name);

// Create users table
$create_users = "CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    status ENUM('active', 'inactive') DEFAULT 'active'
)";

if ($conn->query($create_users) === TRUE) {
    echo "Users table created successfully<br>";
} else {
    die('Error creating users table: ' . $conn->error);
}

// Create login_logs table
$create_logs = "CREATE TABLE IF NOT EXISTS login_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    ip_address VARCHAR(45),
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    logout_time TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)";

if ($conn->query($create_logs) === TRUE) {
    echo "Login logs table created successfully<br>";
} else {
    die('Error creating login logs table: ' . $conn->error);
}

// Insert default admin user
$admin_username = 'admin';
$admin_email = 'admin@deliverybot.com';
$admin_password = password_hash('password123', PASSWORD_BCRYPT);

// Check if admin already exists
$check = $conn->prepare("SELECT id FROM users WHERE username = ?");
$check->bind_param("s", $admin_username);
$check->execute();
$result = $check->get_result();

if ($result->num_rows === 0) {
    $insert = $conn->prepare("INSERT INTO users (username, password, email, full_name) VALUES (?, ?, ?, ?)");
    $full_name = 'Administrator';
    $insert->bind_param("ssss", $admin_username, $admin_password, $admin_email, $full_name);
    
    if ($insert->execute()) {
        echo "Default admin user created successfully<br>";
        echo "Username: admin<br>";
        echo "Password: password123<br>";
    } else {
        die('Error creating admin user: ' . $conn->error);
    }
    $insert->close();
} else {
    echo "Admin user already exists<br>";
}

$check->close();
$conn->close();

echo "<br><strong>Database setup completed!</strong><br>";
echo "Delete this file (setup.php) after running it for security.";

?>
