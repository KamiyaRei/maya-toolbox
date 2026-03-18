import maya.cmds as cmds
import re

class EasyRenamer:
    def __init__(self):
        self.win_name = "EasyRenamerWindow"
        
        # Close window if it already exists
        if cmds.window(self.win_name, exists=True):
            cmds.deleteUI(self.win_name)

        # --- COLOR PALETTE ---
        # Dark blue-grey theme
        bg_main = (0.15, 0.16, 0.19)    # Window background
        bg_frame = (0.20, 0.21, 0.24)   # Frame/Panel background
        bg_button = (0.25, 0.28, 0.33)  # Button background

        # Create UI Window
        self.window = cmds.window(self.win_name, title="Maya Easy Renamer", widthHeight=(360, 480), sizeable=True)
        
        # Main Layout with custom background
        self.main_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=10, columnOffset=("both", 10), backgroundColor=bg_main)
        cmds.separator(height=8, style='none')

        # ==========================================
        # 1. SEARCH AND REPLACE FRAME
        # ==========================================
        cmds.frameLayout(label="Search and Replace", collapsable=True, collapse=False, 
                         marginWidth=12, marginHeight=12, font="boldLabelFont", backgroundColor=bg_frame)
        cmds.columnLayout(adjustableColumn=True, rowSpacing=10)
        
        self.fld_search = cmds.textField(placeholderText="Search for (e.g., pCube)")
        self.fld_replace = cmds.textField(placeholderText="Replace with (e.g., Box)")
        
        self.chk_case = cmds.checkBox(label="Match Case", value=True)
        cmds.button(label="Search and Replace", command=self.search_replace, height=32, backgroundColor=bg_button)
        
        cmds.setParent('..') # End Column
        cmds.setParent('..') # End Frame

        # ==========================================
        # 2. PREFIX & SUFFIX FRAME
        # ==========================================
        cmds.frameLayout(label="Add Prefix / Suffix", collapsable=True, collapse=False, 
                         marginWidth=12, marginHeight=12, font="boldLabelFont", backgroundColor=bg_frame)
        cmds.columnLayout(adjustableColumn=True, rowSpacing=10)
        
        # Prefix Row
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAttach2=("both", "both"), columnAlign2=("left", "center"))
        self.fld_prefix = cmds.textField(placeholderText="Prefix (e.g., L_)")
        cmds.button(label="Apply Prefix", command=self.add_prefix, width=110, height=28, backgroundColor=bg_button)
        cmds.setParent('..') # End Row
        
        # Suffix Row
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAttach2=("both", "both"), columnAlign2=("left", "center"))
        self.fld_suffix = cmds.textField(placeholderText="Suffix (e.g., _low)")
        cmds.button(label="Apply Suffix", command=self.add_suffix, width=110, height=28, backgroundColor=bg_button)
        cmds.setParent('..') # End Row
        
        cmds.setParent('..') # End Column
        cmds.setParent('..') # End Frame

        # ==========================================
        # 3. SEQUENTIAL NUMBERING FRAME
        # ==========================================
        cmds.frameLayout(label="Sequential Numbering", collapsable=True, collapse=False, 
                         marginWidth=12, marginHeight=12, font="boldLabelFont", backgroundColor=bg_frame)
        cmds.columnLayout(adjustableColumn=True, rowSpacing=10)
        
        # Base Name Row
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAttach2=("both", "both"), columnAlign2=("left", "center"))
        self.fld_base = cmds.textField(placeholderText="Base Name (e.g., Prop_### or Prop)")
        cmds.button(label="Rename & Number", command=self.rename_numbered, width=130, height=28, backgroundColor=bg_button)
        cmds.setParent('..') # End Row
        
        # Digits Slider Row
        cmds.rowLayout(numberOfColumns=1, adjustableColumn=1)
        self.sld_digits = cmds.intSliderGrp(field=True, label="Digits:", minValue=1, maxValue=6, value=2, 
                                             columnWidth3=(50, 40, 100), 
                                             annotation="Number of digits if '#' is not used in Base Name")
        cmds.setParent('..') # End Row
        
        cmds.setParent('..') # End Column
        cmds.setParent('..') # End Frame

        cmds.separator(height=10, style='none')
        cmds.showWindow(self.window)

    # --- CORE FUNCTIONS ---
    def get_selection(self):
        sel = cmds.ls(selection=True, long=True)
        if not sel:
            cmds.warning("Nothing selected! Please select objects to rename.")
            return []
        # Sort by hierarchy depth to rename children before parents
        return sorted(sel, key=lambda x: x.count('|'), reverse=True)

    def search_replace(self, *args):
        search_str = cmds.textField(self.fld_search, query=True, text=True)
        replace_str = cmds.textField(self.fld_replace, query=True, text=True)
        match_case = cmds.checkBox(self.chk_case, query=True, value=True)
        
        if not search_str: return
        
        for obj in self.get_selection():
            short_name = obj.split('|')[-1]
            if match_case:
                if search_str in short_name:
                    new_name = short_name.replace(search_str, replace_str)
                    cmds.rename(obj, new_name)
            else:
                if search_str.lower() in short_name.lower():
                    pattern = re.compile(re.escape(search_str), re.IGNORECASE)
                    new_name = pattern.sub(replace_str, short_name)
                    cmds.rename(obj, new_name)

    def add_prefix(self, *args):
        prefix = cmds.textField(self.fld_prefix, query=True, text=True)
        if not prefix: return
        for obj in self.get_selection():
            short_name = obj.split('|')[-1]
            cmds.rename(obj, prefix + short_name)

    def add_suffix(self, *args):
        suffix = cmds.textField(self.fld_suffix, query=True, text=True)
        if not suffix: return
        for obj in self.get_selection():
            short_name = obj.split('|')[-1]
            cmds.rename(obj, short_name + suffix)

    def rename_numbered(self, *args):
        base_name = cmds.textField(self.fld_base, query=True, text=True)
        if not base_name: return
        
        sel = cmds.ls(selection=True)
        if not sel:
            cmds.warning("Nothing selected!")
            return
            
        digits_val = cmds.intSliderGrp(self.sld_digits, query=True, value=True)
        hash_pattern = re.compile(r'(#+)')
        
        for i, obj in enumerate(sel):
            current_num = i + 1
            match = hash_pattern.search(base_name)
            
            if match:
                # Use length of '#' sequence
                hash_str = match.group(1)
                pad_length = len(hash_str)
                num_str = str(current_num).zfill(pad_length)
                new_name = base_name.replace(hash_str, num_str, 1)
            else:
                # Use digits slider and check for underscore
                num_str = str(current_num).zfill(digits_val)
                if not base_name.endswith('_'):
                    new_name = "{}_{}".format(base_name, num_str)
                else:
                    new_name = "{}{}".format(base_name, num_str)
                
            cmds.rename(obj, new_name)

EasyRenamer()
