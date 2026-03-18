<?php
session_start();
header('Content-Type: application/json');

require_once 'config.php';

// Get POST data
$username = isset($_POST['username']) ? trim($_POST['username']) : '';
$password = isset($_POST['password']) ? trim($_POST['password']) : '';

// Validate input
if (empty($username) || empty($password)) {
    echo json_encode([
        'success' => false,
        'message' => 'Username and password are required'
    ]);
    exit;
}

// Prepare and execute query
$stmt = $conn->prepare("SELECT id, username, password, email FROM users WHERE username = ?");
$stmt->bind_param("s", $username);
$stmt->execute();
$result = $stmt->get_result();

if ($result->num_rows === 1) {
    $user = $result->fetch_assoc();
    
    // Verify password
    if (password_verify($password, $user['password'])) {
        // Password is correct, set session
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['username'] = $user['username'];
        $_SESSION['email'] = $user['email'];
        
        // Log login activity
        $ip_address = $_SERVER['REMOTE_ADDR'];
        $log_stmt = $conn->prepare("INSERT INTO login_logs (user_id, ip_address, login_time) VALUES (?, ?, NOW())");
        $log_stmt->bind_param("is", $user['id'], $ip_address);
        $log_stmt->execute();
        $log_stmt->close();
        
        echo json_encode([
            'success' => true,
            'message' => 'Login successful',
            'redirect' => 'index.php'
        ]);
    } else {
        echo json_encode([
            'success' => false,
            'message' => 'Invalid password'
        ]);
    }
} else {
    echo json_encode([
        'success' => false,
        'message' => 'User not found'
    ]);
}

$stmt->close();
$conn->close();

?>
