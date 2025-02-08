import sys
import os
import yt_dlp
import time
import ctypes

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPoint, QUrl, QTimer, QSize, QEvent, QSettings
from PyQt5.QtGui import QIcon, QPainter, QColor, QPixmap, QFont, QPen
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QProgressBar,
    QFileDialog,
    QComboBox,
    QCheckBox,
    QProxyStyle,
    QStyle,
    QStyleOptionComboBox,
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

# --- Custom QProxyStyle to remove focus rectangle for combo boxes ---
class NoFocusRectStyle(QProxyStyle):
    def drawPrimitive(self, element, option, painter, widget=None):
        if element == QStyle.PE_FrameFocusRect:
            return
        return super().drawPrimitive(element, option, painter, widget)

# --- Custom ComboBox subclass ---
class NoFocusComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyle(NoFocusRectStyle(self.style()))
        self.setEditable(False)
    def paintEvent(self, event):
        opt = QStyleOptionComboBox()
        self.initStyleOption(opt)
        opt.state &= ~QStyle.State_HasFocus
        painter = QPainter(self)
        self.style().drawComplexControl(QStyle.CC_ComboBox, opt, painter, self)
        self.style().drawControl(QStyle.CE_ComboBoxLabel, opt, painter, self)

# --- Custom QLineEdit that emits a signal on focus out ---
class CustomLineEdit(QLineEdit):
    focusOut = pyqtSignal()
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.focusOut.emit()

# --- Dynamic Progress Bar ---
class DynamicProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextVisible(False)
        self.setStyleSheet("""
            QProgressBar {
                background-color: #151515;
                border: 1px solid #333;
                border-radius: 5px;
                text-align: center;
                color: white;
                font: 12pt "Segoe UI";
            }
            QProgressBar::chunk {
                background-color: #39FF14;
                border-radius: 5px;
            }
        """)
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        value = self.value()
        text = f"{int(value)}%"
        textColor = QColor("white") if value < 50 else QColor("black")
        painter.setPen(QPen(textColor))
        font = QFont(self.font().family(), self.font().pointSize(), QFont.Bold)
        painter.setFont(font)
        rect = self.rect()
        painter.drawText(rect, Qt.AlignCenter, text)

# --- Global resource path helper ---
def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.getcwd())
    return os.path.join(base_path, relative_path)

# --- Force taskbar icon update ---
def forceTaskbarIcon(winId):
    GCL_HICON = -14
    GCL_HICONSM = -34
    icon_path = resource_path("UI_Photos/favicon.ico")
    hIcon = ctypes.windll.user32.LoadImageW(None, icon_path, 1, 256, 256, 0x00000010)
    if hIcon:
        hwnd = int(winId)
        ctypes.windll.user32.SetClassLongPtrW(hwnd, GCL_HICON, hIcon)
        ctypes.windll.user32.SetClassLongPtrW(hwnd, GCL_HICONSM, hIcon)
    else:
        print("Failed to load icon via LoadImageW")

# --- Options Popup Widget ---
class OptionsWidget(QWidget):
    def __init__(self, mute_at_startup, light_mode, open_folder_after_download, main_window):
        super().__init__(None, flags=Qt.Tool | Qt.FramelessWindowHint)
        self.setFocusPolicy(Qt.NoFocus)
        self.light_mode = light_mode
        self.main_window = main_window
        self.initUI(mute_at_startup, open_folder_after_download)
        self.updateStyleMode()

    def initUI(self, mute_at_startup, open_folder_after_download):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        self.muteAtStartupCheck = QCheckBox("Mute at startup")
        self.muteAtStartupCheck.setChecked(mute_at_startup)
        self.muteAtStartupCheck.setFocusPolicy(Qt.NoFocus)
        layout.addWidget(self.muteAtStartupCheck)
        self.lightModeCheck = QCheckBox("Light Mode")
        self.lightModeCheck.setChecked(self.light_mode)
        self.lightModeCheck.setFocusPolicy(Qt.NoFocus)
        layout.addWidget(self.lightModeCheck)
        self.openFolderCheck = QCheckBox("Open folder after download")
        self.openFolderCheck.setChecked(open_folder_after_download)
        self.openFolderCheck.setFocusPolicy(Qt.NoFocus)
        layout.addWidget(self.openFolderCheck)
        self.muteAtStartupCheck.toggled.connect(
            lambda _: self.main_window.setOptions(
                self.muteAtStartupCheck.isChecked(),
                self.lightModeCheck.isChecked(),
                self.openFolderCheck.isChecked()
            )
        )
        self.lightModeCheck.toggled.connect(
            lambda _: self.main_window.setOptions(
                self.muteAtStartupCheck.isChecked(),
                self.lightModeCheck.isChecked(),
                self.openFolderCheck.isChecked()
            )
        )
        self.openFolderCheck.toggled.connect(
            lambda _: self.main_window.setOptions(
                self.muteAtStartupCheck.isChecked(),
                self.lightModeCheck.isChecked(),
                self.openFolderCheck.isChecked()
            )
        )

    def updateStyleMode(self):
        if self.light_mode:
            self.setStyleSheet("""
                QWidget {
                    background-color: #ffffff;
                    border: none;
                    border-radius: 5px;
                }
                QCheckBox {
                    color: black;
                    font: 12pt "Segoe UI";
                    padding: 2px;
                    outline: none;
                }
                QCheckBox::indicator:focus { outline: none; }
                QCheckBox:hover { background-color: #ddd; }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #161616;
                    border: none;
                    border-radius: 5px;
                }
                QCheckBox {
                    color: white;
                    font: 12pt "Segoe UI";
                    padding: 2px;
                    outline: none;
                }
                QCheckBox::indicator:focus { outline: none; }
                QCheckBox:hover { background-color: #2a2a2a; }
            """)

    def getMuteAtStartup(self):
        return self.muteAtStartupCheck.isChecked()
    def getLightMode(self):
        return self.lightModeCheck.isChecked()
    def getOpenFolderAfterDownload(self):
        return self.openFolderCheck.isChecked()

# --- Background Widget ---
class BackgroundWidget(QWidget):
    def __init__(self, parent=None, bg_color="#0d0d0d"):
        super().__init__(parent)
        self.bg_color = QColor(bg_color)
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.bg_color)
        super().paintEvent(event)

# --- Download Worker ---
class DownloadWorker(QThread):
    progress_signal = pyqtSignal(float)
    status_signal = pyqtSignal(str)
    details_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    error_signal = pyqtSignal(str)
    def __init__(self, url, download_dir, audio_format="wav", quality="320k"):
        super().__init__()
        self.url = url
        self.download_dir = download_dir
        self.audio_format = audio_format.lower()
        self.quality = quality
        self.downloaded_file = None
    def run(self):
        ffmpeg_dir = resource_path("ffmpeg_bin/bin")
        if os.path.isdir(ffmpeg_dir):
            print("DEBUG: ffmpeg_bin/bin contents:", os.listdir(ffmpeg_dir))
        else:
            print("DEBUG: ffmpeg_bin/bin not found!")
        def progress_hook(info):
            if info.get('status') == 'downloading':
                total = info.get('total_bytes') or info.get('total_bytes_estimate')
                if total:
                    downloaded = info.get('downloaded_bytes', 0)
                    percent = downloaded / total * 100
                    speed = info.get('speed', 0)
                    eta = info.get('eta', 0)
                    speed_kbps = speed / 1024 if speed else 0
                    self.progress_signal.emit(percent)
                    self.status_signal.emit(f"Downloading... {percent:.1f}%")
                    self.details_signal.emit(f"Speed: {speed_kbps:.1f} KB/s | ETA: {eta} sec")
            elif info.get('status') == 'finished':
                filename = info.get("filename")
                if filename:
                    self.downloaded_file = os.path.abspath(filename)
                self.progress_signal.emit(100)
                self.status_signal.emit("Download completed, converting...")
        postprocessors = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': self.audio_format,
        }]
        if self.audio_format == "mp3":
            postprocessors[0]['preferredquality'] = self.quality.replace("k", "")
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
            'updatetime': False,
            'ffmpeg_location': ffmpeg_dir,
            'postprocessors': postprocessors,
            'progress_hooks': [progress_hook],
            'quiet': True,
            'no_warnings': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            if self.downloaded_file and os.path.exists(self.downloaded_file):
                os.utime(self.downloaded_file, (time.time(), time.time()))
            self.status_signal.emit("Download completed!")
            self.finished_signal.emit()
        except Exception as e:
            self.error_signal.emit(str(e))

# --- Title Bar ---
class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.start = QPoint(0, 0)
        self.pressing = False
        self.setStyleSheet("background-color: " + parent.titleBarBg + ";")
        self.optionsButton = QPushButton("", self)
        self.optionsButton.setFixedSize(140, 30)
        favicon = QPixmap(resource_path("UI_Photos/favicon.ico"))
        self.optionsButton.setIcon(QIcon(favicon))
        self.optionsButton.setIconSize(QSize(24, 24))
        self.optionsButton.setText(" Options")
        self.optionsButton.setStyleSheet(parent.optionsBtnStyle)
        self.optionsButton.clicked.connect(self.parent.toggleOptions)
        self.titleLabel = QLabel("Waver by getbetter", self)
        self.titleLabel.setStyleSheet(parent.titleLabelStyle)
        self.titleLabel.setAlignment(Qt.AlignCenter)
        self.btnMinimize = QPushButton("–", self)
        self.btnMinimize.setFixedSize(30, 30)
        self.btnMinimize.setStyleSheet(parent.minimizeBtnStyle)
        self.btnMinimize.clicked.connect(self.parent.showMinimized)
        self.btnClose = QPushButton("✕", self)
        self.btnClose.setFixedSize(30, 30)
        self.btnClose.setStyleSheet(parent.closeBtnStyle)
        self.btnClose.clicked.connect(self.parent.close)
        mainLayout = QHBoxLayout(self)
        mainLayout.setContentsMargins(10, 0, 10, 0)
        mainLayout.addWidget(self.optionsButton)
        mainLayout.addStretch(1)
        mainLayout.addWidget(self.titleLabel)
        mainLayout.addStretch(1)
        rightLayout = QHBoxLayout()
        rightLayout.setContentsMargins(0, 0, 0, 0)
        rightLayout.setSpacing(5)
        rightLayout.addWidget(self.btnMinimize)
        rightLayout.addWidget(self.btnClose)
        mainLayout.addLayout(rightLayout)
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Center titleLabel relative to the entire title bar (i.e. the window width)
        new_x = (self.width() - self.titleLabel.width()) // 2
        self.titleLabel.move(new_x, self.titleLabel.y())
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start = event.globalPos()
            self.pressing = True
    def mouseMoveEvent(self, event):
        if self.pressing:
            delta = event.globalPos() - self.start
            self.parent.move(self.parent.pos() + delta)
            self.start = event.globalPos()
    def mouseReleaseEvent(self, event):
        self.pressing = False

# --- Main Window ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.muteAtStartup = False
        self.lightMode = False
        self.openFolderAfterDownload = True
        self.titleBarBg = "#0d0d0d"
        self.optionsBtnStyle = """
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font: 16pt 'Segoe UI';
            }
            QPushButton:hover { background-color: #2a2a2a; }
            QPushButton:pressed { background-color: #444; }
        """
        self.titleLabelStyle = "color: white; font: bold 16pt 'Segoe UI';"
        self.minimizeBtnStyle = """
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font: bold 14pt 'Segoe UI';
            }
            QPushButton:hover { background-color: #555; }
        """
        self.closeBtnStyle = """
            QPushButton { background-color: transparent; color: white; border: none; }
            QPushButton:hover { background-color: #ff5555; }
        """
        self.bgColor = "#0d0d0d"
        self.lineEditStyle = """
            QLineEdit {
                background-color: #161616;
                border: 2px solid #333;
                padding: 10px;
                border-radius: 5px;
                color: white;
                font: 14pt 'Segoe UI';
            }
            QLineEdit:focus { border: 2px solid #1e90ff; }
        """
        self.darkDropdownStyle = (
            "QComboBox {"
            "   background-color: #161616;"
            "   border: 2px solid #333;"
            "   padding: 8px 12px;"
            "   border-radius: 5px;"
            "   color: white;"
            "   font: 13pt 'Segoe UI';"
            "   outline: none;"
            "}"
            "QComboBox:focus { border: 2px solid #1e90ff; outline: none; }"
            "QComboBox::drop-down { border: none; background: transparent; width: 0px; }"
            "QComboBox QAbstractItemView {"
            "   background: #161616;"
            "   border: 2px solid #333;"
            "   border-radius: 5px;"
            "   color: white;"
            "   padding: 4px;"
            "}"
            "QComboBox QAbstractItemView::item:selected { background: #1e90ff; color: white; }"
        )
        self.lightDropdownStyle = (
            "QComboBox {"
            "   background-color: #ffffff;"
            "   border: 2px solid #ccc;"
            "   padding: 8px 12px;"
            "   border-radius: 5px;"
            "   color: black;"
            "   font: 13pt 'Segoe UI';"
            "   outline: none;"
            "}"
            "QComboBox:focus { border: 2px solid #1e90ff; outline: none; }"
            "QComboBox::drop-down { border: none; background: transparent; width: 0px; }"
            "QComboBox QAbstractItemView {"
            "   background-color: #ffffff;"
            "   border: 2px solid #ccc;"
            "   border-radius: 5px;"
            "   color: black;"
            "   padding: 4px;"
            "}"
            "QComboBox QAbstractItemView::item:selected { background: #1e90ff; color: white; }"
        )
        self.currentDropdownStyle = self.darkDropdownStyle

        self.optionsWidget = None

        self.settings = QSettings("MyCompany", "WaverApp")
        self.loadSettings()

        self.resize(900, 550)
        self.initUI()
        self.initAudio()
        self.installEventFilter(self)

    def loadSettings(self):
        self.muteAtStartup = self.settings.value("muteAtStartup", False, type=bool)
        self.lightMode = self.settings.value("lightMode", False, type=bool)
        self.openFolderAfterDownload = self.settings.value("openFolderAfterDownload", True, type=bool)
        downloadDir = self.settings.value("downloadDir", os.path.join(os.environ.get("USERPROFILE", os.getcwd()), "Downloads"))
        self.formatSetting = self.settings.value("audioFormat", "WAV")
        self.qualitySetting = self.settings.value("quality", "320k")
        self._savedDownloadDir = downloadDir

    def saveSettings(self):
        self.settings.setValue("muteAtStartup", self.muteAtStartup)
        self.settings.setValue("lightMode", self.lightMode)
        self.settings.setValue("openFolderAfterDownload", self.openFolderAfterDownload)
        self.settings.setValue("downloadDir", self.downloaderLocInput.text())
        self.settings.setValue("audioFormat", self.formatDropdown.currentText())
        self.settings.setValue("quality", self.qualityDropdown.currentText())

    def setDarkStyles(self):
        self.titleBarBg = "#0d0d0d"
        self.optionsBtnStyle = """
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font: 16pt 'Segoe UI';
            }
            QPushButton:hover { background-color: #2a2a2a; }
            QPushButton:pressed { background-color: #444; }
        """
        self.titleLabelStyle = "color: white; font: bold 16pt 'Segoe UI';"
        self.minimizeBtnStyle = """
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font: bold 14pt 'Segoe UI';
            }
            QPushButton:hover { background-color: #555; }
        """
        self.closeBtnStyle = """
            QPushButton { background-color: transparent; color: white; border: none; }
            QPushButton:hover { background-color: #ff5555; }
        """
        self.bgColor = "#0d0d0d"
        self.lineEditStyle = """
            QLineEdit {
                background-color: #161616;
                border: 2px solid #333;
                padding: 10px;
                border-radius: 5px;
                color: white;
                font: 14pt 'Segoe UI';
            }
            QLineEdit:focus { border: 2px solid #1e90ff; }
        """
        self.currentDropdownStyle = self.darkDropdownStyle

    def setLightStyles(self):
        self.titleBarBg = "#f0f0f0"
        self.optionsBtnStyle = """
            QPushButton {
                background-color: transparent;
                color: black;
                border: none;
                font: 16pt 'Segoe UI';
            }
            QPushButton:hover { background-color: #ddd; }
            QPushButton:pressed { background-color: #bbb; }
        """
        self.titleLabelStyle = "color: black; font: bold 16pt 'Segoe UI';"
        self.minimizeBtnStyle = """
            QPushButton {
                background-color: transparent;
                color: black;
                border: none;
                font: bold 14pt 'Segoe UI';
            }
            QPushButton:hover { background-color: #ccc; }
        """
        self.closeBtnStyle = """
            QPushButton { background-color: transparent; color: black; border: none; }
            QPushButton:hover { background-color: #ffaaaa; }
        """
        self.bgColor = "#f0f0f0"
        self.lineEditStyle = """
            QLineEdit {
                background-color: #ffffff;
                border: 2px solid #ccc;
                padding: 10px;
                border-radius: 5px;
                color: black;
                font: 14pt 'Segoe UI';
            }
            QLineEdit:focus { border: 2px solid #1e90ff; }
        """
        self.currentDropdownStyle = self.lightDropdownStyle

    def updateStyles(self):
        if self.lightMode:
            self.setLightStyles()
        else:
            self.setDarkStyles()
        self.backgroundWidget.bg_color = QColor(self.bgColor)
        self.backgroundWidget.update()
        self.titleBar.setStyleSheet("background-color: " + self.titleBarBg + ";")
        self.titleBar.optionsButton.setStyleSheet(self.optionsBtnStyle)
        self.titleBar.titleLabel.setStyleSheet(self.titleLabelStyle)
        self.titleBar.btnMinimize.setStyleSheet(self.minimizeBtnStyle)
        self.titleBar.btnClose.setStyleSheet(self.closeBtnStyle)
        self.downloaderLocInput.setStyleSheet(self.lineEditStyle)
        self.downloaderUrlInput.setStyleSheet(self.lineEditStyle)
        self.formatDropdown.setStyleSheet(self.currentDropdownStyle)
        self.qualityDropdown.setStyleSheet(self.currentDropdownStyle)
        self.fileTypeLabel.setStyleSheet("color: " + ("white" if not self.lightMode else "black") + "; font: 13pt 'Segoe UI';")
        self.qualityLabel.setStyleSheet("color: " + ("white" if not self.lightMode else "black") + "; font: 13pt 'Segoe UI';")
        self.videoInfoLabel.setStyleSheet("color: " + ("#ddd" if not self.lightMode else "#333") + "; font: 10pt 'Segoe UI';")
        self.downloadStatusLabel.setStyleSheet("color: " + ("white" if not self.lightMode else "black") + "; font: bold 14pt 'Segoe UI';")
        if self.lightMode:
            self.pasteButton.setStyleSheet("""
                QPushButton {
                    background-color: #ffffff;
                    color: black;
                    border: 2px solid #ccc;
                    padding: 10px 15px;
                    border-radius: 5px;
                    font: 12pt 'Segoe UI';
                }
                QPushButton:hover { background-color: #ddd; }
                QPushButton:pressed { background-color: #bbb; }
            """)
            self.muteButton.setStyleSheet("""
                QPushButton {
                    background-color: #ffffff;
                    color: black;
                    border: 2px solid #ccc;
                    border-radius: 8px;
                    font: bold 12pt 'Segoe UI';
                }
                QPushButton:hover { background-color: #ddd; }
                QPushButton:pressed { background-color: #bbb; }
            """)
            self.titleBar.optionsButton.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: black;
                    border: none;
                    font: 16pt 'Segoe UI';
                }
                QPushButton:hover { background-color: #ddd; }
                QPushButton:pressed { background-color: #bbb; }
            """)
        else:
            self.pasteButton.setStyleSheet("""
                QPushButton {
                    background-color: #161616;
                    color: white;
                    border: 2px solid #333;
                    padding: 10px 15px;
                    border-radius: 5px;
                    font: 12pt 'Segoe UI';
                }
                QPushButton:hover { background-color: #2a2a2a; }
                QPushButton:pressed { background-color: #444; }
            """)
            self.muteButton.setStyleSheet("""
                QPushButton {
                    background-color: #161616;
                    color: white;
                    border: 2px solid #333;
                    border-radius: 8px;
                    font: bold 12pt 'Segoe UI';
                }
                QPushButton:hover { background-color: #2a2a2a; }
                QPushButton:pressed { background-color: #444; }
            """)
            self.titleBar.optionsButton.setStyleSheet(self.optionsBtnStyle)

    def initUI(self):
        self.backgroundWidget = BackgroundWidget(self, bg_color=self.bgColor)
        mainLayout = QVBoxLayout(self.backgroundWidget)
        mainLayout.setSpacing(0)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        self.titleBar = TitleBar(self)
        self.titleBar.setFixedHeight(40)
        mainLayout.addWidget(self.titleBar)
        contentWidget = QWidget()
        contentLayout = QVBoxLayout(contentWidget)
        contentLayout.setSpacing(15)
        contentLayout.setContentsMargins(20, 20, 20, 20)
        # --- Top Controls ---
        topControlsLayout = QHBoxLayout()
        fileTypeLayout = QHBoxLayout()
        fileTypeLayout.setSpacing(2)
        self.fileTypeLabel = QLabel("File Type:")
        self.fileTypeLabel.setFixedWidth(80)
        self.fileTypeLabel.setStyleSheet("color: " + ("white" if not self.lightMode else "black") + "; font: 13pt 'Segoe UI';")
        fileTypeLayout.addWidget(self.fileTypeLabel)
        self.formatDropdown = NoFocusComboBox()
        self.formatDropdown.addItems(["WAV", "MP3"])
        self.formatDropdown.setCurrentText(self.formatSetting)
        self.formatDropdown.setStyleSheet(self.currentDropdownStyle)
        self.formatDropdown.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        fileTypeLayout.addWidget(self.formatDropdown)
        topControlsLayout.addLayout(fileTypeLayout)
        qualityLayout = QHBoxLayout()
        qualityLayout.setSpacing(2)
        self.qualityLabel = QLabel("Quality:")
        self.qualityLabel.setFixedWidth(80)
        self.qualityLabel.setStyleSheet("color: " + ("white" if not self.lightMode else "black") + "; font: 13pt 'Segoe UI';")
        qualityLayout.addWidget(self.qualityLabel)
        self.qualityDropdown = NoFocusComboBox()
        self.qualityDropdown.addItems(["128k", "320k"])
        self.qualityDropdown.setCurrentText(self.qualitySetting)
        self.qualityDropdown.setStyleSheet(self.currentDropdownStyle)
        self.qualityDropdown.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        qualityLayout.addWidget(self.qualityDropdown)
        topControlsLayout.addLayout(qualityLayout)
        self.muteButton = QPushButton("Mute")
        self.muteButton.setFixedSize(100, 40)
        self.muteButton.setStyleSheet("""
            QPushButton {
                background-color: #161616;
                color: white;
                border: 2px solid #333;
                border-radius: 8px;
                font: bold 12pt 'Segoe UI';
            }
            QPushButton:hover { background-color: #2a2a2a; }
            QPushButton:pressed { background-color: #444; }
        """)
        self.muteButton.clicked.connect(self.toggleMute)
        topControlsLayout.addWidget(self.muteButton)
        contentLayout.addLayout(topControlsLayout)
        # --- File Save Path ---
        pathLayout = QHBoxLayout()
        self.downloaderLocInput = QLineEdit()
        self.downloaderLocInput.setText(self._savedDownloadDir)
        self.downloaderLocInput.setStyleSheet(self.lineEditStyle)
        pathLayout.addWidget(self.downloaderLocInput, stretch=1)
        browseBtn = QPushButton("Browse")
        browseBtn.clicked.connect(self.browseDownloadFolder)
        browseBtn.setStyleSheet("""
            QPushButton {
                background-color: #147cd3;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 8px;
                font: 12pt 'Segoe UI';
            }
            QPushButton:hover { background-color: #126bb0; }
            QPushButton:pressed { background-color: #0f5a8e; }
        """)
        pathLayout.addWidget(browseBtn)
        contentLayout.addLayout(pathLayout)
        # --- URL Input, Paste Button, and Video Metadata ---
        urlInputLayout = QHBoxLayout()
        self.downloaderUrlInput = CustomLineEdit()
        self.downloaderUrlInput.setPlaceholderText("Enter YouTube URL")
        self.downloaderUrlInput.setStyleSheet(self.lineEditStyle)
        self.downloaderUrlInput.focusOut.connect(self.updateVideoInfo)
        urlInputLayout.addWidget(self.downloaderUrlInput, stretch=1)
        self.pasteButton = QPushButton("Paste")
        self.pasteButton.clicked.connect(self.handlePaste)
        self.pasteButton.setStyleSheet("""
            QPushButton {
                background-color: #161616;
                color: white;
                border: 2px solid #333;
                padding: 10px 15px;
                border-radius: 5px;
                font: 12pt 'Segoe UI';
            }
            QPushButton:hover { background-color: #2a2a2a; }
            QPushButton:pressed { background-color: #444; }
        """)
        urlInputLayout.addWidget(self.pasteButton)
        contentLayout.addLayout(urlInputLayout)
        self.videoInfoLabel = QLabel("")
        self.videoInfoLabel.setStyleSheet("color: " + ("#ddd" if not self.lightMode else "#333") + "; font: 10pt 'Segoe UI';")
        self.videoInfoLabel.setWordWrap(True)
        contentLayout.addWidget(self.videoInfoLabel)
        # --- Download Progress Bar, Status, and Button ---
        self.downloadProgressBar = DynamicProgressBar()
        self.downloadProgressBar.setMinimum(0)
        self.downloadProgressBar.setMaximum(100)
        self.downloadProgressBar.setValue(0)
        self.downloadProgressBar.hide()
        contentLayout.addWidget(self.downloadProgressBar)
        self.downloadStatusLabel = QLabel("")
        self.downloadStatusLabel.setStyleSheet("color: " + ("white" if not self.lightMode else "black") + "; font: bold 14pt 'Segoe UI';")
        self.downloadStatusLabel.setAlignment(Qt.AlignCenter)
        contentLayout.addWidget(self.downloadStatusLabel)
        self.downloadButton = QPushButton("Download Audio")
        self.downloadButton.clicked.connect(self.startDownload)
        self.downloadButton.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #147cd3, stop:1 #126bb0);
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font: bold 14pt 'Segoe UI';
            }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #126bb0, stop:1 #0f5a8e); }
            QPushButton:pressed { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0f5a8e, stop:1 #0c4675); }
        """)
        contentLayout.addWidget(self.downloadButton)
        mainLayout.addWidget(contentWidget)
        self.setCentralWidget(self.backgroundWidget)
        self.updateStyles()

    def initAudio(self):
        self.audioPlayer = QMediaPlayer()
        wav_path = resource_path(os.path.join("music", "ooiiaa.mp3"))
        url = QUrl.fromLocalFile(wav_path)
        self.audioPlayer.setMedia(QMediaContent(url))
        self.audioPlayer.setVolume(50)
        if self.muteAtStartup:
            self.audioPlayer.setMuted(True)
            self.muteButton.setText("Unmute")
        else:
            self.audioPlayer.play()
            self.muteButton.setText("Mute")

    def toggleMute(self):
        if self.audioPlayer.isMuted():
            self.audioPlayer.setMuted(False)
            self.muteButton.setText("Mute")
        else:
            self.audioPlayer.setMuted(True)
            self.muteButton.setText("Unmute")

    def pasteFromClipboard(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            self.downloaderUrlInput.setText(text)

    def handlePaste(self):
        self.pasteFromClipboard()
        QTimer.singleShot(100, self.updateVideoInfo)

    def browseDownloadFolder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder", self.downloaderLocInput.text())
        if folder:
            self.downloaderLocInput.setText(folder)

    def updateVideoInfo(self):
        url = self.downloaderUrlInput.text().strip()
        if not url:
            self.videoInfoLabel.setText("")
            return
        video_info = self.fetch_video_info(url)
        self.videoInfoLabel.setText(video_info)

    def fetch_video_info(self, url):
        try:
            opts = {'quiet': True, 'skip_download': True}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown Title')
                duration = info.get('duration', 0)
                uploader = info.get('uploader', 'Unknown')
                view_count = info.get('view_count', 0)
                minutes = duration // 60
                seconds = duration % 60
                return f"Title: {title}\nDuration: {minutes}m {seconds}s\nUploader: {uploader}\nViews: {view_count}"
        except Exception as e:
            return "Could not fetch video info."

    def startDownload(self):
        url = self.downloaderUrlInput.text().strip()
        if not url:
            self.downloadStatusLabel.setText("Please enter a YouTube URL.")
            return
        self.downloadProgressBar.setValue(0)
        self.downloadProgressBar.show()
        self.downloadButton.setEnabled(False)
        self.downloadStatusLabel.setText("Starting download...")
        download_dir = self.downloaderLocInput.text()
        audio_format = self.formatDropdown.currentText().lower()
        quality = self.qualityDropdown.currentText()
        self.worker = DownloadWorker(url, download_dir, audio_format=audio_format, quality=quality)
        self.worker.progress_signal.connect(lambda value: self.downloadProgressBar.setValue(int(value)))
        self.worker.status_signal.connect(self.downloadStatusLabel.setText)
        self.worker.details_signal.connect(lambda details: self.downloadStatusLabel.setText(f"{self.downloadStatusLabel.text()} | {details}"))
        self.worker.error_signal.connect(lambda err: self.downloadStatusLabel.setText(f"Error: {err}"))
        self.worker.finished_signal.connect(lambda: self.downloadStatusLabel.setText("Download completed!"))
        self.worker.finished_signal.connect(lambda: self.downloadButton.setEnabled(True))
        if self.openFolderAfterDownload:
            self.worker.finished_signal.connect(lambda: self.openDownloadFolder(download_dir))
        self.worker.error_signal.connect(lambda err: self.downloadButton.setEnabled(True))
        self.worker.start()

    def openDownloadFolder(self, folder):
        try:
            os.startfile(folder)
        except Exception as e:
            print("Error opening folder:", e)

    def toggleOptions(self):
        if self.optionsWidget is None:
            self.optionsWidget = OptionsWidget(self.muteAtStartup, self.lightMode, self.openFolderAfterDownload, self)
        if self.optionsWidget.isVisible():
            self.optionsWidget.hide()
        else:
            btn_pos = self.titleBar.optionsButton.mapToGlobal(QPoint(0, self.titleBar.optionsButton.height()))
            self.optionsWidget.muteAtStartupCheck.setChecked(self.muteAtStartup)
            self.optionsWidget.lightModeCheck.setChecked(self.lightMode)
            self.optionsWidget.openFolderCheck.setChecked(self.openFolderAfterDownload)
            self.optionsWidget.updateStyleMode()
            self.optionsWidget.move(btn_pos)
            self.optionsWidget.show()

    def setOptions(self, mute_at_startup, light_mode, open_folder_after_download):
        self.muteAtStartup = mute_at_startup
        self.lightMode = light_mode
        self.openFolderAfterDownload = open_folder_after_download
        if self.muteAtStartup and hasattr(self, 'audioPlayer'):
            self.audioPlayer.setMuted(True)
            self.muteButton.setText("Unmute")
        elif hasattr(self, 'audioPlayer'):
            self.audioPlayer.setMuted(False)
            self.audioPlayer.play()
            self.muteButton.setText("Mute")
        self.updateStyles()
        if self.optionsWidget and self.optionsWidget.isVisible():
            self.optionsWidget.muteAtStartupCheck.setChecked(self.muteAtStartup)
            self.optionsWidget.lightModeCheck.setChecked(self.lightMode)
            self.optionsWidget.openFolderCheck.setChecked(self.openFolderAfterDownload)
            self.optionsWidget.updateStyleMode()

    def eventFilter(self, obj, event):
        # If a mouse button is pressed outside the URL field, clear its focus.
        if event.type() == QEvent.MouseButtonPress:
            if self.downloaderUrlInput.hasFocus():
                if not self.downloaderUrlInput.geometry().contains(self.mapFromGlobal(event.globalPos())):
                    self.downloaderUrlInput.clearFocus()
                    self.updateVideoInfo()
            if self.optionsWidget and self.optionsWidget.isVisible():
                pos = event.globalPos()
                if not self.optionsWidget.geometry().contains(pos) and \
                   not self.titleBar.optionsButton.geometry().contains(self.titleBar.optionsButton.mapFromGlobal(pos)):
                    self.optionsWidget.hide()
        return super().eventFilter(obj, event)

    def updateStyles(self):
        if self.lightMode:
            self.setLightStyles()
        else:
            self.setDarkStyles()
        self.backgroundWidget.bg_color = QColor(self.bgColor)
        self.backgroundWidget.update()
        self.titleBar.setStyleSheet("background-color: " + self.titleBarBg + ";")
        self.titleBar.optionsButton.setStyleSheet(self.optionsBtnStyle)
        self.titleBar.titleLabel.setStyleSheet(self.titleLabelStyle)
        self.titleBar.btnMinimize.setStyleSheet(self.minimizeBtnStyle)
        self.titleBar.btnClose.setStyleSheet(self.closeBtnStyle)
        self.downloaderLocInput.setStyleSheet(self.lineEditStyle)
        self.downloaderUrlInput.setStyleSheet(self.lineEditStyle)
        self.formatDropdown.setStyleSheet(self.currentDropdownStyle)
        self.qualityDropdown.setStyleSheet(self.currentDropdownStyle)
        self.fileTypeLabel.setStyleSheet("color: " + ("white" if not self.lightMode else "black") + "; font: 13pt 'Segoe UI';")
        self.qualityLabel.setStyleSheet("color: " + ("white" if not self.lightMode else "black") + "; font: 13pt 'Segoe UI';")
        self.videoInfoLabel.setStyleSheet("color: " + ("#ddd" if not self.lightMode else "#333") + "; font: 10pt 'Segoe UI';")
        self.downloadStatusLabel.setStyleSheet("color: " + ("white" if not self.lightMode else "black") + "; font: bold 14pt 'Segoe UI';")
        if self.lightMode:
            self.pasteButton.setStyleSheet("""
                QPushButton {
                    background-color: #ffffff;
                    color: black;
                    border: 2px solid #ccc;
                    padding: 10px 15px;
                    border-radius: 5px;
                    font: 12pt 'Segoe UI';
                }
                QPushButton:hover { background-color: #ddd; }
                QPushButton:pressed { background-color: #bbb; }
            """)
            self.muteButton.setStyleSheet("""
                QPushButton {
                    background-color: #ffffff;
                    color: black;
                    border: 2px solid #ccc;
                    border-radius: 8px;
                    font: bold 12pt 'Segoe UI';
                }
                QPushButton:hover { background-color: #ddd; }
                QPushButton:pressed { background-color: #bbb; }
            """)
            self.titleBar.optionsButton.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: black;
                    border: none;
                    font: 16pt 'Segoe UI';
                }
                QPushButton:hover { background-color: #ddd; }
                QPushButton:pressed { background-color: #bbb; }
            """)
        else:
            self.pasteButton.setStyleSheet("""
                QPushButton {
                    background-color: #161616;
                    color: white;
                    border: 2px solid #333;
                    padding: 10px 15px;
                    border-radius: 5px;
                    font: 12pt 'Segoe UI';
                }
                QPushButton:hover { background-color: #2a2a2a; }
                QPushButton:pressed { background-color: #444; }
            """)
            self.muteButton.setStyleSheet("""
                QPushButton {
                    background-color: #161616;
                    color: white;
                    border: 2px solid #333;
                    border-radius: 8px;
                    font: bold 12pt 'Segoe UI';
                }
                QPushButton:hover { background-color: #2a2a2a; }
                QPushButton:pressed { background-color: #444; }
            """)
            self.titleBar.optionsButton.setStyleSheet(self.optionsBtnStyle)

    def closeEvent(self, event):
        self.saveSettings()
        event.accept()

    def saveSettings(self):
        self.settings.setValue("muteAtStartup", self.muteAtStartup)
        self.settings.setValue("lightMode", self.lightMode)
        self.settings.setValue("openFolderAfterDownload", self.openFolderAfterDownload)
        self.settings.setValue("downloadDir", self.downloaderLocInput.text())
        self.settings.setValue("audioFormat", self.formatDropdown.currentText())
        self.settings.setValue("quality", self.qualityDropdown.currentText())

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path(os.path.join("UI_Photos", "favicon.ico"))))
    window = MainWindow()
    window.show()
    if sys.platform == "win32":
        GCL_HICON = -14
        GCL_HICONSM = -34
        icon_path = resource_path(os.path.join("UI_Photos", "favicon.ico"))
        hIcon = ctypes.windll.user32.LoadImageW(None, icon_path, 1, 256, 256, 0x00000010)
        if hIcon:
            hwnd = int(window.winId())
            ctypes.windll.user32.SetClassLongPtrW(hwnd, GCL_HICON, hIcon)
            ctypes.windll.user32.SetClassLongPtrW(hwnd, GCL_HICONSM, hIcon)
        else:
            print("Failed to load icon via LoadImageW")
    sys.exit(app.exec_())
