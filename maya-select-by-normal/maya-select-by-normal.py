import maya.cmds as cmds
import maya.api.OpenMaya as om
import math

class SelectByNormalAPI:
    def __init__(self):
        self.win_name = "SelectByNormalUI"
        
        # Close window if it already exists
        if cmds.window(self.win_name, exists=True):
            cmds.deleteUI(self.win_name)

        # Create UI
        self.window = cmds.window(self.win_name, title="Maya Select by Normal", widthHeight=(280, 110), sizeable=False)
        cmds.columnLayout(adjustableColumn=True, rowSpacing=8, columnOffset=("both", 10))
        cmds.separator(height=5, style='none')

        cmds.text(label="Angle Tolerance (Degrees):", align="left", font="boldLabelFont")
        # Default tolerance is 0.1 for hard flat surfaces.
        self.tol_slider = cmds.floatSliderGrp(field=True, minValue=0.001, maxValue=90.0, fieldMinValue=0.001, fieldMaxValue=180.0, value=0.1)

        cmds.button(label="Select Matching Faces", command=self.execute_selection, height=35, backgroundColor=(0.2, 0.4, 0.5))

        cmds.separator(height=5, style='none')
        cmds.showWindow(self.window)

    def execute_selection(self, *args):
        # Get currently selected faces
        sel = cmds.ls(selection=True, flatten=True)
        faces = cmds.filterExpand(sel, selectionMask=34)
        
        if not faces:
            cmds.warning("Please select at least one polygon face.")
            return

        ref_face = faces[0]
        mesh_name = ref_face.split('.')[0]
        
        try:
            # Extract the face index (e.g., from "pCube1.f[5]" get 5)
            ref_index = int(ref_face.split('[')[-1].split(']')[0])
        except:
            cmds.warning("Could not parse face index.")
            return

        tolerance = cmds.floatSliderGrp(self.tol_slider, query=True, value=True)
        # Add a tiny epsilon to prevent math domain errors on absolute zero
        tolerance = max(tolerance, 0.001) 
        tol_radians = math.radians(tolerance)
        threshold_dot = math.cos(tol_radians)

        # Get the DAG path of the mesh via OpenMaya
        sel_list = om.MSelectionList()
        try:
            sel_list.add(mesh_name)
            dag_path = sel_list.getDagPath(0)
        except:
            cmds.warning("Could not find mesh: " + mesh_name)
            return

        # Iterate through all polygons on the mesh
        poly_iter = om.MItMeshPolygon(dag_path)
        
        # 1. Get the normal vector of the reference face
        poly_iter.setIndex(ref_index)
        ref_normal = poly_iter.getNormal(om.MSpace.kObject)
        ref_normal.normalize()

        faces_to_select = []
        
        # 2. Reset iterator and compare all faces against the reference
        poly_iter.reset()
        while not poly_iter.isDone():
            n = poly_iter.getNormal(om.MSpace.kObject)
            n.normalize()
            
            # Dot product (MVector overloaded operator *)
            dot = ref_normal * n 
            
            # If the vectors point in the same direction within tolerance
            if dot >= threshold_dot:
                faces_to_select.append("{}.f[{}]".format(mesh_name, poly_iter.index()))
                
            poly_iter.next()

        # 3. Apply the selection
        if faces_to_select:
            cmds.select(faces_to_select, replace=True)
            cmds.inViewMessage(amg="Selected {} faces.".format(len(faces_to_select)), pos='midCenter', fade=True)

SelectByNormalAPI()
