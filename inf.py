# info_gathering.py


import platform
import socket
import os
from PyQt5.QtWidgets import QPlainTextEdit
import psutil

def get_system_info(target_text_widget=None):
    if target_text_widget is None:
        return "Error: target_text_widget not provided."

    # System information
    system_info_text = "System Information:\n"
    system_info_text += f"  Operating System: {platform.system()} {platform.version()}\n"
    system_info_text += f"  Processor: {platform.processor()} ({os.cpu_count()} cores)\n"
    system_info_text += f"  Architecture: {platform.architecture()[0]}\n"
    system_info_text += get_memory_info() + "\n"
    system_info_text += get_disk_info() + "\n"

    # Network information
    system_info_text += "\nNetwork Information:\n"
    system_info_text += f"  Hostname: {socket.gethostname()}\n"
    system_info_text += f"  Internal IP: {socket.gethostbyname(socket.gethostname())}\n"
    system_info_text += f"  External IP: {get_external_ip()}\n\n"

    target_text_widget.setPlainText(system_info_text)

def get_memory_info():
    memory_info = psutil.virtual_memory()
    return f"  Memory: Total - {memory_info.total / (1024 ** 3):.2f} GB, " \
           f"Available - {memory_info.available / (1024 ** 3):.2f} GB"

def get_disk_info():
    disk_info = psutil.disk_usage('/')
    return f"  Disk Space: Total - {disk_info.total / (1024 ** 3):.2f} GB, " \
           f"Used - {disk_info.used / (1024 ** 3):.2f} GB, " \
           f"Free - {disk_info.free / (1024 ** 3):.2f} GB"

def get_external_ip():
    try:
        # Attempt to connect to Google to retrieve external IP
        external_ip = socket.create_connection(("www.google.com", 80), 2).getsockname()[0]
        return f"  External IP: {external_ip}"
    except Exception as e:
        return f"Error getting external IP: {e}"

if __name__ == "__main__":
    # src/info_gathering.py

    print("Executing info_gathering module")  # or use logging

    # Example of using get_system_info with a QTextEdit widget
    from PyQt5.QtWidgets import QApplication, QTextEdit, QVBoxLayout, QWidget

    class SystemInfoWindow(QWidget):
        def __init__(self):
            super().__init__()

            layout = QVBoxLayout()
            self.system_info_text = QTextEdit()
            layout.addWidget(self.system_info_text)
            self.setLayout(layout)

            # Call get_system_info with the QTextEdit widget
            get_system_info(self.system_info_text)

    app = QApplication([])
    window = SystemInfoWindow()
    window.show()
    app.exec_()
