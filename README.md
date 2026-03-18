# Maya Easy Renamer

Advanced renaming and scene organization utility for Autodesk Maya.

## Key Features

* **Smart Renaming:** Sequential numbering with custom padding and support for hash patterns (e.g., `Object_###`).
* **Search & Replace:** Quick string replacement with optional Match Case and Regex support.
* **Affix Tools:** Instant addition of prefixes and suffixes to selected objects.
* **Hierarchy Safety:** Built on a UUID-based core to ensure stable renaming even within complex parent-child chains.
* **Cleanup & Organization:** * Alphabetical sorting of objects in the Outliner.
    * Stripping of end digits and namespaces.
    * Character trimming from the start or end of object names.
* **UI:** Built with PySide for cross-version compatibility (Maya 2017–2025+).

## Installation

1. Copy the code from `maya_easy_renamer.py`.
2. Open the **Script Editor** in Maya and paste the code into a **Python** tab.
3. Highlight the code and drag it to your **Shelf** to create a shortcut icon.

## Usage

1. Select the objects you want to rename in the Outliner or Viewport.
2. Run the script and use the corresponding section (Search, Affix, or Numbering).
3. For sequential numbering, use the radio buttons for quick padding or enter a custom value in the input field.
