#!/bin/bash

# Update and install git
echo "Updating system and installing Git..."
sudo apt update && sudo apt upgrade -y
sudo apt install git-all -y

# Create ROS2 workspace
echo "Creating ROS2 workspace..."
mkdir -p ~/ros2_ws/src

# Navigate to the workspace and clone the repository
cd ~/ros2_ws/src
echo "Cloning bigfootbot repository..."
git clone https://github.com/arsenikalbin/bigfootbot.git

# Change to the develop branch
cd bigfootbot
echo "Switching to the 'develop' branch..."
git checkout develop

# Set Git username and email
echo "Configuring Git user..."

# Ask for the Git username
read -p "Enter your Git username: " git_username
git config --global user.name "$git_username"

# Ask for the Git email
read -p "Enter your Git email: " git_email
git config --global user.email "$git_email"

# Set up Git credential storage
echo "Storing Git credentials..."
git config --global credential.helper store
git push

# Install Docker
while true; do
    echo "Please choose your operating system:"
    echo "1. Ubuntu"
    echo "2. Debian"

    read -p "Enter your choice (number): " os_choice

    case $os_choice in
        1)
            echo "Installing Docker on Ubuntu..."

            # Uninstall conflicting packages
            for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done

            # Add Docker's official GPG key:
            sudo apt-get update
            sudo apt-get install ca-certificates curl
            sudo install -m 0755 -d /etc/apt/keyrings
            sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
            sudo chmod a+r /etc/apt/keyrings/docker.asc

            # Add the repository to Apt sources:
            echo \
            "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
            $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
            sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            sudo apt-get update

            # Install Docker
            sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

            echo "Docker installed successfully!"
            break
            ;;

        2)
            echo "Installing Docker on Debian..."

            # Uninstall conflicting packages
            for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do sudo apt-get remove $pkg; done

            # Add Docker's official GPG key:
            sudo apt-get update
            sudo apt-get install ca-certificates curl
            sudo install -m 0755 -d /etc/apt/keyrings
            sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
            sudo chmod a+r /etc/apt/keyrings/docker.asc

            # Add the repository to Apt sources:
            echo \
            "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
            $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
            sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            sudo apt-get update

            # Install Docker
            sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

            echo "Docker installed successfully!"
            break
            ;;

        *)
            echo "Invalid choice. Please choose valid option."
            # The loop continues, prompting the user again
            ;;
    esac
done

# Add the current user to the Docker group
echo "Adding user to the Docker group..."
sudo usermod -aG docker ${USER}

# Udev rules
echo "Installing necessary Udev rules..."

# Copy udev rules
sudo cp ~/ros2_ws/src/bigfootbot/motor_control/udev/99-roboclaw.rules /etc/udev/rules.d
sudo cp ~/ros2_ws/src/bigfootbot/bfb_gps/udev/99-gps-module.rules /etc/udev/rules.d
sudo cp ~/ros2_ws/src/bigfootbot/bfb_arduino_gateway/udev/99-arduino-mega.rules /etc/udev/rules.d

# Reload rules
sudo udevadm control --reload-rules && sudo udevadm trigger

# Notify user to setup Docker swarm and network
echo "After reboot, follow instructions in the end of this file to setup Docker Swarm and network."

while true; do
    echo "Do you want to reboot now?"
    echo "1. Yes"
    echo "2. No, I will reboot later"

    read -p "Enter your choice (number): " os_choice

    case $os_choice in
        1)
            echo "Rebooting now..."
            sudo reboot
            break
            ;;

        2)
            echo "Please reboot your device later to apply changes."
            break
            ;;

        *)
            echo "Invalid choice. Please choose valid option."
            # The loop continues, prompting the user again
            ;;

    esac
done

# --- Set up Docker network ---

# 1. Create swarm on one machine: docker swarm init --advertise-addr <PC1_IP>
# 2. Join swarm on the other machine: docker swarm join --token <token> <PC1_IP>:2377
# 3. Create overlay network on swarm leader machine: docker network create --driver overlay --attachable bfb_teleop_overlay

# To run Docker compose services, use: docker compose -f <compose_file> up <service_1> <service_2> ...