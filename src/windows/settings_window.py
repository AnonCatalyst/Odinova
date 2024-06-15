from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QColorDialog, QComboBox, QSlider, QHBoxLayout, QApplication, QMainWindow, QCheckBox
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtCore import Qt, pyqtSignal

def color_to_rgb_string(color):
    return f"rgb({color.red()}, {color.green()}, {color.blue()})"

class SettingsWindow(QDialog):
    theme_changed = pyqtSignal(str)
    def __init__(self, main_window):
        
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 400, 400)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Dark mode toggle
        self.dark_mode_checkbox = QCheckBox("Dark Mode")
        self.dark_mode_checkbox.setChecked(True)  # Enable dark mode by default
        self.dark_mode_checkbox.stateChanged.connect(self.toggle_dark_mode)
        self.layout.addWidget(self.dark_mode_checkbox)

        # Background customization section
        self.add_section_label("TOP-BAR BACKGROUND")

        self.background_color_button = QPushButton("Change Top-Bar Background Color")
        self.background_color_button.clicked.connect(self.change_background_color)
        self.layout.addWidget(self.background_color_button)

        # Font color customization section
        self.add_section_label("FONT COLOR CUSTOMIZATION")

        self.font_color_button = QPushButton("Change Font Color")
        self.font_color_button.clicked.connect(self.change_font_color)
        self.layout.addWidget(self.font_color_button)

        # Border customization section
        self.add_section_label("BORDER CUSTOMIZATION")

        self.border_width_label = QLabel("Border Width")
        self.layout.addWidget(self.border_width_label)

        self.border_width_slider = QSlider()
        self.border_width_slider.setOrientation(Qt.Orientation.Horizontal)
        self.border_width_slider.setMinimum(0)
        self.border_width_slider.setMaximum(20)
        self.border_width_slider.setValue(5)
        self.border_width_slider.setTickInterval(1)
        self.border_width_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.border_width_slider.valueChanged.connect(self.update_border_width)
        self.layout.addWidget(self.border_width_slider)

        self.border_color_button = QPushButton("Change Border Color")
        self.border_color_button.clicked.connect(self.change_border_color)
        self.layout.addWidget(self.border_color_button)

        # Apply dark mode theme by default
        self.apply_dark_theme()

    def toggle_dark_mode(self, state):
        if state == Qt.CheckState.Checked:
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

    def apply_dark_theme(self):
        self.setStyleSheet("""
            background-color: #1E1E1E;
            color: white;
        """)

    def apply_light_theme(self):
        self.setStyleSheet("""
            background-color: white;
            color: black;
        """)

    def add_section_label(self, text):
        description_label = QLabel(text)
        description_label.setStyleSheet("color: #888888; font-size: 10px;")
        self.layout.addWidget(description_label)
        border_label = QLabel()
        border_label.setFixedHeight(1)
        border_label.setStyleSheet("background-color: #888888;")
        self.layout.addWidget(border_label)

    def change_background_color(self):
        if self.dark_mode_checkbox.isChecked():
            # Apply dark mode background color
            color = QColorDialog.getColor(initial=Qt.GlobalColor.black)
        else:
            # Apply light mode background color
            color = QColorDialog.getColor(initial=Qt.GlobalColor.white)
        if color.isValid():
            background_color = QColor(color.red(), color.green(), color.blue())
            self.main_window.setStyleSheet(f"background-color: {background_color.name()};")
        else:
            # Handle case where user cancels color selection
            pass

    def change_font_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            font_color = color_to_rgb_string(color)
            self.update_font_color(self.main_window, font_color)
        else:
            # Handle case where user cancels color selection
            pass

    def update_font_color(self, widget, font_color):
        if isinstance(widget, QPushButton):
            widget.setStyleSheet(f"color: {font_color};")
        for child in widget.findChildren(QPushButton):
            self.update_font_color(child, font_color)

    def update_border_width(self, value):
        border_width = f"{value}px solid black"  # Change border color if needed
        self.main_window.setStyleSheet(f"border: {border_width};")

    def change_border_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            border_color = color_to_rgb_string(color)
            border_width = self.border_width_slider.value()
            border_style = f"{border_width}px solid {border_color}"
            self.main_window.setStyleSheet(f"border: {border_style};")
        else:
            # Handle case where user cancels color selection
            pass
