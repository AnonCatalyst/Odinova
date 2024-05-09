import subprocess
import platform
import os

def install_dependencies():
    try:
        subprocess.run(["pip", "install", "PyQt5", "--break-system-packages"], check=True)
        subprocess.run(["pip", "install", "-r", "src/requirements.txt", "--break-system-packages"], check=True)
        print("Python dependencies installed successfully.")
    except subprocess.CalledProcessError:
        print("Error installing Python dependencies.")

def install_system_dependencies():
    system = platform.system().lower()
    if system == "linux":
        if os.path.exists("/etc/arch-release"):
            subprocess.run(["sudo", "pacman", "-S", "--noconfirm", "python-pyqt5", "python-yarl"], check=True)
        else:
            subprocess.run(["sudo", "apt-get", "install", "-y", "python3-pyqt5"], check=True)
    elif system == "darwin":
        subprocess.run(["brew", "install", "pyqt@5"], check=True)
    elif system == "windows":
        try:
            subprocess.run(["pip", "install", "pyqt5"], check=True)
        except subprocess.CalledProcessError:
            print("Error installing PyQt5 using pip.")
    print("System-level dependencies installed successfully.")

def setup_maigret():
    try:
        os.system("rmdir /s /q src\\maigret")
        subprocess.run(["git", "clone", "https://github.com/soxoj/maigret", "src\\maigret"], check=True)
        if os.path.exists("src/maigret/requirements.txt"):
            subprocess.run(["pip", "install", "-r", "src\\maigret\\requirements.txt", "--break-system-packages"], check=True)
            subprocess.run(["pip", "install", "src\\maigret", "--break-system-packages"], check=True)
            print("Maigret setup completed successfully.")
        else:
            print("Error: requirements.txt not found.")
    except subprocess.CalledProcessError:
        print("Error setting up Maigret.")

def install_yarl():
    try:
        system = platform.system().lower()
        if system == "linux" and os.path.exists("/etc/arch-release"):
            subprocess.run(["sudo", "pacman", "-S", "--noconfirm", "python-yarl"], check=True)
            print("python-yarl installed successfully.")
        else:
            subprocess.run(["pip", "install", "yarl"], check=True)
            print("yarl installed successfully.")
    except subprocess.CalledProcessError:
        print("Error installing yarl.")

if __name__ == "__main__":
    install_system_dependencies()
    install_dependencies()
    install_yarl()
    setup_maigret()

