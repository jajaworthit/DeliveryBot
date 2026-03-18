<?php
session_start();
header('Content-Type: application/json');

require_once 'config.php';

// Check if user is logged in
if (!isset($_SESSION['user_id'])) {
    echo json_encode([
        'success' => false,
        'message' => 'You must be logged in to submit delivery requests'
    ]);
    exit;
}

// Get POST data
$senderName = isset($_POST['senderName']) ? trim($_POST['senderName']) : '';
$senderPhone = isset($_POST['senderPhone']) ? trim($_POST['senderPhone']) : '';
$pickupAddress = isset($_POST['pickupAddress']) ? trim($_POST['pickupAddress']) : '';
$deliveryAddress = isset($_POST['deliveryAddress']) ? trim($_POST['deliveryAddress']) : '';
$itemType = isset($_POST['itemType']) ? trim($_POST['itemType']) : '';
$priority = isset($_POST['priority']) ? trim($_POST['priority']) : '';
$itemDescription = isset($_POST['itemDescription']) ? trim($_POST['itemDescription']) : '';
$deliveryTime = isset($_POST['deliveryTime']) ? trim($_POST['deliveryTime']) : '';
$specialInstructions = isset($_POST['specialInstructions']) ? trim($_POST['specialInstructions']) : '';

// Accept field names from the existing HTML form (backwards compatible)
if ($senderName === '' && isset($_POST['name'])) {
    $senderName = trim($_POST['name']);
}
if ($senderPhone === '' && isset($_POST['phone'])) {
    $senderPhone = trim($_POST['phone']);
}
if ($itemDescription === '' && isset($_POST['description'])) {
    $itemDescription = trim($_POST['description']);
}
if ($specialInstructions === '' && isset($_POST['instructions'])) {
    $specialInstructions = trim($_POST['instructions']);
}

// Validate required fields
$required_fields = ['senderName', 'senderPhone', 'pickupAddress', 'deliveryAddress', 'itemType', 'priority', 'itemDescription'];
foreach ($required_fields as $field) {
    if (empty($$field)) {
        echo json_encode([
            'success' => false,
            'message' => 'Please fill in all required fields'
        ]);
        exit;
    }
}

// Generate unique request ID
$requestId = 'DR' . date('Y') . str_pad(mt_rand(1, 99999), 5, '0', STR_PAD_LEFT);

// Calculate estimated delivery time based on priority
$estimatedTime = '';
switch ($priority) {
    case 'urgent':
        $estimatedTime = date('Y-m-d H:i:s', strtotime('+30 minutes'));
        break;
    case 'express':
        $estimatedTime = date('Y-m-d H:i:s', strtotime('+1 hour'));
        break;
    case 'standard':
        $estimatedTime = date('Y-m-d H:i:s', strtotime('+3 hours'));
        break;
}

// Create delivery_requests table if it doesn't exist
$createTable = "CREATE TABLE IF NOT EXISTS delivery_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    request_id VARCHAR(20) UNIQUE NOT NULL,
    user_id INT NOT NULL,
    sender_name VARCHAR(100) NOT NULL,
    sender_phone VARCHAR(20) NOT NULL,
    pickup_address TEXT NOT NULL,
    delivery_address TEXT NOT NULL,
    item_type VARCHAR(50) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    item_description TEXT NOT NULL,
    delivery_time DATETIME,
    special_instructions TEXT,
    status ENUM('pending', 'assigned', 'in_progress', 'completed', 'cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    estimated_delivery DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)";

if ($conn->query($createTable) === FALSE) {
    echo json_encode([
        'success' => false,
        'message' => 'Database setup error: ' . $conn->error
    ]);
    exit;
}

// Insert delivery request
$stmt = $conn->prepare("INSERT INTO delivery_requests 
    (request_id, user_id, sender_name, sender_phone, pickup_address, delivery_address, 
     item_type, priority, item_description, delivery_time, special_instructions, estimated_delivery) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)");

$stmt->bind_param("sissssssssss", 
    $requestId, $_SESSION['user_id'], $senderName, $senderPhone, 
    $pickupAddress, $deliveryAddress, $itemType, $priority, 
    $itemDescription, $deliveryTime, $specialInstructions, $estimatedTime);

if ($stmt->execute()) {
    echo json_encode([
        'success' => true,
        'message' => 'Delivery request submitted successfully!',
        'requestId' => $requestId,
        'status' => 'pending',
        'estimatedTime' => date('M j, Y g:i A', strtotime($estimatedTime))
    ]);
} else {
    echo json_encode([
        'success' => false,
        'message' => 'Error submitting request: ' . $stmt->error
    ]);
}

$stmt->close();
$conn->close();
?>
