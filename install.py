import subprocess
import platform
import os

os.system("cd src && rm -rf osintgram")
os.system("cd src && git clone https://github.com/Datalux/Osintgram && cd osintgram && sudo python3 setup.py install")
    


def install_dependencies():
    try:
        # Install PyQt5 using pip
        subprocess.run(["pip", "install", "PyQt5", "--break-system-packages"])

        # Install other Python dependencies from requirements.txt
        subprocess.run(["pip", "install", "-r", "src/requirements.txt", "--break-system-packages"])

        print("Python dependencies installed successfully.")

        # If you have additional setup steps, add them here

    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")

def install_system_dependencies():
    system = platform.system().lower()

    try:
        if system == "linux":
            # Install PyQt5 system-level dependencies for Linux
            subprocess.run(["sudo", "apt-get", "install", "-y", "python3-pyqt5"])
        elif system == "darwin":
            # Install PyQt5 system-level dependencies for macOS
            subprocess.run(["brew", "install", "pyqt@5"])
        elif system == "windows":
            # Install PyQt5 system-level dependencies for Windows
            # Replace with appropriate commands for Windows
            pass

        print("System-level dependencies installed successfully.")

    except subprocess.CalledProcessError as e:
        print(f"Error installing system-level dependencies: {e}")
def setup_maigret():
    os.system("cd src && rm -rf maigret")
    os.system("cd src && git clone https://github.com/soxoj/maigret && cd maigret && pip3 install -r requirements.txt")
    os.system("pip3 install maigret")

if __name__ == "__main__":
    install_system_dependencies()
    install_dependencies()
    setup_maigret()
