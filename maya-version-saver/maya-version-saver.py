import maya.cmds as cmds
import os
import re
import sys
import subprocess

# --- PYSIDE COMPATIBILITY LAYER ---
# Try to import PySide6 first, fall back to PySide2 for older Maya versions
try:
    from PySide6 import QtWidgets, QtCore, QtGui
except ImportError:
    try:
        from PySide2 import QtWidgets, QtCore, QtGui
    except ImportError:
        cmds.error("PySide is not available in this Maya version.")

from maya.app.general.mayaMixin import MayaQWidgetBaseMixin

class VersionSaverQt(MayaQWidgetBaseMixin, QtWidgets.QDialog):
    """Main UI dialog for versioned file saving in Maya"""
    
    def __init__(self, parent=None):
        super(VersionSaverQt, self).__init__(parent)
        self.setWindowTitle("Version Saver v1.1")
        self.resize(400, 320)
        
        # Main frame for custom styling
        self.main_bg = QtWidgets.QFrame()
        self.main_bg.setObjectName("MainBG")
        
        # Custom dark theme stylesheet
        self.setStyleSheet("""
            QFrame#MainBG { background-color: #23262d; }
            QLabel { color: #d7dce6; font-size: 14px; }
            QLabel#TitleLabel { font-size: 16px; font-weight: bold; color: #6f8cff; }
            QLabel#PathLabel { color: #8b95a6; font-size: 12px; }
            
            QGroupBox {
                border: 1px solid #3b414d; 
                border-radius: 4px;
                margin-top: 20px; 
                padding-top: 20px; 
                font-weight: bold;
                font-size: 14px;
                color: #f1f5fb; 
                background-color: #2a2f38; 
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                padding: 0 8px;
            }
            
            QPushButton {
                background-color: #394152; 
                border: 1px solid #505a6d; 
                border-radius: 4px;
                padding: 8px 14px;
                color: #f3f6fb; 
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #455066; }
            QPushButton:pressed { background-color: #53607b; }
            
            QPushButton#ActionBtn { background-color: #3b5998; font-size: 15px; padding: 12px; }
            QPushButton#ActionBtn:hover { background-color: #4c70ba; }
            
            QPushButton#QuickBtn { background-color: #2d6b4a; font-size: 15px; padding: 12px; }
            QPushButton#QuickBtn:hover { background-color: #3a8a5f; }
            
            QSpinBox {
                background-color: #1f232a; 
                border: 1px solid #434b59; 
                border-radius: 3px;
                padding: 6px 10px;
                color: #eef2f7; 
                font-size: 18px;
                font-weight: bold;
            }
            QSpinBox::up-button, QSpinBox::down-button { width: 0px; height: 0px; border: none; }
        """)

        self.get_scene_info()      # Parse current scene filename
        self.create_widgets()      # Build UI elements
        self.create_layouts()      # Arrange UI elements
        self.create_connections()  # Connect signals to slots
        self.update_preview()      # Initialize preview text and color

    def get_scene_info(self):
        """Parse current scene file to extract base name, version, padding, suffix, and extension"""
        filepath = cmds.file(q=True, sceneName=True)
        if not filepath:
            # Default values for unsaved scene
            self.base_name = "untitled"
            self.version = 1
            self.padding = 2
            self.suffix = ""
            self.ext = ".ma"
            self.dir_path = ""
            return

        self.dir_path = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        name, self.ext = os.path.splitext(filename)

        # Parse version pattern: name_vXXsuffix
        match = re.search(r'(.*)_v(\d+)(.*)$', name, re.IGNORECASE)
        if match:
            self.base_name = match.group(1)
            ver_str = match.group(2)
            self.version = int(ver_str)
            self.padding = len(ver_str)      # Preserve existing padding (e.g., v01 vs v001)
            self.suffix = match.group(3)      # Capture any text after version number
        else:
            # No version found in filename
            self.base_name = name
            self.version = 1
            self.padding = 2
            self.suffix = ""

    def create_widgets(self):
        """Create all UI widgets"""
        self.lbl_title = QtWidgets.QLabel("CURRENT SCENE:")
        self.lbl_title.setObjectName("TitleLabel")
        
        # Display full current filename
        display_name = "{}_v{}{}{}".format(
            self.base_name, 
            str(self.version).zfill(self.padding), 
            self.suffix, 
            self.ext
        )
        self.lbl_filename = QtWidgets.QLabel(display_name)
        self.lbl_filename.setStyleSheet("font-size: 16px;")
        
        # Show directory path or unsaved message
        self.lbl_path = QtWidgets.QLabel(self.dir_path if self.dir_path else "Not saved yet!")
        self.lbl_path.setObjectName("PathLabel")
        self.lbl_path.setWordWrap(True)
        
        self.btn_open_folder = QtWidgets.QPushButton("Open Folder")
        self.btn_open_folder.setEnabled(bool(self.dir_path))  # Disable if scene never saved
        
        self.grp_version = QtWidgets.QGroupBox("Version Control")
        self.btn_minus = QtWidgets.QPushButton("-")
        self.btn_minus.setFixedWidth(40)
        self.btn_plus = QtWidgets.QPushButton("+")
        self.btn_plus.setFixedWidth(40)
        
        self.spn_version = QtWidgets.QSpinBox()
        self.spn_version.setRange(1, 9999)
        self.spn_version.setValue(self.version)
        self.spn_version.setAlignment(QtCore.Qt.AlignCenter)
        self.spn_version.setFixedWidth(80)
        
        # Preview label shows what will be saved
        self.lbl_preview = QtWidgets.QLabel("")
        self.lbl_preview.setAlignment(QtCore.Qt.AlignCenter)
        
        self.btn_save = QtWidgets.QPushButton("SAVE VERSION")
        self.btn_save.setObjectName("ActionBtn")
        
        self.btn_quick = QtWidgets.QPushButton("+1 & QUICK SAVE")
        self.btn_quick.setObjectName("QuickBtn")

    def create_layouts(self):
        """Arrange widgets in layouts"""
        master_layout = QtWidgets.QVBoxLayout(self)
        master_layout.setContentsMargins(0, 0, 0, 0)
        master_layout.addWidget(self.main_bg)

        main_layout = QtWidgets.QVBoxLayout(self.main_bg)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(25, 25, 25, 25)

        # Header section with current file info
        main_layout.addWidget(self.lbl_title)
        main_layout.addWidget(self.lbl_filename)
        
        # Path and folder button row
        path_layout = QtWidgets.QHBoxLayout()
        path_layout.addWidget(self.lbl_path, stretch=1)
        path_layout.addWidget(self.btn_open_folder)
        main_layout.addLayout(path_layout)
        
        # Version control group box
        v_layout = QtWidgets.QVBoxLayout(self.grp_version)
        v_layout.setContentsMargins(15, 25, 15, 15)
        
        # Spinbox with increment/decrement buttons
        spin_layout = QtWidgets.QHBoxLayout()
        spin_layout.addStretch()
        spin_layout.addWidget(self.btn_minus)
        spin_layout.addWidget(QtWidgets.QLabel("v"))
        spin_layout.addWidget(self.spn_version)
        spin_layout.addWidget(self.btn_plus)
        spin_layout.addStretch()
        
        v_layout.addLayout(spin_layout)
        v_layout.addWidget(self.lbl_preview)
        
        main_layout.addWidget(self.grp_version)
        main_layout.addStretch()
        
        # Action buttons row
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.btn_quick)
        btn_layout.addWidget(self.btn_save)
        main_layout.addLayout(btn_layout)

    def create_connections(self):
        """Connect UI signals to their handlers"""
        self.btn_minus.clicked.connect(lambda: self.spn_version.setValue(self.spn_version.value() - 1))
        self.btn_plus.clicked.connect(lambda: self.spn_version.setValue(self.spn_version.value() + 1))
        self.spn_version.valueChanged.connect(self.update_preview)  # Update preview when version changes
        self.btn_open_folder.clicked.connect(self.open_directory)
        
        self.btn_save.clicked.connect(lambda: self.execute_save(increment=False))
        self.btn_quick.clicked.connect(lambda: self.execute_save(increment=True))

    def update_preview(self):
        """Update preview label showing what filename will be saved"""
        val = self.spn_version.value()
        new_name = "{}_v{}{}{}".format(
            self.base_name, 
            str(val).zfill(self.padding), 
            self.suffix, 
            self.ext
        )
        
        # Visual feedback based on whether version is new or will overwrite existing
        if val == self.version:
            self.lbl_preview.setText("Overwrite Current: " + new_name)
            self.lbl_preview.setStyleSheet("color: #d9534f; font-style: italic; margin-top: 5px;")  # Red warning
        else:
            self.lbl_preview.setText("Save as: " + new_name)
            self.lbl_preview.setStyleSheet("color: #5cb85c; font-weight: bold; margin-top: 5px;")  # Green success

    def open_directory(self):
        """Open the scene's folder in system file explorer"""
        if not self.dir_path or not os.path.exists(self.dir_path):
            cmds.warning("Directory does not exist yet.")
            return
            
        # Cross-platform folder opening
        if sys.platform == 'win32':
            os.startfile(self.dir_path)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', self.dir_path])
        else:
            subprocess.Popen(['xdg-open', self.dir_path])

    def execute_save(self, increment=False):
        """Save the scene with the specified version number"""
        if not self.dir_path:
            cmds.warning("Scene has no path! Please save the file manually once.")
            return

        # Increment version before saving if Quick Save was clicked
        if increment:
            self.spn_version.setValue(self.spn_version.value() + 1)
            
        ver_val = self.spn_version.value()
        new_filename = "{}_v{}{}{}".format(
            self.base_name, 
            str(ver_val).zfill(self.padding), 
            self.suffix, 
            self.ext
        )
        
        full_path = os.path.join(self.dir_path, new_filename).replace('\\', '/')
        
        # Check for existing file and ask for confirmation before overwriting
        if os.path.exists(full_path):
            result = cmds.confirmDialog(
                title='Overwrite Scene?',
                message='File already exists:\n\n{}\n\nDo you want to overwrite it?'.format(new_filename),
                button=['Yes', 'No'],
                defaultButton='No',
                cancelButton='No',
                dismissString='No'
            )
            if result == 'No':
                # Revert version increment if user cancelled
                if increment:
                    self.spn_version.setValue(self.spn_version.value() - 1)
                return

        # Determine Maya file type based on extension
        f_type = "mayaAscii" if self.ext.lower() == ".ma" else "mayaBinary"
        
        try:
            cmds.file(rename=full_path)
            cmds.file(save=True, type=f_type)
            # Display in-view message for visual confirmation
            cmds.inViewMessage(amg="Saved: {}".format(new_filename), pos='midCenter', fade=True)
            self.close()
        except Exception as e:
            cmds.error("Failed to save: {}".format(str(e)))

# Launch the UI
# Clean up any existing instance before creating new one
try:
    version_saver_ui.close()
    version_saver_ui.deleteLater()
except:
    pass
version_saver_ui = VersionSaverQt()
version_saver_ui.show()