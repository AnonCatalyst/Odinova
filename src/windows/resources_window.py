from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTextBrowser, QPushButton, QFileDialog, QScrollArea
from PyQt6.QtCore import Qt
import os
import markdown
from src.core.design_handler import DesignHandler

class ResourcesWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        self.load_markdown_files()
        print("README.md | Loaded into RESOURCES window successfully!")

        # Add import button
        import_button_layout = QHBoxLayout()
        self.import_button = DesignHandler.create_button("Import Markdown File")
        self.import_button.clicked.connect(self.import_markdown_file)
        import_button_layout.addWidget(self.import_button)
        self.layout.addLayout(import_button_layout)

        # Apply dark theme
        DesignHandler.apply_dark_theme(self)

    def load_markdown_files(self):
        print("Checking for any available Markdown.md files & Loading README.md...")
        md_folder = 'src/md'
        if not os.path.exists(md_folder):
            os.makedirs(md_folder)

        readme_path = os.path.join(md_folder, 'README.md')
        if os.path.exists(readme_path):
            self.add_markdown_tab(readme_path)

        for filename in os.listdir(md_folder):
            if filename.endswith('.md') and filename != 'README.md':
                self.add_markdown_tab(os.path.join(md_folder, filename))

    def add_markdown_tab(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()

        # Convert markdown content to HTML
        html_content = markdown.markdown(content)

        # Limit the displayed content
        max_chars = 10000  # Adjust this value as needed
        if len(html_content) > max_chars:
            html_content = html_content[:max_chars] + "<p>...</p>"

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        text_browser = QTextBrowser()
        text_browser.setHtml(html_content)

        scroll_area.setWidget(text_browser)

        tab_name = os.path.basename(file_path)
        self.tab_widget.addTab(scroll_area, tab_name)

    def import_markdown_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Import Markdown File", "", "Markdown Files (*.md)")

        if file_path:
            self.add_markdown_tab(file_path)

