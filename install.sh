#!/bin/bash
destination_dir="/usr/local/bin"
copy_files()
{
    sudo mkdir ${destination_dir}/Anoncatalyst
    
    cp -r ../Odinova "$destination_dir/Anoncatalyst"

    if [ $? -eq 0 ]; then
        echo "Copied Odinova folder to $destination_dir"
    else
        echo "Failed to copy Odinova folder"
        exit 1
    fi
    chmod -R a+rw "$destination_dir/Anoncatalyst/"
    cd "$destination_dir/Anoncatalyst/Odinova" || { echo "Failed to change directory"; exit 1; }
    chmod +x odinova
    rm install.sh

    if [ -n "$BASH_VERSION" ]; then
    echo 'export PATH="$PATH:'"$destination_dir/Anoncatalyst/Odinova"'"' >> ~/.bashrc
    echo "Added Anoncatalyst directory to PATH in ~/.bashrc"
    fi

    # Check if the user is using Zsh
    if [ -n "$ZSH_VERSION" ]; then
        echo 'export PATH="$PATH:'"$destination_dir/Anoncatalyst/Odinova"'"' >> ~/.zshrc
        echo "Added Anoncatalyst directory to PATH in ~/.zshrc"
    fi
}

clone_maigret()
{
    echo "Cloning Maigret..."
    git clone https://github.com/soxoj/maigret src/maigret
    echo "Completed Maigret Clone"
}

install_dependencies() {
    python3 -m venv venv
    source venv/bin/activate

    echo "Installing Python dependencies..."
    pip install -r src/requirements.txt
    echo "Python dependencies installed successfully."
    deactivate
}
install_system_dependencies() {
    echo "Installing system-level dependencies..."
    system=$(uname | tr '[:upper:]' '[:lower:]')
    if [ "$system" = "linux" ]; then
        if [ -f "/etc/arch-release" ]; then
            sudo pacman -S --noconfirm python-pyqt5 python-yarl
        elif [ -f "/etc/redhat-release" ]; then
            if [ -x "$(command -v yum)" ]; then
                sudo yum install -y python3-pyqt5
            elif [ -x "$(command -v dnf)" ]; then
                sudo dnf install -y python3-pyqt5
            else
                echo "Neither yum nor dnf found. Unable to install system dependencies."
                exit 1
            fi
        else
            sudo apt-get install -y python3-pyqt5
        fi
    elif [ "$system" = "darwin" ]; then
        brew install pyqt@5
    elif [ "$system" = "windows" ]; then
        pip install pyqt5
    else
        echo "Unsupported system: $system"
        exit 1
    fi
    echo "System-level dependencies installed successfully."
}

copy_files
clone_maigret
install_dependencies
install_system_dependencies
source ~/.bashrc

echo "Installation complete. You can now run odinova from anywhere in the terminal"