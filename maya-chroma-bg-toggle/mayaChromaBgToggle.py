import maya.cmds as cmds

# Simple chroma (green) background toggle for Maya

# Stored user settings
global CHROMA_PREV_GRAD
global CHROMA_PREV_BG

if 'CHROMA_PREV_GRAD' not in globals():
    CHROMA_PREV_GRAD = cmds.displayPref(query=True, displayGradient=True)

if 'CHROMA_PREV_BG' not in globals():
    CHROMA_PREV_BG = cmds.displayRGBColor("background", query=True)


def is_green(bg, tolerance=0.05):
    """Check if color is close to pure green"""
    return (
        abs(bg[0] - 0.0) < tolerance and
        abs(bg[1] - 1.0) < tolerance and
        abs(bg[2] - 0.0) < tolerance
    )


def toggle_chroma_bg():
    global CHROMA_PREV_GRAD
    global CHROMA_PREV_BG

    is_grad = cmds.displayPref(query=True, displayGradient=True)
    bg = cmds.displayRGBColor("background", query=True)

    # Detect current chroma state
    chroma_active = (not is_grad) and is_green(bg)

    if chroma_active:
        # Restore previous settings
        cmds.displayPref(displayGradient=CHROMA_PREV_GRAD)
        cmds.displayRGBColor("background", *CHROMA_PREV_BG)
    else:
        # Save current settings
        CHROMA_PREV_GRAD = is_grad
        CHROMA_PREV_BG = bg

        # Set pure green background
        cmds.displayPref(displayGradient=False)
        cmds.displayRGBColor("background", 0.0, 1.0, 0.0)


toggle_chroma_bg()
