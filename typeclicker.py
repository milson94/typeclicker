import sys
import random
import pyautogui
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QShortcut
from PyQt5.QtGui import QKeySequence, QMouseEvent, QColor, QBrush, QPixmap, QPainter, QFont
from PyQt5.QtCore import Qt, QPoint, pyqtSignal

class DraggableImage(QWidget):
    position_changed = pyqtSignal(QPoint, str)  # Signal to notify position and letter changes

    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.setFixedSize(30, 30)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setWindowOpacity(1.0)

        self.color = color
        self.key = None
        self.letter = ""

        self.update_pixmap()

        # Initialize dragging variables
        self.drag_position = None

    def update_pixmap(self):
        pixmap = QPixmap(30, 30)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setBrush(QBrush(self.color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 30, 30)

        if self.letter:
            painter.setPen(Qt.white)
            painter.setFont(QFont("Arial", 12))
            painter.drawText(pixmap.rect(), Qt.AlignCenter, self.letter)

        painter.end()
        self.setPixmap(pixmap)

    def setPixmap(self, pixmap):
        self.pixmap = pixmap
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pixmap)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        elif event.button() == Qt.RightButton and not self.key:  # Only allow key assignment if no key is assigned yet
            self.grabKeyboard()  # Start listening for key presses

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            new_pos = event.globalPos() - self.drag_position
            self.move(new_pos)
            self.position_changed.emit(new_pos, self.letter)  # Emit the new position and letter
            event.accept()

    def keyPressEvent(self, event):
        if not self.key:  # Only assign a key if none is assigned yet
            self.key = event.key()
            self.letter = event.text().upper()
            self.update_pixmap()
            self.position_changed.emit(self.pos(), self.letter)  # Emit the new letter
            self.releaseKeyboard()  # Stop listening for key presses

class NotePadPro(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("NotePad Pro")

        # Remove window frame and make it always on top
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # Initialize dragging variables
        self.drag_position = None

        # Create the plus button
        self.add_note_button = QPushButton("+", self)
        self.add_note_button.setFixedSize(40, 40)
        self.add_note_button.setStyleSheet("""
            QPushButton {
                background-color: #333;
                border: none;
                border-radius: 20px;
                color: white;
                font-size: 24px;
            }
        """)
        self.add_note_button.clicked.connect(self.on_button_click)

        # Create a layout and add the button to the center
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)  # Reduce margins to shrink the window size

        # Add a stretchable spacer to push the button to the center vertically
        main_layout.addStretch()

        # Create a horizontal layout for the center alignment
        center_layout = QHBoxLayout()
        center_layout.addStretch()  # Add a stretchable spacer to push the button to the center horizontally
        center_layout.addWidget(self.add_note_button)
        center_layout.addStretch()  # Add a stretchable spacer to push the button to the center horizontally

        # Add the center layout to the main layout
        main_layout.addLayout(center_layout)

        # Add a stretchable spacer to push the button to the center vertically
        main_layout.addStretch()

        # Set the layout
        self.setLayout(main_layout)

        # Adjust window size to fit the button
        self.adjustSize()

        # Center the window on the screen
        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

        # Register the Ctrl+A+B shortcut
        self.shortcut_ctrl_ab = QShortcut(QKeySequence("Ctrl+A+B"), self)
        self.shortcut_ctrl_ab.activated.connect(self.close)

        # Register the Esc shortcut
        self.shortcut_esc = QShortcut(QKeySequence("Esc"), self)
        self.shortcut_esc.activated.connect(self.close)

        # Dictionary to keep track of image positions and letters
        self.image_positions = {}

        # List to keep track of all created images
        self.created_images = []

        # Store the initial mouse position
        self.initial_mouse_position = pyautogui.position()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def on_button_click(self):
        print("Button clicked!")
        self.create_random_image()

    def create_random_image(self):
        # Generate a random color
        random_color = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        print(f"Creating image with color: {random_color.name()}")

        # Create a draggable image
        image = DraggableImage(random_color)
        image.position_changed.connect(self.update_image_position)
        image.show()

        # Center the image on the screen
        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - image.width()) // 2
        y = (screen_geometry.height() - image.height()) // 2
        image.move(x, y)
        print(f"Moving image to position: ({x}, {y})")

        # Keep track of the image position and letter
        self.image_positions[image] = (image.pos(), image.letter)

        # Keep track of the created image
        self.created_images.append(image)

    def update_image_position(self, pos, letter):
        # Update the position and letter of the image in the dictionary
        sender_image = self.sender()
        self.image_positions[sender_image] = (pos, letter)
        print(f"Image {letter} moved to position: {pos}")  # Debugging line

    def keyPressEvent(self, event):
        print(f"Key pressed: {event.key()}")  # Debugging line
        for image, (pos, letter) in self.image_positions.items():
            if image.key == event.key():  # Check if the pressed key matches the assigned key
                print(f"Simulating click at position: {pos} for image {letter}")  # Debugging line
                self.simulate_click(pos)
                break

    def simulate_click(self, pos):
        # Simulate a mouse click at the given position using pyautogui
        pyautogui.click(pos.x(), pos.y())
        # Move the mouse back to the main window containing the + button
        main_window_pos = self.mapToGlobal(self.rect().center())
        offset_x = random.randint(-30, -20)
        offset_y = random.randint(-30, 30)
        pyautogui.moveTo(main_window_pos.x() + offset_x, main_window_pos.y() + offset_y)
        # Simulate two clicks to ensure the main window is fully active
        pyautogui.click()
        pyautogui.click()

    def closeEvent(self, event):
        # Close all created images when the main window is closed
        for image in self.created_images:
            image.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NotePadPro()
    window.show()
    sys.exit(app.exec_())
