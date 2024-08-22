#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status.

# Define the base directory and virtual environment directory
BASE_DIR="src/windows/ottools"
VENV_DIR="$BASE_DIR/venv"

# Function to detect package manager
detect_package_manager() {
  if command -v pacman &> /dev/null; then
    echo "pacman"
  elif command -v apt-get &> /dev/null; then
    echo "apt"
  else
    echo "No supported package manager found (pacman or apt)."
    exit 1
  fi
}

# Install Python if not installed
install_python() {
  local pkg_manager=$1
  if [ "$pkg_manager" = "pacman" ]; then
    sudo pacman -Syu --noconfirm python
  elif [ "$pkg_manager" = "apt" ]; then
    sudo apt update
    sudo apt install -y python3
  fi
}

# Create base directory and ottools directory if they don't exist
mkdir -p "$BASE_DIR"

# Check and install Python if not installed
PKG_MANAGER=$(detect_package_manager)
if ! command -v python3 &> /dev/null; then
  echo "Python 3 not found. Installing Python 3..."
  install_python "$PKG_MANAGER"
fi

# Function to create or recreate the virtual environment
create_virtualenv() {
  echo "Creating or recreating virtual environment..."
  if [ -d "$VENV_DIR" ]; then
    echo "Removing existing virtual environment..."
    rm -rf "$VENV_DIR"
  fi
  python3 -m venv "$VENV_DIR" || {
    echo "Failed to create virtual environment. Check if Python 3 and the venv module are installed correctly."
    exit 1
  }
}

# Create or recreate the virtual environment
create_virtualenv

# Verify the virtual environment creation
if [ ! -f "$VENV_DIR/bin/activate" ]; then
  echo "Virtual environment activation script not found. Check if the virtual environment was created correctly."
  echo "Directory contents:"
  ls -l "$VENV_DIR/bin/"
  exit 1
fi

# Activate the virtual environment
. "$VENV_DIR/bin/activate"  # Use dot (.) for compatibility

# Function to handle errors
handle_error() {
  echo "Error: $1"
  deactivate
  exit 1
}

# Function to install a Python tool
install_tool() {
  local tool=$1
  echo "Installing $tool..."
  pip install "$tool" || handle_error "Failed to install $tool"
}

# Detect the package manager
echo "Detected package manager: $PKG_MANAGER"

# Install tools
echo "Installing Holehe, PyDork, and Getrails..."

install_tool "holehe" &
holehe_pid=$!

install_tool "pydork" &
pydork_pid=$!

install_tool "getrails" &
getrails_pid=$!

wait $holehe_pid $pydork_pid $getrails_pid
echo "Holehe, PyDork, and Getrails installed successfully!"

# Install Blackbird
echo "Installing Blackbird..."
BLACKBIRD_DIR="$BASE_DIR/Odinova-Blackbird-clone"
rm -rf "$BLACKBIRD_DIR"
git clone https://github.com/AnonCatalyst/Odinova-blackbird-clone "$BLACKBIRD_DIR" || handle_error "Failed to clone Blackbird repository"
(
    cd "$BLACKBIRD_DIR"
    pip install -r requirements.txt || handle_error "Failed to install Blackbird requirements"
    echo "Blackbird installed successfully!"
) &

# Install UnderworldQuest
echo "Installing UnderworldQuest..."
UWQ_DIR="$BASE_DIR/UnderworldQuest"
rm -rf "$UWQ_DIR"
git clone https://github.com/Malwareman007/UnderworldQuest "$UWQ_DIR" || handle_error "Failed to clone UnderworldQuest repository"
(
    cd "$UWQ_DIR"
    pip install -r requirements.txt || handle_error "Failed to install UnderworldQuest requirements"
    echo "UnderworldQuest installed successfully!"
) &

wait
echo "All tools installed successfully!"
deactivate
