import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTreeView, QPushButton, QInputDialog, QMessageBox, QToolBar
from PyQt6.QtGui import QFileSystemModel, QIcon
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QFileInfo, QThread

class FileOperationThread(QThread):
    def __init__(self, operation, *args, **kwargs):
        super().__init__()
        self.operation = operation
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.operation(*self.args, **self.kwargs)

class DocumentsWindow(QWidget):
    open_document = pyqtSignal(str)  # Signal to indicate opening a document

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        # Initialize the file system model
        self.model = QFileSystemModel()
        self.model.setRootPath('src/docs')  # Root path for the file manager
        
        # Initialize the tree view
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index('src/docs'))
        self.tree.setSelectionMode(QTreeView.SelectionMode.SingleSelection)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)

        # Connect double click event to slot
        self.tree.doubleClicked.connect(self.handle_double_click)

        # Add the tree view to the layout
        self.layout.addWidget(self.tree)

        # Initialize toolbar
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(16, 16))

        # Create and add buttons to the toolbar
        self.create_folder_button = QPushButton(QIcon.fromTheme("folder-new"), "Create Folder")
        self.create_folder_button.clicked.connect(self.create_folder)
        self.toolbar.addWidget(self.create_folder_button)

        self.delete_button = QPushButton(QIcon.fromTheme("edit-delete"), "Delete")
        self.delete_button.clicked.connect(self.delete_item)
        self.toolbar.addWidget(self.delete_button)

        self.rename_button = QPushButton(QIcon.fromTheme("edit-rename"), "Rename")
        self.rename_button.clicked.connect(self.rename_item)
        self.toolbar.addWidget(self.rename_button)

        self.open_button = QPushButton(QIcon.fromTheme("document-open"), "Open")
        self.open_button.clicked.connect(self.open_item)  # Connect to open_item method
        self.toolbar.addWidget(self.open_button)

        self.properties_button = QPushButton(QIcon.fromTheme("document-properties"), "Properties")
        self.properties_button.clicked.connect(self.show_properties)
        self.toolbar.addWidget(self.properties_button)

        # Add "Go Up" button to navigate to parent directory
        self.go_up_button = QPushButton(QIcon.fromTheme("go-up"), "Go Up")
        self.go_up_button.clicked.connect(self.go_up)
        self.toolbar.addWidget(self.go_up_button)

        # Add the toolbar to the layout
        self.layout.addWidget(self.toolbar)

        # Set layout
        self.setLayout(self.layout)

    def handle_double_click(self, index):
        if not index.isValid():
            return

        if self.model.isDir(index):
            self.tree.setRootIndex(index)
        else:
            self.open_item()

    def create_folder(self):
        index = self.tree.currentIndex()
        if not index.isValid():
            index = self.model.index('src/docs')

        folder_name, ok = QInputDialog.getText(self, "Create Folder", "Folder name:")
        if ok and folder_name:
            if not self.model.mkdir(index, folder_name).isValid():
                QMessageBox.warning(self, "Error", "Failed to create the folder.")
            else:
                # Navigate to parent directory
                parent_index = self.model.parent(index)
                self.tree.setRootIndex(parent_index)

    def delete_item(self):
        index = self.tree.currentIndex()
        if not index.isValid():
            return

        file_path = self.model.filePath(index)
        if QMessageBox.question(self, "Delete", f"Are you sure you want to delete '{file_path}'?",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            if self.model.isDir(index):
                operation_thread = FileOperationThread(self.model.rmdir, index)
                operation_thread.start()
            else:
                operation_thread = FileOperationThread(self.model.remove, index)
                operation_thread.start()

    def rename_item(self):
        index = self.tree.currentIndex()
        if not index.isValid():
            return

        old_file_path = self.model.filePath(index)
        old_file_name = os.path.basename(old_file_path)
        new_file_name, ok = QInputDialog.getText(self, "Rename", "New name:", text=old_file_name)
        if ok and new_file_name:
            new_file_path = os.path.join(os.path.dirname(old_file_path), new_file_name)
            operation_thread = FileOperationThread(self.rename_file, old_file_path, new_file_path)
            operation_thread.start()

    def rename_file(self, old_path, new_path):
        try:
            os.rename(old_path, new_path)
            self.model.refresh(self.model.index(os.path.dirname(new_path)))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to rename the item: {e}")

    def open_item(self):
        index = self.tree.currentIndex()
        if not index.isValid():
            return

        file_path = self.model.filePath(index)
        if not self.model.isDir(index):  # Check if the selected item is a file
            self.open_document.emit(file_path)  # Emit the signal with the file path

    def show_properties(self):
        index = self.tree.currentIndex()
        if not index.isValid():
            return

        file_path = self.model.filePath(index)
        file_info = QFileInfo(file_path)
        properties = f"Name: {file_info.fileName()}\n"
        properties += f"Path: {file_info.absoluteFilePath()}\n"
        properties += f"Size: {file_info.size()} bytes\n"
        properties += f"Last Modified: {file_info.lastModified().toString('yyyy-MM-dd hh:mm:ss')}"
        QMessageBox.information(self, "Properties", properties)

    def go_up(self):
        current_index = self.tree.rootIndex()
        if not current_index.isValid():
            return

        parent_index = self.model.parent(current_index)
        if parent_index.isValid():
            self.tree.setRootIndex(parent_index)
