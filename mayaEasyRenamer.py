import maya.cmds as cmds
import re

class EasyRenamer:
    def __init__(self):
        self.win_name = "EasyRenamerWindow"
        
        if cmds.window(self.win_name, exists=True):
            cmds.deleteUI(self.win_name)

        # --- PREMIUM COLOR PALETTE ---
        self.bg_window = (0.12, 0.12, 0.13)
        self.bg_frame  = (0.18, 0.18, 0.19)
        self.bg_button = (0.25, 0.25, 0.27)
        self.bg_accent = (0.22, 0.45, 0.65)
        self.bg_warn   = (0.45, 0.25, 0.25)

        # Create UI Window
        self.window = cmds.window(self.win_name, title="Maya Easy Renamer v1.2", widthHeight=(380, 720), sizeable=True, backgroundColor=self.bg_window)
        
        self.scroll_layout = cmds.scrollLayout(childResizable=True, backgroundColor=self.bg_window)
        self.main_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=8, columnOffset=("both", 12), backgroundColor=self.bg_window)
        
        # --- HEADER ---
        cmds.separator(height=10, style='none')
        cmds.text(label="EASY RENAMER", font="boldLabelFont", height=30, backgroundColor=(0.15, 0.15, 0.16))
        cmds.separator(height=10, style='none')

        # --- GLOBAL SETTINGS & RESET ---
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAttach2=("both", "right"), columnAlign2=("left", "center"))
        self.chk_auto_shape = cmds.checkBox(label="Auto-Rename Shapes", value=True)
        cmds.button(label="Reset Tool", command=self.reset_ui, width=80, height=24, backgroundColor=self.bg_warn, annotation="Reset all fields to default")
        cmds.setParent('..')
        
        cmds.separator(height=10, style='in')

        # ==========================================
        # 1. SEARCH AND REPLACE
        # ==========================================
        cmds.frameLayout(label=" Search and Replace", collapsable=True, collapse=False, 
                         marginWidth=12, marginHeight=12, font="boldLabelFont", backgroundColor=self.bg_frame)
        cmds.columnLayout(adjustableColumn=True, rowSpacing=8)
        
        self.fld_search = cmds.textField(placeholderText="Search for (e.g., pCube)")
        self.fld_replace = cmds.textField(placeholderText="Replace with (e.g., Box)")
        
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=1)
        self.chk_case = cmds.checkBox(label="Match Case", value=True)
        cmds.button(label="Replace", command=self.search_replace, width=120, height=30, backgroundColor=self.bg_button)
        cmds.setParent('..')
        
        cmds.setParent('..')
        cmds.setParent('..')

        # ==========================================
        # 2. PREFIX & SUFFIX
        # ==========================================
        cmds.frameLayout(label=" Add Prefix / Suffix", collapsable=True, collapse=False, 
                         marginWidth=12, marginHeight=12, font="boldLabelFont", backgroundColor=self.bg_frame)
        cmds.columnLayout(adjustableColumn=True, rowSpacing=8)
        
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAttach2=("both", "both"), columnAlign2=("left", "center"))
        self.fld_prefix = cmds.textField(placeholderText="Prefix (e.g., L_)")
        cmds.button(label="Add Prefix", command=self.add_prefix, width=120, height=28, backgroundColor=self.bg_button)
        cmds.setParent('..')
        
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAttach2=("both", "both"), columnAlign2=("left", "center"))
        self.fld_suffix = cmds.textField(placeholderText="Suffix (e.g., _low)")
        cmds.button(label="Add Suffix", command=self.add_suffix, width=120, height=28, backgroundColor=self.bg_button)
        cmds.setParent('..')
        
        cmds.setParent('..')
        cmds.setParent('..')

        # ==========================================
        # 3. SEQUENTIAL NUMBERING
        # ==========================================
        cmds.frameLayout(label=" Sequential Numbering", collapsable=True, collapse=False, 
                         marginWidth=12, marginHeight=12, font="boldLabelFont", backgroundColor=self.bg_frame)
        cmds.columnLayout(adjustableColumn=True, rowSpacing=10)
        
        self.fld_base = cmds.textField(placeholderText="Base Name (e.g., Prop_### or Prop)")
        
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=1)
        self.sld_digits = cmds.intSliderGrp(field=True, label="Digits:", minValue=1, maxValue=6, value=2, columnWidth3=(40, 40, 80))
        self.fld_start = cmds.intFieldGrp(numberOfFields=1, label="Start #:", value1=1, columnWidth2=(45, 45))
        cmds.setParent('..')

        # Удалил невалидный флаг font отсюда:
        cmds.button(label="RENAME & NUMBER", command=self.rename_numbered, height=36, backgroundColor=self.bg_accent)
        
        cmds.setParent('..')
        cmds.setParent('..')

        # ==========================================
        # 4. CLEANUP TOOLS
        # ==========================================
        cmds.frameLayout(label=" Cleanup Tools", collapsable=True, collapse=False, 
                         marginWidth=12, marginHeight=12, font="boldLabelFont", backgroundColor=self.bg_frame)
        cmds.columnLayout(adjustableColumn=True, rowSpacing=8)

        cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnAttach2=("both", "both"), columnAlign2=("center", "center"))
        cmds.button(label="Strip End Digits", command=self.strip_digits, height=28, backgroundColor=self.bg_button)
        cmds.button(label="Strip Namespaces", command=self.remove_namespaces, width=140, height=28, backgroundColor=self.bg_button)
        cmds.setParent('..')

        cmds.separator(height=6, style='in')

        cmds.rowLayout(numberOfColumns=3, adjustableColumn=1)
        cmds.text(label="Trim First:", align="right")
        self.fld_trim_first = cmds.intField(value=1, width=45)
        cmds.button(label="Remove", command=self.remove_first_n, width=80, height=24, backgroundColor=self.bg_button)
        cmds.setParent('..')

        cmds.rowLayout(numberOfColumns=3, adjustableColumn=1)
        cmds.text(label="Trim Last:", align="right")
        self.fld_trim_last = cmds.intField(value=1, width=45)
        cmds.button(label="Remove", command=self.remove_last_n, width=80, height=24, backgroundColor=self.bg_button)
        cmds.setParent('..')

        cmds.setParent('..')
        cmds.setParent('..')

        cmds.separator(height=15, style='none')
        cmds.showWindow(self.window)

    # --- UI RESET FUNCTION ---
    def reset_ui(self, *args):
        cmds.textField(self.fld_search, edit=True, text="")
        cmds.textField(self.fld_replace, edit=True, text="")
        cmds.checkBox(self.chk_case, edit=True, value=True)
        
        cmds.textField(self.fld_prefix, edit=True, text="")
        cmds.textField(self.fld_suffix, edit=True, text="")
        
        cmds.textField(self.fld_base, edit=True, text="")
        cmds.intSliderGrp(self.sld_digits, edit=True, value=2)
        cmds.intFieldGrp(self.fld_start, edit=True, value1=1)
        
        cmds.intField(self.fld_trim_first, edit=True, value=1)
        cmds.intField(self.fld_trim_last, edit=True, value=1)
        
        cmds.checkBox(self.chk_auto_shape, edit=True, value=True)
        cmds.warning("Easy Renamer UI Reset to Defaults.")

    # --- HELPER FUNCTIONS ---
    def get_selection(self):
        sel = cmds.ls(selection=True, long=True)
        if not sel:
            cmds.warning("Nothing selected! Please select objects.")
            return []
        return sorted(sel, key=lambda x: x.count('|'), reverse=True)

    def process_rename(self, obj, new_name):
        if cmds.referenceQuery(obj, isNodeReferenced=True):
            cmds.warning("Skipped referenced node: {}".format(obj.split('|')[-1]))
            return obj

        short_name = obj.split('|')[-1]
        if short_name == new_name:
            return obj
            
        renamed_obj = cmds.rename(obj, new_name)
        
        if cmds.checkBox(self.chk_auto_shape, query=True, value=True):
            shapes = cmds.listRelatives(renamed_obj, shapes=True, fullPath=True)
            if shapes:
                shape_short_name = renamed_obj.split('|')[-1] + "Shape"
                if shapes[0].split('|')[-1] != shape_short_name:
                    if not cmds.referenceQuery(shapes[0], isNodeReferenced=True):
                        cmds.rename(shapes[0], shape_short_name)
                    
        return renamed_obj

    # --- CORE FUNCTIONS ---
    def search_replace(self, *args):
        search_str = cmds.textField(self.fld_search, query=True, text=True)
        replace_str = cmds.textField(self.fld_replace, query=True, text=True)
        match_case = cmds.checkBox(self.chk_case, query=True, value=True)
        
        if not search_str: return
        
        for obj in self.get_selection():
            short_name = obj.split('|')[-1]
            new_name = short_name
            if match_case:
                if search_str in short_name:
                    new_name = short_name.replace(search_str, replace_str)
            else:
                if search_str.lower() in short_name.lower():
                    pattern = re.compile(re.escape(search_str), re.IGNORECASE)
                    new_name = pattern.sub(replace_str, short_name)
            self.process_rename(obj, new_name)

    def add_prefix(self, *args):
        prefix = cmds.textField(self.fld_prefix, query=True, text=True)
        if not prefix: return
        for obj in self.get_selection():
            self.process_rename(obj, prefix + obj.split('|')[-1])

    def add_suffix(self, *args):
        suffix = cmds.textField(self.fld_suffix, query=True, text=True)
        if not suffix: return
        for obj in self.get_selection():
            self.process_rename(obj, obj.split('|')[-1] + suffix)

    def rename_numbered(self, *args):
        base_name = cmds.textField(self.fld_base, query=True, text=True)
        if not base_name: return
        
        sel = self.get_selection()
        if not sel: return
            
        digits_val = cmds.intSliderGrp(self.sld_digits, query=True, value=True)
        start_num = cmds.intFieldGrp(self.fld_start, query=True, value1=True)
        hash_pattern = re.compile(r'(#+)')
        
        sel.reverse()
        for i, obj in enumerate(sel):
            current_num = start_num + i
            match = hash_pattern.search(base_name)
            if match:
                hash_str = match.group(1)
                new_name = base_name.replace(hash_str, str(current_num).zfill(len(hash_str)), 1)
            else:
                num_str = str(current_num).zfill(digits_val)
                new_name = f"{base_name}_{num_str}" if not base_name.endswith('_') else f"{base_name}{num_str}"
            self.process_rename(obj, new_name)

    # --- CLEANUP FUNCTIONS ---
    def strip_digits(self, *args):
        for obj in self.get_selection():
            self.process_rename(obj, re.sub(r'\d+$', '', obj.split('|')[-1]))

    def remove_namespaces(self, *args):
        for obj in self.get_selection():
            short_name = obj.split('|')[-1]
            if ':' in short_name:
                self.process_rename(obj, short_name.split(':')[-1])

    def remove_first_n(self, *args):
        n = cmds.intField(self.fld_trim_first, query=True, value=True)
        if n <= 0: return
        for obj in self.get_selection():
            short_name = obj.split('|')[-1]
            if len(short_name) > n:
                self.process_rename(obj, short_name[n:])

    def remove_last_n(self, *args):
        n = cmds.intField(self.fld_trim_last, query=True, value=True)
        if n <= 0: return
        for obj in self.get_selection():
            short_name = obj.split('|')[-1]
            if len(short_name) > n:
                self.process_rename(obj, short_name[:-n])

EasyRenamer()
