import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from ui.main_window import MainWindow
from paths import resource_path


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("AutoSub")
    app.setStyle("Fusion")
    app.setWindowIcon(QIcon(resource_path("assets/app_icon.svg")))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
