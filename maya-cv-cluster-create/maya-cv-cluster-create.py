import maya.cmds as cmds

# Create a cluster on each CV of selected curve

def create_clusters_on_curve():
    sel = cmds.ls(selection=True)
    if not sel:
        cmds.warning("Select a curve.")
        return

    curve = sel[0]

    # Validate curve
    shapes = cmds.listRelatives(curve, shapes=True) or []
    if not shapes or cmds.nodeType(shapes[0]) != "nurbsCurve":
        cmds.warning("Selection is not a NURBS curve.")
        return

    # Get all CVs
    cvs = cmds.ls(curve + ".cv[*]", flatten=True)

    for i, cv in enumerate(cvs):
        # Create cluster on CV
        cluster_node, cluster_handle = cmds.cluster(cv)

        # Clean naming: curvename_CL_##
        cmds.rename(cluster_handle, f"{curve}_CL_{i+1:02d}")

    cmds.select(curve)

    # Nice viewport message
    cmds.inViewMessage(
        amg='<hl>Clusters created</hl>',
        pos='botLeft',
        fade=True
    )


create_clusters_on_curve()
