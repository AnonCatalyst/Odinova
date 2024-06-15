#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status.

# Define the base directory and virtual environment directory
BASE_DIR="src/windows/ottools"
VENV_DIR="$BASE_DIR/venv"

# Create base directory if it doesn't exist
mkdir -p $BASE_DIR

# Create a Python virtual environment
if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv $VENV_DIR
fi

# Activate the virtual environment
source $VENV_DIR/bin/activate

# Function to handle errors
handle_error() {
  echo "Error: $1"
  deactivate
  exit 1
}

# Install tools
echo "Installing Holehe..."
pip install holehe || handle_error "Failed to install Holehe" &
holehe_pid=$!

echo "Installing PyDork..."
pip install pydork || handle_error "Failed to install PyDork" &
pydork_pid=$!

echo "Installing Getrails..."
pip install getrails || handle_error "Failed to install Getrails" &
getrails_pid=$!

wait $holehe_pid $pydork_pid $getrails_pid
echo "Holehe, PyDork, and Getrails installed successfully!"

echo "Installing Blackbird..."
BLACKBIRD_DIR="$BASE_DIR/Odinova-Blackbird-clone"
rm -rf $BLACKBIRD_DIR
git clone https://github.com/AnonCatalyst/Odinova-blackbird-clone $BLACKBIRD_DIR || handle_error "Failed to clone Blackbird repository"
(
    cd $BLACKBIRD_DIR
    pip install -r requirements.txt || handle_error "Failed to install Blackbird requirements"
    echo "Blackbird installed successfully!"
) &

echo "Installing UnderworldQuest..."
UWQ_DIR="$BASE_DIR/UnderworldQuest"
rm -rf $UWQ_DIR
git clone https://github.com/Malwareman007/UnderworldQuest $UWQ_DIR || handle_error "Failed to clone UnderworldQuest repository"
(
    cd $UWQ_DIR
    pip install -r requirements.txt || handle_error "Failed to install UnderworldQuest requirements"
    echo "UnderworldQuest installed successfully!"
) &

wait
echo "All tools installed successfully!"
deactivate
