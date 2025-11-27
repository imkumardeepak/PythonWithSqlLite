#!/bin/bash

# Script to deploy Flask application as a systemd service on Linux

# Exit on any error
set -e

# Variables
APP_NAME="student-dashboard"
APP_DIR="/opt/$APP_NAME"
USER="www-data"
GROUP="www-data"

echo "Starting deployment of $APP_NAME..."

# Update system packages
echo "Updating system packages..."
sudo apt update

# Install Python and pip if not already installed
echo "Installing Python and pip..."
sudo apt install -y python3 python3-pip python3-venv

# Create application directory
echo "Creating application directory..."
sudo mkdir -p $APP_DIR

# Copy application files (assuming they're in the current directory)
echo "Copying application files..."
sudo cp -r ../templates $APP_DIR/
sudo cp ../app.py $APP_DIR/
sudo cp ../requirements.txt $APP_DIR/

# Change ownership of the application directory
sudo chown -R $USER:$GROUP $APP_DIR

# Create a virtual environment
echo "Creating virtual environment..."
sudo -u $USER bash -c "cd $APP_DIR && python3 -m venv venv"

# Activate virtual environment and install dependencies
echo "Installing Python dependencies..."
sudo -u $USER bash -c "cd $APP_DIR && source venv/bin/activate && pip install -r requirements.txt"

# Create systemd service file
echo "Creating systemd service..."
sudo tee /etc/systemd/system/$APP_NAME.service > /dev/null <<EOF
[Unit]
Description=Student Results Dashboard Flask App
After=network.target

[Service]
Type=simple
User=$USER
Group=$GROUP
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd daemon
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable the service
echo "Enabling the service..."
sudo systemctl enable $APP_NAME.service

# Start the service
echo "Starting the service..."
sudo systemctl start $APP_NAME.service

# Check service status
echo "Checking service status..."
sudo systemctl status $APP_NAME.service --no-pager

echo "Deployment completed!"
echo "The application should now be running as a service."
echo "Check status with: sudo systemctl status $APP_NAME.service"
echo "View logs with: sudo journalctl -u $APP_NAME.service -f"