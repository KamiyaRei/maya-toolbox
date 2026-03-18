import maya.cmds as cmds
import re

# --- PYSIDE COMPATIBILITY LAYER ---
try:
    from PySide6 import QtWidgets, QtCore, QtGui
except ImportError:
    try:
        from PySide2 import QtWidgets, QtCore, QtGui
    except ImportError:
        cmds.error("PySide is not available in this Maya version.")

from maya.app.general.mayaMixin import MayaQWidgetBaseMixin

class EasyRenamerQt(MayaQWidgetBaseMixin, QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(EasyRenamerQt, self).__init__(parent)
        self.setWindowTitle("Maya Easy Renamer v2.0")
        self.resize(600, 680)
        
        self.main_bg = QtWidgets.QFrame()
        self.main_bg.setObjectName("MainBG")
        
        self.setStyleSheet("""
            QFrame#MainBG { background-color: #23262d; }
            QLabel { color: #d7dce6; font-size: 14px; }
            QCheckBox, QRadioButton { color: #d7dce6; spacing: 10px; font-size: 14px; }
            
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
                min-height: 24px; 
            }
            QPushButton:hover { background-color: #455066; }
            QPushButton:pressed { background-color: #53607b; }
            
            QPushButton#MainActionBtn {
                font-weight: bold;
                font-size: 15px;
                padding: 12px;
                background-color: #394152;
            }
            
            QLineEdit, QSpinBox {
                background-color: #1f232a; 
                border: 1px solid #434b59; 
                border-radius: 3px;
                padding: 6px 10px;
                color: #eef2f7; 
                font-size: 14px;
            }
            QLineEdit:focus, QSpinBox:focus { border: 1px solid #6f8cff; }
            QSpinBox::up-button, QSpinBox::down-button { width: 0px; height: 0px; border: none; }
        """)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        # Global settings
        self.chk_auto_shape = QtWidgets.QCheckBox("Auto-Rename Shapes")
        self.chk_auto_shape.setChecked(True)
        self.btn_reset = QtWidgets.QPushButton("Reset Tool")
        self.btn_reset.setFixedWidth(120)

        # 1. Search & Replace
        self.grp_search = QtWidgets.QGroupBox("Search and Replace")
        self.fld_search = QtWidgets.QLineEdit()
        self.fld_search.setPlaceholderText("Search for (e.g., pCube)")
        self.fld_replace = QtWidgets.QLineEdit()
        self.fld_replace.setPlaceholderText("Replace with (e.g., Box)")
        self.chk_case = QtWidgets.QCheckBox("Match Case")
        self.chk_case.setChecked(True)
        self.btn_replace = QtWidgets.QPushButton("Replace")
        self.btn_replace.setFixedWidth(160)

        # 2. Prefix & Suffix
        self.grp_affix = QtWidgets.QGroupBox("Add Prefix / Suffix")
        self.fld_prefix = QtWidgets.QLineEdit()
        self.fld_prefix.setPlaceholderText("Prefix (e.g., L_)")
        self.btn_prefix = QtWidgets.QPushButton("Add Prefix")
        self.btn_prefix.setFixedWidth(160)
        
        self.fld_suffix = QtWidgets.QLineEdit()
        self.fld_suffix.setPlaceholderText("Suffix (e.g., _low)")
        self.btn_suffix = QtWidgets.QPushButton("Add Suffix")
        self.btn_suffix.setFixedWidth(160)

        # 3. Sequential Numbering
        self.grp_seq = QtWidgets.QGroupBox("Sequential Numbering")
        self.fld_base = QtWidgets.QLineEdit()
        self.fld_base.setPlaceholderText("Base Name (e.g., Prop_### or Prop)")
        
        self.lbl_digits = QtWidgets.QLabel("Digits:")
        self.grp_rad_digits = QtWidgets.QButtonGroup(self)
        self.rad_dig_2 = QtWidgets.QRadioButton("2")
        self.rad_dig_3 = QtWidgets.QRadioButton("3")
        self.rad_dig_4 = QtWidgets.QRadioButton("4")
        self.rad_dig_2.setChecked(True)
        self.grp_rad_digits.addButton(self.rad_dig_2)
        self.grp_rad_digits.addButton(self.rad_dig_3)
        self.grp_rad_digits.addButton(self.rad_dig_4)
        
        # Поле с Placeholder "0"
        self.fld_custom_digits = QtWidgets.QLineEdit()
        self.fld_custom_digits.setPlaceholderText("0") 
        self.fld_custom_digits.setFixedWidth(70)
        self.fld_custom_digits.setAlignment(QtCore.Qt.AlignCenter)
        
        self.lbl_start = QtWidgets.QLabel("Start #:")
        self.spn_start = QtWidgets.QSpinBox()
        self.spn_start.setRange(0, 9999)
        self.spn_start.setValue(1)
        self.spn_start.setFixedWidth(80)
        self.spn_start.setAlignment(QtCore.Qt.AlignCenter)
        
        self.btn_seq = QtWidgets.QPushButton("SET NAME")
        self.btn_seq.setObjectName("MainActionBtn")

        # 4. Cleanup Tools
        self.grp_clean = QtWidgets.QGroupBox("Cleanup Tools")
        self.btn_strip_dig = QtWidgets.QPushButton("Strip End Digits")
        self.btn_strip_ns = QtWidgets.QPushButton("Strip Namespaces")
        
        # Compact Cut Row
        self.lbl_cut_f = QtWidgets.QLabel("Cut First:")
        self.spn_cut_f = QtWidgets.QSpinBox()
        self.spn_cut_f.setRange(0, 100)
        self.spn_cut_f.setFixedWidth(50)
        self.btn_cut_f = QtWidgets.QPushButton("Apply")
        
        self.lbl_cut_l = QtWidgets.QLabel("Cut Last:")
        self.spn_cut_l = QtWidgets.QSpinBox()
        self.spn_cut_l.setRange(0, 100)
        self.spn_cut_l.setFixedWidth(50)
        self.btn_cut_l = QtWidgets.QPushButton("Apply")

    def create_layouts(self):
        master_layout = QtWidgets.QVBoxLayout(self)
        master_layout.setContentsMargins(0, 0, 0, 0)
        master_layout.addWidget(self.main_bg)

        main_layout = QtWidgets.QVBoxLayout(self.main_bg)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(25, 25, 25, 25)

        lyt_global = QtWidgets.QHBoxLayout()
        lyt_global.addWidget(self.chk_auto_shape)
        lyt_global.addStretch()
        lyt_global.addWidget(self.btn_reset)
        main_layout.addLayout(lyt_global)

        # Search
        lyt_search = QtWidgets.QVBoxLayout(self.grp_search)
        lyt_search.setContentsMargins(15, 22, 15, 15)
        lyt_search.setSpacing(12)
        lyt_search.addWidget(self.fld_search)
        lyt_search.addWidget(self.fld_replace)
        s_row = QtWidgets.QHBoxLayout()
        s_row.addWidget(self.chk_case)
        s_row.addStretch()
        s_row.addWidget(self.btn_replace)
        lyt_search.addLayout(s_row)
        main_layout.addWidget(self.grp_search)

        # Affix
        lyt_affix = QtWidgets.QVBoxLayout(self.grp_affix)
        lyt_affix.setContentsMargins(15, 22, 15, 15)
        lyt_affix.setSpacing(12)
        r1 = QtWidgets.QHBoxLayout(); r1.addWidget(self.fld_prefix); r1.addWidget(self.btn_prefix); lyt_affix.addLayout(r1)
        r2 = QtWidgets.QHBoxLayout(); r2.addWidget(self.fld_suffix); r2.addWidget(self.btn_suffix); lyt_affix.addLayout(r2)
        main_layout.addWidget(self.grp_affix)

        # Sequential Numbering
        lyt_seq = QtWidgets.QVBoxLayout(self.grp_seq)
        lyt_seq.setContentsMargins(15, 22, 15, 15)
        lyt_seq.addWidget(self.fld_base)
        lyt_s2 = QtWidgets.QHBoxLayout()
        lyt_s2.addWidget(self.lbl_digits); lyt_s2.addWidget(self.rad_dig_2); lyt_s2.addWidget(self.rad_dig_3); lyt_s2.addWidget(self.rad_dig_4); lyt_s2.addWidget(self.fld_custom_digits)
        lyt_s2.addStretch()
        lyt_s2.addWidget(self.lbl_start); lyt_s2.addWidget(self.spn_start)
        lyt_seq.addLayout(lyt_s2)
        lyt_seq.addWidget(self.btn_seq)
        main_layout.addWidget(self.grp_seq)

        # Cleanup Tools
        lyt_clean = QtWidgets.QVBoxLayout(self.grp_clean)
        lyt_clean.setContentsMargins(15, 22, 15, 15)
        lyt_clean.setSpacing(12)
        
        c_row1 = QtWidgets.QHBoxLayout()
        c_row1.addWidget(self.btn_strip_dig)
        c_row1.addWidget(self.btn_strip_ns)
        lyt_clean.addLayout(c_row1)
        
        c_row2 = QtWidgets.QHBoxLayout()
        c_row2.addWidget(self.lbl_cut_f); c_row2.addWidget(self.spn_cut_f); c_row2.addWidget(self.btn_cut_f)
        c_row2.addSpacing(20)
        c_row2.addWidget(self.lbl_cut_l); c_row2.addWidget(self.spn_cut_l); c_row2.addWidget(self.btn_cut_l)
        lyt_clean.addLayout(c_row2)
        
        main_layout.addWidget(self.grp_clean)
        main_layout.addStretch()

    def create_connections(self):
        self.fld_custom_digits.textChanged.connect(self.manage_digit_visuals)
        self.btn_reset.clicked.connect(self.reset_ui)
        self.btn_replace.clicked.connect(self.search_replace)
        self.btn_prefix.clicked.connect(self.add_prefix)
        self.btn_suffix.clicked.connect(self.add_suffix)
        self.btn_seq.clicked.connect(self.rename_numbered)
        self.btn_strip_dig.clicked.connect(self.strip_digits)
        self.btn_strip_ns.clicked.connect(self.remove_namespaces)
        self.btn_cut_f.clicked.connect(self.remove_first_n)
        self.btn_cut_l.clicked.connect(self.remove_last_n)

    def manage_digit_visuals(self):
        # Если в поле Custom что-то вписано, блокируем радио-кнопки
        text = self.fld_custom_digits.text().strip()
        active = not bool(text)
        self.rad_dig_2.setEnabled(active)
        self.rad_dig_3.setEnabled(active)
        self.rad_dig_4.setEnabled(active)

    def reset_ui(self):
        # Очистка полей
        for f in [self.fld_search, self.fld_replace, self.fld_prefix, self.fld_suffix, self.fld_base, self.fld_custom_digits]: 
            f.clear()
        self.rad_dig_2.setChecked(True)
        self.spn_start.setValue(1)
        self.spn_cut_f.setValue(0)
        self.spn_cut_l.setValue(0)
        cmds.warning("Easy Renamer UI Reset.")

    def get_selection(self):
        sel = cmds.ls(selection=True, long=True)
        return sorted(sel, key=lambda x: x.count('|'), reverse=True) if sel else []

    def process_rename(self, obj, new_name):
        if cmds.referenceQuery(obj, isNodeReferenced=True): return obj
        short = obj.split('|')[-1]
        if short == new_name: return obj
        renamed = cmds.rename(obj, new_name)
        if self.chk_auto_shape.isChecked():
            shapes = cmds.listRelatives(renamed, shapes=True, fullPath=True)
            if shapes:
                s_name = renamed.split('|')[-1] + "Shape"
                if shapes[0].split('|')[-1] != s_name and not cmds.referenceQuery(shapes[0], isNodeReferenced=True):
                    cmds.rename(shapes[0], s_name)
        return renamed

    def search_replace(self):
        s, r = self.fld_search.text(), self.fld_replace.text()
        if not s: return
        for o in self.get_selection():
            n = o.split('|')[-1]
            new = n.replace(s, r) if self.chk_case.isChecked() else re.compile(re.escape(s), re.IGNORECASE).sub(r, n)
            self.process_rename(o, new)

    def add_prefix(self):
        p = self.fld_prefix.text()
        if p: [self.process_rename(o, p + o.split('|')[-1]) for o in self.get_selection()]

    def add_suffix(self):
        s = self.fld_suffix.text()
        if s: [self.process_rename(o, o.split('|')[-1] + s) for o in self.get_selection()]

    def rename_numbered(self):
        base = self.fld_base.text()
        if not base: return
        sel = self.get_selection()
        if not sel: return
        
        c_val = self.fld_custom_digits.text().strip()
        # Если в Custom введено число, используем его, иначе — радио-кнопку
        if c_val.isdigit():
            dv = int(c_val)
        else:
            dv = 2 if self.rad_dig_2.isChecked() else (3 if self.rad_dig_3.isChecked() else 4)
            
        st = self.spn_start.value()
        sel.reverse()
        for i, o in enumerate(sel):
            num = str(st + i).zfill(dv)
            if '#' in base:
                h = re.search(r'(#+)', base).group(1)
                new = base.replace(h, str(st + i).zfill(len(h)), 1)
            else:
                new = f"{base}_{num}" if not base.endswith('_') else f"{base}{num}"
            self.process_rename(o, new)

    def strip_digits(self):
        [self.process_rename(o, re.sub(r'\d+$', '', o.split('|')[-1])) for o in self.get_selection()]

    def remove_namespaces(self):
        [self.process_rename(o, o.split('|')[-1].split(':')[-1]) for o in self.get_selection() if ':' in o]

    def remove_first_n(self):
        n = self.spn_cut_f.value()
        if n > 0:
            for o in self.get_selection():
                name = o.split('|')[-1]
                if len(name) > n: self.process_rename(o, name[n:])

    def remove_last_n(self):
        n = self.spn_cut_l.value()
        if n > 0:
            for o in self.get_selection():
                name = o.split('|')[-1]
                if len(name) > n: self.process_rename(o, name[:-n])

try:
    easy_renamer_ui.close(); easy_renamer_ui.deleteLater()
except: pass
easy_renamer_ui = EasyRenamerQt(); easy_renamer_ui.show()
