import sys
import os
import shutil
from src.logging import LoggingWindow
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QTreeView, QInputDialog, 
    QMessageBox, QToolBar, QLabel, QSplitter, QMenu, QFileDialog
)
from PyQt6.QtGui import QIcon, QAction, QFileSystemModel, QPixmap, QPainter, QPen, QStandardItemModel, QStandardItem, QFileSystemModel
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QModelIndex, QAbstractItemModel




class ToolbarWithDividers(QToolBar):
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setPen(QPen(Qt.GlobalColor.darkGray, 1))
        painter.drawLine(0, 0, 0, self.height())


class TaggedFileSystemModel(QFileSystemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tagged_items = set()

    def flags(self, index):
        return super().flags(index) | Qt.ItemFlag.ItemIsUserCheckable

    def data(self, index, role):
        if role == Qt.ItemDataRole.CheckStateRole and self.filePath(index) in self.tagged_items:
            return Qt.CheckState.Checked
        return super().data(index, role)

    def set_tagged(self, index, tagged):
        file_path = self.filePath(index)
        if tagged:
            self.tagged_items.add(file_path)
        else:
            self.tagged_items.discard(file_path)
        self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])

    def create_folder(self, path, name):
        self.untag_all()
        return super().mkdir(path, name)


    def untag_all(self):
        if self.tagged_items:
            self.tagged_items.clear()
            self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount() - 1, 0), [Qt.ItemDataRole.CheckStateRole])

   
class DocumentsWindow(QWidget):
    open_document = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = LoggingWindow()
        self.clipboard = []
        self.tagging_active = False
        self.setup_ui()

    def setup_ui(self):
        self.model = TaggedFileSystemModel()
        self.model.setRootPath('src/docs')
        self.model.setReadOnly(False)

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index('src/docs'))
        self.tree.setSelectionMode(QTreeView.SelectionMode.ExtendedSelection)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        self.tree.setDragDropMode(QTreeView.DragDropMode.DragDrop)
        self.tree.doubleClicked.connect(self.handle_double_click)
        self.tree.selectionModel().selectionChanged.connect(self.update_preview)

        self.preview = QLabel("𝗣𝗿𝗲𝘃𝗶𝗲𝘄 𝗣𝗮𝗻𝗲")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.preview.setWordWrap(True)
        self.preview.setFixedWidth(300)

        splitter = QSplitter()
        splitter.addWidget(self.tree)
        splitter.addWidget(self.preview)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(splitter)

        self.toolbar = ToolbarWithDividers()
        self.toolbar.setIconSize(QSize(16, 16))
        self.layout.addWidget(self.toolbar, alignment=Qt.AlignmentFlag.AlignRight)
        self.setup_actions()
        self.setLayout(self.layout)


    def update_preview(self):
        index = self.tree.currentIndex()
        if index.isValid():
            item_path = self.model.filePath(index)
            if os.path.isdir(item_path):
                self.preview.setText(f"Folder: {os.path.basename(item_path)}")
            else:
                if os.path.exists(item_path):
                    try:
                        with open(item_path, 'r') as file:
                            content = file.read()
                        self.preview.setText(content)
                    except Exception as e:
                        self.preview.setText(f"Error reading file: {str(e)}")
                        self.logger.log_error(f"Error reading file {item_path}: {str(e)}")
                else:
                    self.preview.setText("Error: File not found.")
                    self.logger.log_error(f"File not found: {item_path}")
            self.logger.log_interaction(f"Updated preview for item: {item_path}")



    def setup_actions(self):
        actions = [
            ("folder-new", "🖿", self.create_folder),
            ("go-up", "🢁", self.go_up),
            ("edit-rename", "Rename", self.rename_item),
            ("document-properties", "Properties", self.show_properties),
            ("edit-copy", "Copy", self.copy_item),
            ("edit-paste", "Paste", self.paste_item),
            ("batch-process-menu", "𝗕𝗮𝘁𝗰𝗵 𝗣𝗿𝗼𝗰𝗲𝘀𝘀 𝗠𝗲𝗻𝘂", self.show_batch_process_menu),
            ("tag", "𝗧𝗮𝗴 𝗗𝗼𝗰𝘂𝗺𝗲𝗻𝘁", self.tag_item),
            ("edit-delete", "🗑", self.delete_item),
        ]

        for icon_name, action_name, method in actions:
            action = QAction(QIcon(f"icons/{icon_name}.png"), action_name, self)
            action.triggered.connect(method)
            self.toolbar.addAction(action)


    def show_batch_process_menu(self):
        menu = QMenu(self)
        menu.addAction("Copy Tagged", self.copy_tagged_items)
        menu.addAction("Paste Tagged", self.paste_tagged_items)
        menu.addAction("Delete Tagged", self.delete_tagged_items)
        menu.addAction("Untag All", self.model.untag_all)

        # Display the menu at the toolbar's position
        menu.exec(self.toolbar.mapToGlobal(self.toolbar.rect().bottomLeft()))


    def handle_double_click(self, index):
        item_path = self.model.filePath(index)
        self.tree.setRootIndex(index if os.path.isdir(item_path) else self.tree.rootIndex())
        self.logger.log_interaction(f"Double clicked on item: {item_path}")


    def create_folder(self):
        if self.tree.selectionModel().hasSelection():
            QMessageBox.warning(self, "Items Selected", "Please unselect all items before creating a new folder.")
            return
        index = self.tree.currentIndex()
        parent_path = self.model.rootPath()
        folder_name, ok = QInputDialog.getText(self, "Create Folder", "Folder name:")
        if ok and folder_name:
            new_folder_path = os.path.join(parent_path, folder_name)
            try:
                os.makedirs(new_folder_path, exist_ok=True)
                QMessageBox.information(self, "Folder Created", f"Folder '{folder_name}' created successfully.")
            except OSError as e:
                QMessageBox.critical(self, "Error", f"Failed to create folder: {e.strerror}")

    def delete_item(self):
        indexes = self.tree.selectedIndexes()
        for index in indexes:
            if index.column() == 0:
                file_path = self.model.filePath(index)
                try:
                    shutil.rmtree(file_path) if os.path.isdir(file_path) else os.remove(file_path)
                    self.model.remove(index)
                    self.logger.log_interaction(f"Deleted item: {file_path}")
                    QMessageBox.information(self, "Item Deleted", f"Deleted item: {file_path}")
                except Exception as e:
                    self.logger.log_error(f"Error deleting item: {str(e)}")
                    QMessageBox.critical(self, "Error", f"Failed to delete item: {str(e)}")

    def rename_item(self):
        index = self.tree.currentIndex()
        if index.isValid():
            item_path = self.model.filePath(index)
            new_name, ok = QInputDialog.getText(self, "Rename", "New name:", text=os.path.basename(item_path))
            if ok and new_name:
                new_path = os.path.join(os.path.dirname(item_path), new_name)
                try:
                    os.rename(item_path, new_path)
                    # Refresh the model
                    self.model.setRootPath(self.model.rootPath())
                    self.logger.log_interaction(f"Renamed item: {item_path} to {new_path}")
                    QMessageBox.information(self, "Item Renamed", f"Renamed item: {item_path} to {new_path}")
                except OSError as e:
                    self.logger.log_error(f"Error renaming item: {str(e)}")
                    QMessageBox.critical(self, "Error", f"Failed to rename item: {str(e)}")




    def show_properties(self):
        index = self.tree.currentIndex()
        if index.isValid():
            item_path = self.model.filePath(index)
            properties = (
                f"Path: {item_path}\n"
                f"Size: {os.path.getsize(item_path)} bytes\n"
                f"Modified: {os.path.getmtime(item_path)}"
            )
            QMessageBox.information(self, "Properties", properties)


    def go_up(self):
        current_index = self.tree.rootIndex()
        current_path = self.model.filePath(current_index)
        parent_path = os.path.dirname(current_path)
        parent_index = self.model.index(parent_path)

        # Set the new root index to the parent directory
        self.tree.setRootIndex(parent_index)
        # Untag all items when going up
        self.model.untag_all()
        self.logger.log_interaction(f"Navigated up from {current_path} to {parent_path}")


    def copy_item(self):
        self.clipboard = self.tree.selectedIndexes()
        self.logger.log_interaction("Copied items to clipboard")

    def paste_item(self):
        if not self.clipboard:
            QMessageBox.warning(self, "Clipboard Empty", "No items to paste.")
            return
        dest_index = self.tree.currentIndex()
        dest_path = self.model.filePath(dest_index)
        for index in self.clipboard:
            src_path = self.model.filePath(index)
            try:
                if os.path.isfile(src_path):
                    shutil.copy2(src_path, dest_path)
                else:
                    shutil.copytree(src_path, os.path.join(dest_path, os.path.basename(src_path)))
                self.logger.log_interaction(f"Pasted item: {src_path} to {dest_path}")
                QMessageBox.information(self, "Item Pasted", f"Pasted item: {src_path} to {dest_path}")
            except Exception as e:
                self.logger.log_error(f"Error pasting item: {str(e)}")
                QMessageBox.critical(self, "Error", f"Failed to paste item: {str(e)}")

    def tag_item(self):
        index = self.tree.currentIndex()
        if index.isValid():
            tagged = self.model.filePath(index) in self.model.tagged_items
            self.model.set_tagged(index, not tagged)
            action = "Tagged" if not tagged else "Untagged"
            self.logger.log_interaction(f"{action} item: {self.model.filePath(index)}")

    def copy_tagged_items(self):
        if not self.model.tagged_items:
            QMessageBox.warning(self, "No Tagged Items", "No tagged items to copy.")
            return
        self.clipboard = list(self.model.tagged_items)
        self.logger.log_interaction("Copied tagged items to clipboard")

    def paste_tagged_items(self):
        if not self.clipboard:
            QMessageBox.warning(self, "Clipboard Empty", "No items to paste.")
            return
        dest_index = self.tree.currentIndex()
        dest_path = self.model.filePath(dest_index)
        for src_path in self.clipboard:
            try:
                if os.path.isfile(src_path):
                    shutil.copy2(src_path, dest_path)
                else:
                    shutil.copytree(src_path, os.path.join(dest_path, os.path.basename(src_path)))
                self.logger.log_interaction(f"Pasted tagged item: {src_path} to {dest_path}")
                QMessageBox.information(self, "Item Pasted", f"Pasted tagged item: {src_path} to {dest_path}")
            except Exception as e:
                self.logger.log_error(f"Error pasting tagged item: {str(e)}")
                QMessageBox.critical(self, "Error", f"Failed to paste tagged item: {str(e)}")

    def delete_tagged_items(self):
        if not self.model.tagged_items:
            QMessageBox.warning(self, "No Tagged Items", "No tagged items to delete.")
            return
        reply = QMessageBox.question(self, 'Confirm Delete', f"Are you sure you want to delete {len(self.model.tagged_items)} tagged items?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            for item_path in self.model.tagged_items:
                try:
                    shutil.rmtree(item_path) if os.path.isdir(item_path) else os.remove(item_path)
                    self.logger.log_interaction(f"Deleted tagged item: {item_path}")
                except Exception as e:
                    self.logger.log_error(f"Error deleting tagged item: {str(e)}")
            self.model.untag_all()
            QMessageBox.information(self, "Items Deleted", "Tagged items deleted successfully.")
