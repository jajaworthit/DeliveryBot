// Delivery Robot Website JavaScript - Aligned with Arduino Bridge

// Form Handling
const form = document.getElementById('deliveryForm');
const statusMessage = document.getElementById('statusMessage');

form.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    statusMessage.className = 'request-message success';
    statusMessage.textContent = '✅ Delivery request submitted successfully! We will contact you shortly.';
    
    console.log('Form Data:', data);
    
    setTimeout(() => {
        statusMessage.style.display = 'none';
    }, 5000);
    
    setTimeout(() => {
        form.reset();
    }, 2000);
});

form.addEventListener('reset', function() {
    statusMessage.style.display = 'none';
});

// Robot Status Monitoring System - Aligned with Arduino Bridge
class RobotStatusMonitor {
    constructor() {
        this.status = {
            door: 'CLOSED',
            robot: 'IDLE',
            battery: 85,
            deliveryProgress: 0,
            connection: 'DISCONNECTED'
        };
        
        this.websocket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        
        this.initializeElements();
        this.initializeEventListeners();
        this.connectWebSocket();
        this.updateAllStatus();
    }

    initializeElements() {
        this.doorLight = document.querySelector('#doorIndicator .status-light');
        this.doorText = document.querySelector('#doorIndicator .status-text');
        this.robotLight = document.querySelector('#robotIndicator .status-light');
        this.robotText = document.querySelector('#robotIndicator .status-text');
        this.connectionLight = document.querySelector('#connectionIndicator .status-light');
        this.connectionText = document.querySelector('#connectionIndicator .status-text');
        
        this.batteryFill = document.querySelector('.battery-fill');
        this.batteryText = document.getElementById('batteryText');
        
        this.progressFill = document.querySelector('.progress-fill');
        this.progressSteps = document.querySelectorAll('.progress-step');
        
        this.startDeliveryBtn = document.getElementById('startDeliveryBtn');
        this.emergencyStopBtn = document.getElementById('emergencyStopBtn');
        this.refreshStatusBtn = document.getElementById('refreshStatusBtn');
    }

    initializeEventListeners() {
        this.startDeliveryBtn.addEventListener('click', () => this.startDelivery());
        this.emergencyStopBtn.addEventListener('click', () => this.emergencyStop());
        this.refreshStatusBtn.addEventListener('click', () => this.refreshStatus());
    }

    connectWebSocket() {
        try {
            this.websocket = new WebSocket('ws://localhost:8765');
            
            this.websocket.onopen = () => {
                console.log('WebSocket connected to Arduino bridge');
                this.reconnectAttempts = 0;
                this.showNotification('Connected to Arduino system!', 'success');
            };
            
            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };
            
            this.websocket.onclose = () => {
                console.log('WebSocket disconnected');
                this.status.connection = 'DISCONNECTED';
                this.updateConnectionStatus();
                this.attemptReconnect();
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.status.connection = 'DISCONNECTED';
                this.updateConnectionStatus();
            };
            
        } catch (error) {
            console.error('Failed to connect WebSocket:', error);
            this.status.connection = 'DISCONNECTED';
            this.updateConnectionStatus();
            this.attemptReconnect();
        }
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            setTimeout(() => {
                this.connectWebSocket();
            }, 3000);
        } else {
            this.showNotification('Failed to connect to Arduino system. Please check the bridge server.', 'error');
        }
    }

    handleWebSocketMessage(data) {
        console.log('Received from Arduino:', data);
        
        switch(data.type) {
            case 'connection':
                this.status.connection = data.status;
                this.updateConnectionStatus();
                this.showNotification(data.message, data.status === 'CONNECTED' ? 'success' : 'error');
                break;
                
            case 'door_status':
                this.status.door = data.status;
                this.updateDoorStatus();
                this.showNotification(`Door ${data.status}`, 'success');
                break;
                
            case 'rfid_scan':
                const accessType = data.access === 'GRANTED' ? 'success' : 'error';
                const message = `RFID ${data.access} (UID: ${data.uid})`;
                this.showNotification(message, accessType);
                
                if (data.door_status) {
                    this.status.door = data.door_status;
                    this.updateDoorStatus();
                }
                break;
                
            case 'system_status':
                console.log('System status:', data.status);
                break;
                
            case 'initial_status':
                if (data.arduino_connected) {
                    this.status.connection = 'CONNECTED';
                    this.updateConnectionStatus();
                }
                if (data.door_status) {
                    this.status.door = data.door_status;
                    this.updateDoorStatus();
                }
                break;
                
            case 'command_ack':
                console.log('Command acknowledged:', data.command);
                break;
        }
    }

    startDelivery() {
        if (this.status.door !== 'OPEN') {
            this.showNotification('Please open the door first! RFID authorization required.', 'error');
            return;
        }
        
        this.status.robot = 'LOADING';
        this.updateRobotStatus();
        this.showNotification('Delivery started!', 'success');
        
        this.sendWebSocketCommand('delivery');
        
        setTimeout(() => {
            this.status.robot = 'DELIVERING';
            this.updateRobotStatus();
        }, 2000);
    }

    emergencyStop() {
        this.status.robot = 'EMERGENCY STOP';
        this.updateRobotStatus();
        this.showNotification('Emergency stop activated!', 'error');
        
        this.sendWebSocketCommand('emergency_stop');
        
        setTimeout(() => {
            this.status.robot = 'IDLE';
            this.updateRobotStatus();
        }, 2000);
    }

    refreshStatus() {
        this.sendWebSocketCommand('refresh_status');
        this.showNotification('Status refreshed!', 'success');
    }

    updateAllStatus() {
        this.updateDoorStatus();
        this.updateRobotStatus();
        this.updateBatteryStatus();
        this.updateConnectionStatus();
    }

    updateDoorStatus() {
        const isOpen = this.status.door === 'OPEN';
        this.doorLight.className = `status-light ${isOpen ? 'active' : 'inactive'}`;
        this.doorText.textContent = this.status.door;
    }

    updateRobotStatus() {
        let lightClass = 'inactive';
        let robotStatusText = this.status.robot;
        
        switch(this.status.robot) {
            case 'IDLE':
                lightClass = 'warning';
                break;
            case 'LOADING':
            case 'DELIVERING':
                lightClass = 'active';
                break;
            case 'EMERGENCY STOP':
                lightClass = 'inactive';
                break;
        }
        
        this.robotLight.className = `status-light ${lightClass}`;
        this.robotText.textContent = robotStatusText;
    }

    updateBatteryStatus() {
        this.batteryFill.style.width = `${this.status.battery}%`;
        this.batteryText.textContent = `${Math.round(this.status.battery)}%`;
        
        if (this.status.battery < 20) {
            this.batteryFill.style.background = 'linear-gradient(90deg, #ff4444, #cc0000)';
        } else if (this.status.battery < 60) {
            this.batteryFill.style.background = 'linear-gradient(90deg, #ffaa00, #ff8800)';
        } else {
            this.batteryFill.style.background = 'linear-gradient(90deg, #00ff88, #00cc66)';
        }
    }

    updateConnectionStatus() {
        const isConnected = this.status.connection === 'CONNECTED';
        this.connectionLight.className = `status-light ${isConnected ? 'active' : 'inactive'}`;
        this.connectionText.textContent = this.status.connection;
    }

    sendWebSocketCommand(command) {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify({ command: command }));
            console.log('Sent command to Arduino:', command);
            return true;
        } else {
            console.warn('WebSocket not connected - cannot send command');
            this.showNotification('Arduino system not connected', 'error');
            return false;
        }
    }

    showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `request-message ${type}`;
        notification.textContent = message;
        notification.style.display = 'block';
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '1000';
        notification.style.minWidth = '300px';
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Initialize the robot status monitor when page loads
document.addEventListener('DOMContentLoaded', function() {
    const robotMonitor = new RobotStatusMonitor();
    window.robotMonitor = robotMonitor;
});
