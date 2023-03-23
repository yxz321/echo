# EchoGUI Module Documentation

## Overview

The EchoGUI module provides a graphical user interface (GUI) for visualizing and managing liquid handling picklists for an Echo Liquid Handler. The application allows users to load picklists in CSV format, visualize source and destination plates, and interactively inspect transfer volumes between wells.

## Usage

Can be used as a main function, or imported and used in a Python script. To incorporate the EchoGUI into a python script, create a Tkinter root object and pass it to the EchoGUI class constructor. Then, call the mainloop() method on the root object to start the GUI event loop.

```python
import tkinter as tk
from echogui import EchoGUI

if __name__ == "__main__":
    root = tk.Tk()
    gui = EchoGUI(root)
    root.geometry("1920x1080")  # using full screen is suggested in 1080p
    root.mainloop()
```

## EchoGUI Class

### `__init__(self, master)`

The constructor method initializes the EchoGUI object and sets up the main window and the user interface components.

- `master`: The parent widget for the EchoGUI. This is typically the root Tkinter object.

### `load_picklist(self)`

Loads a picklist from a CSV file selected by the user using a file dialog. Once loaded, the method visualizes the source and destination plates based on the picklist data.

### `create_grid_labels(self, row_count, col_count, x_offset, y_offset, cell_size)`

Creates the labels for plate grid rows and columns based on the provided parameters.

### `visualize_plates(self)`

Visualizes the source and destination plates based on the picklist data, including well colors based on transfer volumes and max volume limits.

### `update_grids(self, *args)`

Updates the plate grids visualization based on the user-specified row and column values.

### `on_hover(self, event, row, col, well_type)`

Displays detailed information about a well when the mouse hovers over it, including the total volume transferred and the related wells for the transfers.

- `event`: The event that triggered the method call.
- `row`: The row of the well being hovered over.
- `col`: The column of the well being hovered over.
- `well_type`: The type of well being hovered over, either "src" (source) or "dst" (destination).

### `on_leave(self, event, well_type)`

Removes the blue highlighting of related wells when the mouse leaves the focused well.

- `event`: The event that triggered the method call.
- `well_type`: The type of well being hovered over, either "src" (source) or "dst" (destination).

# echo_helper documentation
