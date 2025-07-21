import sys
import os
import yt_dlp
import time
import ctypes
import librosa
import numpy as np
from scipy import signal

# Version information
__version__ = "1.1.0"
__author__ = "catwarez@proton.me"
__app_name__ = "Waver"

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPoint, QUrl, QTimer, QSize, QEvent, QSettings
from PyQt6.QtGui import QIcon, QPainter, QColor, QPixmap, QFont, QPen
from PyQt6.QtWidgets import (
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
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

# --- Custom QProxyStyle to remove focus rectangle for combo boxes ---
class NoFocusRectStyle(QProxyStyle):
    def drawPrimitive(self, element, option, painter, widget=None):
        if element == QStyle.PrimitiveElement.PE_FrameFocusRect:
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
        opt.state &= ~QStyle.StateFlag.State_HasFocus
        painter = QPainter(self)
        self.style().drawComplexControl(QStyle.ComplexControl.CC_ComboBox, opt, painter, self)
        self.style().drawControl(QStyle.ControlElement.CE_ComboBoxLabel, opt, painter, self)

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
        font = QFont(self.font().family(), self.font().pointSize(), QFont.Weight.Bold)
        painter.setFont(font)
        rect = self.rect()
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)

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
    def __init__(self, light_mode, open_folder_after_download, auto_analyze, main_window):
        super().__init__(None, flags=Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.light_mode = light_mode
        self.main_window = main_window
        self.initUI(open_folder_after_download, auto_analyze)
        self.updateStyleMode()

    def initUI(self, open_folder_after_download, auto_analyze):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        self.lightModeCheck = QCheckBox("Light Mode")
        self.lightModeCheck.setChecked(self.light_mode)
        self.lightModeCheck.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layout.addWidget(self.lightModeCheck)
        self.openFolderCheck = QCheckBox("Open folder after download")
        self.openFolderCheck.setChecked(open_folder_after_download)
        self.openFolderCheck.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layout.addWidget(self.openFolderCheck)
        self.autoAnalyzeCheck = QCheckBox("Auto-Analyze Key and BPM")
        self.autoAnalyzeCheck.setChecked(auto_analyze)
        self.autoAnalyzeCheck.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layout.addWidget(self.autoAnalyzeCheck)
        
        # Connect all checkboxes to update options
        for checkbox in [self.lightModeCheck, self.openFolderCheck, self.autoAnalyzeCheck]:
            checkbox.toggled.connect(self.updateOptions)
    
    def updateOptions(self):
        self.main_window.setOptions(
                self.lightModeCheck.isChecked(),
            self.openFolderCheck.isChecked(),
            auto_analyze=self.autoAnalyzeCheck.isChecked()
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
                    padding: 5px;
                    outline: none;
                    spacing: 8px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    border: 2px solid #ccc;
                    border-radius: 3px;
                    background-color: white;
                }
                QCheckBox::indicator:hover {
                    border: 2px solid #1e90ff;
                }
                QCheckBox::indicator:checked {
                    background-color: #1e90ff;
                    border: 2px solid #1e90ff;
                    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
                }
                QCheckBox::indicator:focus { outline: none; }
                QCheckBox:hover { background-color: #f0f0f0; border-radius: 3px; }
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
                    padding: 5px;
                    outline: none;
                    spacing: 8px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    border: 2px solid #555;
                    border-radius: 3px;
                    background-color: #2a2a2a;
                }
                QCheckBox::indicator:hover {
                    border: 2px solid #1e90ff;
                }
                QCheckBox::indicator:checked {
                    background-color: #1e90ff;
                    border: 2px solid #1e90ff;
                    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
                }
                QCheckBox::indicator:focus { outline: none; }
                QCheckBox:hover { background-color: #333; border-radius: 3px; }
            """)

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
    file_downloaded_signal = pyqtSignal(str)  # Emit the downloaded file path
    error_signal = pyqtSignal(str)
    def __init__(self, url, download_dir, format_type="wav", quality="320k"):
        super().__init__()
        self.url = url
        self.download_dir = download_dir
        self.format_type = format_type.lower()
        self.quality = quality
        self.downloaded_file = None
        self.is_video = format_type.lower() == "mp4"
    def run(self):
        ffmpeg_dir = resource_path("ffmpeg_bin/bin")
        
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
                if self.is_video:
                    self.status_signal.emit("Download completed!")
                else:
                    self.status_signal.emit("Download completed, converting...")
        
        if self.is_video:
            # Video download settings
            # Convert quality like "1080p" to format selection
            if "2160p" in self.quality or "4K" in self.quality:
                format_selector = "best[height<=2160]"
            elif "1440p" in self.quality:
                format_selector = "best[height<=1440]"
            elif "1080p" in self.quality:
                format_selector = "best[height<=1080]"
            elif "720p" in self.quality:
                format_selector = "best[height<=720]"
            elif "480p" in self.quality:
                format_selector = "best[height<=480]"
            else:
                format_selector = "best"
                
            ydl_opts = {
                'format': format_selector,
                'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
                'updatetime': False,
                'ffmpeg_location': ffmpeg_dir,
                'progress_hooks': [progress_hook],
                'quiet': True,
                'no_warnings': True,
            }
        else:
            # Audio download settings
            postprocessors = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': self.format_type,
            }]
            if self.format_type == "mp3":
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
            
            # For audio files, determine the final converted file path
            final_file = None
            if not self.is_video and self.downloaded_file:
                # Get the final audio file path by changing extension
                base_path = os.path.splitext(self.downloaded_file)[0]
                final_file = f"{base_path}.{self.format_type}"
            else:
                # For video files, use the original downloaded file
                final_file = self.downloaded_file
            
            if final_file and os.path.exists(final_file):
                os.utime(final_file, (time.time(), time.time()))
                self.file_downloaded_signal.emit(final_file)
            
            self.status_signal.emit("Download completed!")
            self.finished_signal.emit()
        except Exception as e:
            self.error_signal.emit(str(e))

# --- Video Info Worker for async loading ---
class VideoInfoWorker(QThread):
    info_ready = pyqtSignal(str)
    error_occurred = pyqtSignal()
    
    def __init__(self, url):
        super().__init__()
        self.url = url
        
    def run(self):
        try:
            opts = {'quiet': True, 'skip_download': True}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                title = info.get('title', 'Unknown Title')
                duration = info.get('duration', 0)
                uploader = info.get('uploader', 'Unknown')
                view_count = info.get('view_count', 0)
                
                # Format duration
                if duration > 0:
                    hours = duration // 3600
                    minutes = (duration % 3600) // 60
                    seconds = duration % 60
                    if hours > 0:
                        duration_str = f"{hours}h {minutes}m {seconds}s"
                    else:
                        duration_str = f"{minutes}m {seconds}s"
                else:
                    duration_str = "Unknown"
                
                # Format view count
                if view_count >= 1000000:
                    views_str = f"{view_count / 1000000:.1f}M"
                elif view_count >= 1000:
                    views_str = f"{view_count / 1000:.1f}K"
                else:
                    views_str = str(view_count)
                
                # Better formatting for smaller screens
                info_text = f"""<div style="line-height: 1.5; padding-left: 25px;">
<div style="margin-bottom: 5px;"><b>📺 {title}</b></div>
<div style="font-size: 11pt;">⏱️ {duration_str} • 👤 {uploader} • 👁️ {views_str} views</div>
</div>"""
                self.info_ready.emit(info_text.strip())
        except Exception:
            self.error_occurred.emit()

# --- Audio Analysis Worker ---
class AudioAnalysisWorker(QThread):
    analysis_complete = pyqtSignal(float, str)  # BPM, Key
    analysis_error = pyqtSignal(str)
    analysis_progress = pyqtSignal(str)
    
    def __init__(self, audio_file_path):
        super().__init__()
        self.audio_file_path = audio_file_path
        
    def run(self):
        try:
            self.analysis_progress.emit("Loading audio file...")
            
            # Load audio file (first 60 seconds for analysis)
            y, sr = librosa.load(self.audio_file_path, duration=60.0, sr=22050)
            
            if len(y) == 0:
                self.analysis_error.emit("Could not load audio data")
                return
                
            self.analysis_progress.emit("Analyzing tempo...")
            
            # BPM Detection using multiple methods for accuracy
            # Method 1: Beat tracking with dynamic programming
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=512)
            
            # Method 2: Tempogram-based analysis for verification
            onset_frames = librosa.onset.onset_detect(y=y, sr=sr, hop_length=512)
            tempo_tempogram = librosa.feature.tempo(
                onset_envelope=librosa.onset.onset_strength(y=y, sr=sr),
                sr=sr,
                hop_length=512,
                aggregate=np.median
            )
            
            # Use the most reliable tempo estimate
            if abs(tempo - tempo_tempogram) < 10:  # If methods agree
                final_bpm = float(tempo.item() if hasattr(tempo, 'item') else tempo)
            else:
                # Use beat tracking if tempogram differs significantly
                final_bpm = float(tempo.item() if hasattr(tempo, 'item') else tempo)
            
            # Round to reasonable BPM values
            final_bpm = round(final_bpm, 1)
            
            self.analysis_progress.emit("Analyzing key signature...")
            
            # Key Detection using chromagram analysis
            # Compute chromagram (pitch class profile)
            chromagram = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=512)
            
            # Average chromagram over time to get overall key profile
            chroma_mean = np.mean(chromagram, axis=1)
            
            # Key profiles for major and minor scales (Krumhansl-Schmuckler)
            major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
            minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
            
            # Normalize profiles
            major_profile = major_profile / np.sum(major_profile)
            minor_profile = minor_profile / np.sum(minor_profile)
            
            # Note names
            note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            
            best_correlation = -1
            best_key = "Unknown"
            
            # Test all 24 keys (12 major + 12 minor)
            for shift in range(12):
                # Test major key
                shifted_major = np.roll(major_profile, shift)
                correlation_major = np.corrcoef(chroma_mean, shifted_major)[0, 1]
                
                if correlation_major > best_correlation:
                    best_correlation = correlation_major
                    best_key = f"{note_names[shift]} Major"
                
                # Test minor key
                shifted_minor = np.roll(minor_profile, shift)
                correlation_minor = np.corrcoef(chroma_mean, shifted_minor)[0, 1]
                
                if correlation_minor > best_correlation:
                    best_correlation = correlation_minor
                    best_key = f"{note_names[shift]} Minor"
            
            # Only report key if correlation is strong enough
            if best_correlation < 0.6:
                best_key = "Unknown"
            
            self.analysis_complete.emit(final_bpm, best_key)
            
        except Exception as e:
            self.analysis_error.emit(f"Analysis failed: {str(e)}")

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
        self.titleLabel = QLabel(f"Waver v{__version__} by getbetter", self)
        self.titleLabel.setStyleSheet(parent.titleLabelStyle)
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
        if event.button() == Qt.MouseButton.LeftButton:
            self.start = event.globalPosition().toPoint()
            self.pressing = True
    def mouseMoveEvent(self, event):
        if self.pressing:
            delta = event.globalPosition().toPoint() - self.start
            self.parent.move(self.parent.pos() + delta)
            self.start = event.globalPosition().toPoint()
    def mouseReleaseEvent(self, event):
        self.pressing = False

# --- Main Window ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.lightMode = False
        self.openFolderAfterDownload = True
        self.autoAnalyze = False
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
            "   border: 2px solid #444;"
            "   padding: 10px 16px;"
            "   border-radius: 8px;"
            "   color: white;"
            "   font: 13pt 'Segoe UI';"
            "   outline: none;"
            "   min-width: 80px;"
            "}"
            "QComboBox:hover { border: 2px solid #555; background-color: #1a1a1a; }"
            "QComboBox:focus { border: 2px solid #1e90ff; outline: none; }"
            "QComboBox::drop-down {"
            "   subcontrol-origin: padding;"
            "   subcontrol-position: top right;"
            "   width: 20px;"
            "   border: none;"
            "   background: transparent;"
            "}"
            "QComboBox::down-arrow {"
            "   image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEyIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDFMNiA2TDExIDEiIHN0cm9rZT0iI2FhYSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);"
            "   width: 12px;"
            "   height: 8px;"
            "}"
            "QComboBox QAbstractItemView {"
            "   background: #1a1a1a;"
            "   border: 2px solid #444;"
            "   border-radius: 8px;"
            "   color: white;"
            "   padding: 4px;"
            "   selection-background-color: #1e90ff;"
            "   outline: none;"
            "}"
            "QComboBox QAbstractItemView::item {"
            "   padding: 8px 12px;"
            "   border: none;"
            "   min-height: 20px;"
            "}"
            "QComboBox QAbstractItemView::item:selected {"
            "   background: #1e90ff;"
            "   color: white;"
            "   border-radius: 4px;"
            "}"
            "QComboBox QAbstractItemView::item:hover {"
            "   background: #2a2a2a;"
            "   border-radius: 4px;"
            "}"
        )
        self.lightDropdownStyle = (
            "QComboBox {"
            "   background-color: #ffffff;"
            "   border: 2px solid #ddd;"
            "   padding: 10px 16px;"
            "   border-radius: 8px;"
            "   color: black;"
            "   font: 13pt 'Segoe UI';"
            "   outline: none;"
            "   min-width: 80px;"
            "}"
            "QComboBox:hover { border: 2px solid #bbb; background-color: #f8f8f8; }"
            "QComboBox:focus { border: 2px solid #1e90ff; outline: none; }"
            "QComboBox::drop-down {"
            "   subcontrol-origin: padding;"
            "   subcontrol-position: top right;"
            "   width: 20px;"
            "   border: none;"
            "   background: transparent;"
            "}"
            "QComboBox::down-arrow {"
            "   image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEyIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDFMNiA2TDExIDEiIHN0cm9rZT0iIzY2NiIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);"
            "   width: 12px;"
            "   height: 8px;"
            "}"
            "QComboBox QAbstractItemView {"
            "   background: #ffffff;"
            "   border: 2px solid #ddd;"
            "   border-radius: 8px;"
            "   color: black;"
            "   padding: 4px;"
            "   selection-background-color: #1e90ff;"
            "   outline: none;"
            "}"
            "QComboBox QAbstractItemView::item {"
            "   padding: 8px 12px;"
            "   border: none;"
            "   min-height: 20px;"
            "}"
            "QComboBox QAbstractItemView::item:selected {"
            "   background: #1e90ff;"
            "   color: white;"
            "   border-radius: 4px;"
            "}"
            "QComboBox QAbstractItemView::item:hover {"
            "   background: #f0f0f0;"
            "   border-radius: 4px;"
            "}"
        )
        self.currentDropdownStyle = self.darkDropdownStyle

        self.optionsWidget = None

        self.settings = QSettings("MyCompany", "WaverApp")
        self.loadSettings()

        # Set minimum size but allow dynamic resizing
        self.setMinimumSize(900, 550)
        self.resize(900, 650)  # Start with slightly taller window
        self.initUI()
        self.initAudio()
        self.installEventFilter(self)

    def getDefaultDownloadsFolder(self):
        """Get the user's default Downloads folder path dynamically"""
        try:
            # Try to get the user's Downloads folder using different methods
            if sys.platform == "win32":
                # Windows: Try to get the actual Downloads folder
                import winreg
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                      r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders") as key:
                        downloads_path = winreg.QueryValueEx(key, "{374DE290-123F-4565-9164-39C4925E467B}")[0]
                        if os.path.exists(downloads_path):
                            return downloads_path
                except:
                    pass
                # Fallback for Windows
                downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
            else:
                # macOS/Linux
                downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
            
            # Create the folder if it doesn't exist
            if not os.path.exists(downloads_path):
                os.makedirs(downloads_path, exist_ok=True)
            
            return downloads_path
        except Exception:
            # Ultimate fallback to current directory
            return os.getcwd()

    def loadSettings(self):
        self.isMuted = self.settings.value("audioMuted", False, type=bool)  # Remember last mute state
        self.lightMode = self.settings.value("lightMode", False, type=bool)
        self.openFolderAfterDownload = self.settings.value("openFolderAfterDownload", True, type=bool)
        self.autoAnalyze = self.settings.value("autoAnalyze", False, type=bool)

        
        # Get default downloads folder dynamically
        defaultDownloadsDir = self.getDefaultDownloadsFolder()
        downloadDir = self.settings.value("downloadDir", defaultDownloadsDir)
        
        # Verify the saved directory still exists, if not, fall back to default
        if not os.path.exists(downloadDir):
            downloadDir = defaultDownloadsDir
        
        self.formatSetting = self.settings.value("downloadFormat", "WAV")
        # Set default quality based on format
        if self.formatSetting == "MP4":
            default_quality = "1080p"
        else:
            default_quality = "320k"
        self.qualitySetting = self.settings.value("quality", default_quality)
        self._savedDownloadDir = downloadDir

    def saveSettings(self):
        self.settings.setValue("audioMuted", self.isMuted)
        self.settings.setValue("lightMode", self.lightMode)
        self.settings.setValue("openFolderAfterDownload", self.openFolderAfterDownload)
        self.settings.setValue("autoAnalyze", self.autoAnalyze)

        self.settings.setValue("downloadDir", self.downloaderLocInput.text())
        self.settings.setValue("downloadFormat", self.formatDropdown.currentText())
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
        contentLayout.setContentsMargins(25, 20, 25, 20)
        # --- Top Controls ---
        topControlsLayout = QHBoxLayout()
        fileTypeLayout = QHBoxLayout()
        fileTypeLayout.setSpacing(2)
        self.fileTypeLabel = QLabel("File Type:")
        self.fileTypeLabel.setFixedWidth(80)
        self.fileTypeLabel.setStyleSheet("color: " + ("white" if not self.lightMode else "black") + "; font: 13pt 'Segoe UI';")
        fileTypeLayout.addWidget(self.fileTypeLabel)
        self.formatDropdown = NoFocusComboBox()
        self.formatDropdown.addItems(["WAV", "MP3", "MP4"])
        self.formatDropdown.setCurrentText(self.formatSetting)
        self.formatDropdown.setStyleSheet(self.currentDropdownStyle)
        self.formatDropdown.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.formatDropdown.currentTextChanged.connect(self.onFormatChanged)
        fileTypeLayout.addWidget(self.formatDropdown)
        topControlsLayout.addLayout(fileTypeLayout)
        qualityLayout = QHBoxLayout()
        qualityLayout.setSpacing(2)
        self.qualityLabel = QLabel("Quality:")
        self.qualityLabel.setFixedWidth(80)
        self.qualityLabel.setStyleSheet("color: " + ("white" if not self.lightMode else "black") + "; font: 13pt 'Segoe UI';")
        qualityLayout.addWidget(self.qualityLabel)
        self.qualityDropdown = NoFocusComboBox()
        self.qualityDropdown.setStyleSheet(self.currentDropdownStyle)
        self.qualityDropdown.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        qualityLayout.addWidget(self.qualityDropdown)
        
        # Initialize quality options based on current format
        self.onFormatChanged(self.formatSetting)
        self.qualityDropdown.setCurrentText(self.qualitySetting)
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
        self.downloaderLocInput.setPlaceholderText("Download folder path...")
        self.downloaderLocInput.setToolTip(f"Current: {self._savedDownloadDir}\nDefault: {self.getDefaultDownloadsFolder()}")
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
        
        resetBtn = QPushButton("Reset")
        resetBtn.clicked.connect(self.resetToDefaultFolder)
        resetBtn.setToolTip("Reset to default Downloads folder")
        resetBtn.setStyleSheet("""
            QPushButton {
                background-color: #666;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 8px;
                font: 12pt 'Segoe UI';
            }
            QPushButton:hover { background-color: #777; }
            QPushButton:pressed { background-color: #555; }
        """)
        pathLayout.addWidget(resetBtn)
        
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
        
        # Create a container widget for video info with proper margins
        videoInfoContainer = QWidget()
        videoInfoLayout = QHBoxLayout(videoInfoContainer)
        videoInfoLayout.setContentsMargins(0, 0, 0, 0)
        videoInfoLayout.setSpacing(0)
        
        self.videoInfoLabel = QLabel("")
        self.videoInfoLabel.setStyleSheet("""
            QLabel {
                color: #bbb;
                font: 12pt 'Segoe UI';
                background-color: #1a1a1a;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 15px;
                line-height: 1.5;
                min-height: 60px;
                max-width: 100%;
            }
        """)
        self.videoInfoLabel.setWordWrap(True)
        self.videoInfoLabel.setContentsMargins(20, 8, 20, 8)
        self.videoInfoLabel.setTextFormat(Qt.TextFormat.RichText)
        
        videoInfoLayout.addWidget(self.videoInfoLabel)
        contentLayout.addWidget(videoInfoContainer)
        # --- Download Progress Bar, Status, and Button ---
        self.downloadProgressBar = DynamicProgressBar()
        self.downloadProgressBar.setMinimum(0)
        self.downloadProgressBar.setMaximum(100)
        self.downloadProgressBar.setValue(0)
        self.downloadProgressBar.hide()
        contentLayout.addWidget(self.downloadProgressBar)
        self.downloadStatusLabel = QLabel("")
        self.downloadStatusLabel.setStyleSheet("color: " + ("white" if not self.lightMode else "black") + "; font: bold 14pt 'Segoe UI';")
        self.downloadStatusLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        contentLayout.addWidget(self.downloadStatusLabel)
        self.downloadButton = QPushButton("Download")
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
        
        # --- Audio Analysis Components ---
        self.analyzeButton = QPushButton("🎵 Analyze Key and BPM")
        self.analyzeButton.clicked.connect(self.startAudioAnalysis)
        self.analyzeButton.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #9333ea, stop:1 #7c3aed);
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font: bold 14pt 'Segoe UI';
            }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c3aed, stop:1 #6d28d9); }
            QPushButton:pressed { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6d28d9, stop:1 #5b21b6); }
        """)
        self.analyzeButton.hide()  # Hidden by default

        contentLayout.addWidget(self.analyzeButton)
        
        # Analysis results display
        self.analysisResultsLabel = QLabel("")
        self.analysisResultsLabel.setStyleSheet("""
            QLabel {
                color: #bbb;
                font: 14pt 'Segoe UI';
                background-color: #1a1a1a;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 8px;
                min-height: 50px;
                width: 100%;
                qproperty-wordWrap: true;
            }
        """)
        self.analysisResultsLabel.setWordWrap(True)
        self.analysisResultsLabel.setContentsMargins(0, 5, 0, 5)
        self.analysisResultsLabel.setTextFormat(Qt.TextFormat.RichText)
        self.analysisResultsLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.analysisResultsLabel.hide()  # Hidden by default
        contentLayout.addWidget(self.analysisResultsLabel)
        
        # Analysis progress label
        self.analysisProgressLabel = QLabel("")
        self.analysisProgressLabel.setStyleSheet("color: " + ("white" if not self.lightMode else "black") + "; font: italic 12pt 'Segoe UI';")
        self.analysisProgressLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.analysisProgressLabel.hide()  # Hidden by default
        contentLayout.addWidget(self.analysisProgressLabel)
        
        # Store downloaded file path for analysis
        self.lastDownloadedFile = None
        self.audioAnalysisWorker = None
        
        mainLayout.addWidget(contentWidget)
        self.setCentralWidget(self.backgroundWidget)
        self.updateStyles()

    def startAudioAnalysis(self):
        """Start audio analysis on the last downloaded file"""
        if not self.lastDownloadedFile or not os.path.exists(self.lastDownloadedFile):
            self.analysisProgressLabel.setText("No audio file available for analysis")
            self.analysisProgressLabel.show()
            QTimer.singleShot(3000, self.analysisProgressLabel.hide)
            return
        
        # Show progress and hide button
        self.analyzeButton.hide()
        self.analysisProgressLabel.show()
        self.analysisResultsLabel.hide()
        
        # Adjust window size for progress display
        self.adjustWindowSize()
        
        # Terminate previous worker if running
        if self.audioAnalysisWorker and self.audioAnalysisWorker.isRunning():
            self.audioAnalysisWorker.terminate()
            self.audioAnalysisWorker.wait()
        
        # Start analysis
        self.audioAnalysisWorker = AudioAnalysisWorker(self.lastDownloadedFile)
        self.audioAnalysisWorker.analysis_progress.connect(self.updateAnalysisProgress)
        self.audioAnalysisWorker.analysis_complete.connect(self.onAnalysisComplete)
        self.audioAnalysisWorker.analysis_error.connect(self.onAnalysisError)
        self.audioAnalysisWorker.start()
    
    def updateAnalysisProgress(self, message):
        """Update analysis progress message"""
        self.analysisProgressLabel.setText(message)
    
    def onAnalysisComplete(self, bpm, key):
        """Handle completed audio analysis"""
        self.analysisProgressLabel.hide()
        
        # Format and display results - full width horizontal layout
        results_html = f"""
        <table style="width: 100%; margin: 0; padding: 0; border-collapse: collapse;">
            <tr>
                <td style="text-align: center; padding: 8px; font-size: 14pt; font-weight: bold; color: #fff; width: 20%;">
                    🎵 Analysis Results
                </td>
                <td style="text-align: center; padding: 8px; width: 40%;">
                    <span style="color: #1e90ff; font-size: 14pt;">🥁 BPM:</span> 
                    <span style="font-size: 18pt; font-weight: bold; color: #fff; margin-left: 8px;">{bpm}</span>
                </td>
                <td style="text-align: center; padding: 8px; width: 40%;">
                    <span style="color: #9333ea; font-size: 14pt;">🎹 Key:</span> 
                    <span style="font-size: 18pt; font-weight: bold; color: #fff; margin-left: 8px;">{key}</span>
                </td>
            </tr>
        </table>
        """
        
        self.analysisResultsLabel.setText(results_html)
        self.analysisResultsLabel.show()
        
        # Show analyze button again for re-analysis (only if auto-analyze is disabled)
        if not self.autoAnalyze:
            self.analyzeButton.show()
        
        # Adjust window size to accommodate results
        self.adjustWindowSize()
    
    def onAnalysisError(self, error_message):
        """Handle analysis error"""
        self.analysisProgressLabel.hide()
        self.analysisResultsLabel.setText(f"<div style='text-align: center; color: #ff6b6b; padding: 8px;'>❌ Analysis failed: {error_message}</div>")
        self.analysisResultsLabel.show()
        # Only show button if auto-analyze is disabled
        if not self.autoAnalyze:
            self.analyzeButton.show()
        
        # Adjust window size to show error message
        self.adjustWindowSize()
    
    def onFileDownloaded(self, file_path):
        """Handle when a file is downloaded - decide whether to auto-analyze or show button"""

        
        self.lastDownloadedFile = file_path
        
        # Hide previous analysis results
        self.analysisResultsLabel.hide()
        self.analysisProgressLabel.hide()
        
        # Only analyze audio files (not videos)
        if not file_path.lower().endswith('.mp4'):
            if self.autoAnalyze:
                # Auto-analyze if enabled - don't show button
                self.analyzeButton.hide()  # Make sure button is hidden
                # Don't adjust window size since no button to show
                QTimer.singleShot(1000, self.startAudioAnalysis)  # Small delay to let download complete message show
            else:
                # Show analyze button if auto-analyze is disabled
                self.analyzeButton.show()
                # Adjust window size to show the button properly
                self.adjustWindowSize()
        else:
            # Hide analyze button for video files
            
            self.analyzeButton.hide()

    def adjustWindowSize(self):
        """Dynamically adjust window size based on visible content"""
        # Calculate required height based on visible components
        base_height = 550  # Minimum height
        extra_height = 0
        
        # Add height for analyze button
        if self.analyzeButton.isVisible():
            extra_height += 60
        
        # Add height for analysis results
        if self.analysisResultsLabel.isVisible():
            extra_height += 50
        
        # Add height for analysis progress
        if self.analysisProgressLabel.isVisible():
            extra_height += 40
        
        # Calculate new height with some padding
        new_height = base_height + extra_height + 20
        
        # Get current size and adjust height while keeping width
        current_size = self.size()
        self.resize(current_size.width(), max(new_height, 550))
        
        # Optional: Center the window after resize
        # self.centerWindow()

    def initAudio(self):
        self.audioPlayer = QMediaPlayer()
        self.audioOutput = QAudioOutput()
        self.audioPlayer.setAudioOutput(self.audioOutput)
        
        # Get the audio file path and check if it exists
        wav_path = resource_path(os.path.join("music", "ooiiaa.mp3"))
        
        if os.path.exists(wav_path):
            url = QUrl.fromLocalFile(os.path.abspath(wav_path))
            self.audioPlayer.setSource(url)
            self.audioOutput.setVolume(0.5)
            
            # Connect signals for error handling
            self.audioPlayer.errorOccurred.connect(self.onAudioError)
            
            # Apply the saved mute state
            self.audioOutput.setMuted(self.isMuted)
            if self.isMuted:
                self.muteButton.setText("Unmute")
            else:
                # Start playback if not muted
                self.audioPlayer.play()
                # Try with a delay in case immediate doesn't work
                QTimer.singleShot(500, self.audioPlayer.play)
                self.muteButton.setText("Mute")
        else:
            print(f"Warning: Audio file not found at {wav_path}")
            self.muteButton.setText("Mute")
            # Disable audio functionality if file doesn't exist
            self.audioPlayer = None
            self.audioOutput = None

    def toggleMute(self):
        if self.audioOutput is None:
            return  # No audio available
            
        if self.audioOutput.isMuted():
            self.audioOutput.setMuted(False)
            self.isMuted = False
            # Need to explicitly start playback when unmuting
            self.audioPlayer.play()
            self.muteButton.setText("Mute")
        else:
            self.audioOutput.setMuted(True)
            self.isMuted = True
            self.muteButton.setText("Unmute")
        
        # Save the mute state immediately
        self.settings.setValue("audioMuted", self.isMuted)

    def pasteFromClipboard(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            self.downloaderUrlInput.setText(text)

    def handlePaste(self):
        self.pasteFromClipboard()
        QTimer.singleShot(100, self.updateVideoInfo)

    def browseDownloadFolder(self):
        currentPath = self.downloaderLocInput.text()
        # Start browsing from the current path if it exists, otherwise use default
        startPath = currentPath if os.path.exists(currentPath) else self.getDefaultDownloadsFolder()
        
        folder = QFileDialog.getExistingDirectory(
            self, 
            "Select Download Folder", 
            startPath,
            QFileDialog.Option.ShowDirsOnly
        )
        
        if folder:
            # Update the input field
            self.downloaderLocInput.setText(folder)
            # Update the tooltip to show current vs default
            self.downloaderLocInput.setToolTip(f"Current: {folder}\nDefault: {self.getDefaultDownloadsFolder()}")
            # Immediately save this preference
            self.settings.setValue("downloadDir", folder)

    def updateVideoInfo(self):
        url = self.downloaderUrlInput.text().strip()
        if not url:
            self.videoInfoLabel.setText("")
            return
        
        # Stop any existing worker
        if hasattr(self, 'video_info_worker') and self.video_info_worker.isRunning():
            self.video_info_worker.terminate()
            self.video_info_worker.wait()
        
        # Show loading message
        self.videoInfoLabel.setText("🔄 Loading video information...")
        
        # Start new worker
        self.video_info_worker = VideoInfoWorker(url)
        self.video_info_worker.info_ready.connect(self.videoInfoLabel.setText)
        self.video_info_worker.error_occurred.connect(lambda: self.videoInfoLabel.setText("❌ Could not fetch video information"))
        self.video_info_worker.start()



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
        format_type = self.formatDropdown.currentText().lower()
        quality = self.qualityDropdown.currentText()
        self.worker = DownloadWorker(url, download_dir, format_type=format_type, quality=quality)
        self.worker.progress_signal.connect(lambda value: self.downloadProgressBar.setValue(int(value)))
        self.worker.status_signal.connect(self.downloadStatusLabel.setText)
        self.worker.details_signal.connect(lambda details: self.downloadStatusLabel.setText(f"{self.downloadStatusLabel.text()} | {details}"))
        self.worker.error_signal.connect(lambda err: self.downloadStatusLabel.setText(f"Error: {err}"))
        self.worker.finished_signal.connect(lambda: self.downloadStatusLabel.setText("Download completed!"))
        self.worker.finished_signal.connect(lambda: self.downloadButton.setEnabled(True))
        self.worker.file_downloaded_signal.connect(self.onFileDownloaded)
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
            self.optionsWidget = OptionsWidget(self.lightMode, self.openFolderAfterDownload, self.autoAnalyze, self)
        if self.optionsWidget.isVisible():
            self.optionsWidget.hide()
        else:
            btn_pos = self.titleBar.optionsButton.mapToGlobal(QPoint(0, self.titleBar.optionsButton.height()))
            self.optionsWidget.lightModeCheck.setChecked(self.lightMode)
            self.optionsWidget.openFolderCheck.setChecked(self.openFolderAfterDownload)
            self.optionsWidget.updateStyleMode()
            self.optionsWidget.move(btn_pos)
            self.optionsWidget.show()

    def setOptions(self, light_mode, open_folder_after_download, auto_analyze=None):
        self.lightMode = light_mode
        self.openFolderAfterDownload = open_folder_after_download
        if auto_analyze is not None:
            self.autoAnalyze = auto_analyze

        
        # Save settings immediately when they change
        self.saveSettings()
        
        self.updateStyles()
        if self.optionsWidget and self.optionsWidget.isVisible():
            self.optionsWidget.lightModeCheck.setChecked(self.lightMode)
            self.optionsWidget.openFolderCheck.setChecked(self.openFolderAfterDownload)
            self.optionsWidget.autoAnalyzeCheck.setChecked(self.autoAnalyze)
            self.optionsWidget.updateStyleMode()

    def eventFilter(self, obj, event):
        # If a mouse button is pressed outside the URL field, clear its focus.
        if event.type() == QEvent.Type.MouseButtonPress:
            if self.downloaderUrlInput.hasFocus():
                if not self.downloaderUrlInput.geometry().contains(self.mapFromGlobal(event.globalPosition().toPoint())):
                    self.downloaderUrlInput.clearFocus()
                    self.updateVideoInfo()
            if self.optionsWidget and self.optionsWidget.isVisible():
                pos = event.globalPosition().toPoint()
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

    def onAudioError(self, error):
        """Callback for audio errors"""
        print(f"Audio error: {error}")

    def closeEvent(self, event):
        self.saveSettings()
        event.accept()



    def resetToDefaultFolder(self):
        """Reset download folder to the default Downloads directory"""
        defaultFolder = self.getDefaultDownloadsFolder()
        self.downloaderLocInput.setText(defaultFolder)
        self.settings.setValue("downloadDir", defaultFolder)
        self.downloaderLocInput.setToolTip(f"Current: {defaultFolder}\nDefault: {defaultFolder}")

    def onFormatChanged(self, format_text):
        """Update quality options based on selected format (audio vs video)"""
        self.qualityDropdown.clear()
        
        if format_text == "MP4":
            # Video quality options (resolutions)
            video_qualities = ["480p", "720p", "1080p", "1440p", "2160p (4K)"]
            self.qualityDropdown.addItems(video_qualities)
            # Set default to 1080p for video
            self.qualityDropdown.setCurrentText("1080p")
        else:
            # Audio quality options (bitrates)
            audio_qualities = ["128k", "320k"]
            self.qualityDropdown.addItems(audio_qualities)
            # Set default to 320k for audio
            self.qualityDropdown.setCurrentText("320k")

if __name__ == '__main__':
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
    sys.exit(app.exec())
