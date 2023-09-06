import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd
import numpy as np
from collections import Counter


class EchoGUI:
    """
    Developed with GPT-4
    The EchoGUI module provides a graphical user interface (GUI) for visualizing and managing liquid handling
    picklists for an Echo Liquid Handler. The application allows users to load picklists in CSV format,
    visualize source and destination plates, and interactively inspect transfer volumes between wells.
    Key features:
    *
    """

    def __init__(self, master):
        self.master = master
        master.title("Echo Liquid Handler GUI")

        self.main_canvas = tk.Canvas(master)
        self.main_canvas.grid(row=0, column=0, sticky="nsew")

        self.main_frame = tk.Frame(self.main_canvas)
        self.main_canvas.create_window((0, 0), window=self.main_frame, anchor="nw")

        self.load_picklist_button = tk.Button(self.main_frame, text="Load Picklist", command=self.load_picklist)
        self.load_picklist_button.grid(row=0, column=0)

        self.src_rows_label = tk.Label(self.main_frame, text="Source Plate Rows:")
        self.src_rows_label.grid(row=1, column=0)
        self.src_rows_var = tk.IntVar(value=16)
        self.src_rows_input = ttk.Spinbox(self.main_frame, from_=1, to=100, textvariable=self.src_rows_var)
        self.src_rows_input.grid(row=1, column=1)

        self.src_cols_label = tk.Label(self.main_frame, text="Source Plate Columns:")
        self.src_cols_label.grid(row=2, column=0)
        self.src_cols_var = tk.IntVar(value=24)
        self.src_cols_input = ttk.Spinbox(self.main_frame, from_=1, to=100, textvariable=self.src_cols_var)
        self.src_cols_input.grid(row=2, column=1)

        self.dst_rows_label = tk.Label(self.main_frame, text="Destination Plate Rows:")
        self.dst_rows_label.grid(row=3, column=0)
        self.dst_rows_var = tk.IntVar(value=16)
        self.dst_rows_input = ttk.Spinbox(self.main_frame, from_=1, to=100, textvariable=self.dst_rows_var)
        self.dst_rows_input.grid(row=3, column=1)

        self.dst_cols_label = tk.Label(self.main_frame, text="Destination Plate Columns:")
        self.dst_cols_label.grid(row=4, column=0)
        self.dst_cols_var = tk.IntVar(value=24)
        self.dst_cols_input = ttk.Spinbox(self.main_frame, from_=1, to=100, textvariable=self.dst_cols_var)
        self.dst_cols_input.grid(row=4, column=1)

        self.src_rows_var.trace("w", self.update_grids)
        self.src_cols_var.trace("w", self.update_grids)
        self.dst_rows_var.trace("w", self.update_grids)
        self.dst_cols_var.trace("w", self.update_grids)

        self.canvas = tk.Canvas(self.main_frame, width=800, height=700)
        self.canvas.grid(row=1, rowspan=6, column=2, padx=(50, 0))

        self.src_max_vol_label = tk.Label(self.main_frame, text="Max Source Well Volume:")
        self.src_max_vol_label.grid(row=5, column=0)
        self.src_max_vol_var = tk.DoubleVar(value=25000)
        self.src_max_vol_input = ttk.Spinbox(self.main_frame, from_=0, to=1000000, increment=0.1, textvariable=self.src_max_vol_var)
        self.src_max_vol_input.grid(row=5, column=1)
        self.src_max_vol_var.trace("w", self.update_well_colors)

        self.dst_max_vol_label = tk.Label(self.main_frame, text="Max Destination Well Volume:")
        self.dst_max_vol_label.grid(row=6, column=0)
        self.dst_max_vol_var = tk.DoubleVar(value=50000)
        self.dst_max_vol_input = ttk.Spinbox(self.main_frame, from_=0, to=1000000, increment=0.1, textvariable=self.dst_max_vol_var)
        self.dst_max_vol_input.grid(row=6, column=1)
        self.dst_max_vol_var.trace("w", self.update_well_colors)

        self.src_plate_label = tk.Label(self.main_frame, text="Source Plate")
        self.src_plate_label.grid(row=0, column=2, padx=(0, 600))
        self.dst_plate_label = tk.Label(self.main_frame, text="Destination Plate")
        self.dst_plate_label.grid(row=3, column=2, padx=(0, 600), pady=(20, 0))

        # drop box to select source plate / destination plate
        self.src_plate_combobox = ttk.Combobox(self.main_frame, state="readonly")
        self.src_plate_combobox.grid(row=0, column=2, padx=(0, 300))
        self.dst_plate_combobox = ttk.Combobox(self.main_frame, state="readonly")
        self.dst_plate_combobox.grid(row=3, column=2, padx=(0, 300), pady=(20, 0))

        # Bind the comboboxes to the update_grids function
        self.src_plate_combobox.bind("<<ComboboxSelected>>", self.update_grids)
        self.dst_plate_combobox.bind("<<ComboboxSelected>>", self.update_grids)

        # self.time_text = tk.Text(self.main_frame, wrap=tk.WORD, height=2, width=40)
        self.time_label = tk.Label(self.main_frame, text="Estimated time:", height=2, width=40)
        self.time_label.grid(row=0, column=2, padx=(500, 0))

        self.details_text = tk.Text(self.main_frame, wrap=tk.WORD, height=40, width=40)
        self.details_text.grid(row=0, rowspan=6, column=2, padx=(500, 0), pady=(20, 0))

        self.v_scrollbar = ttk.Scrollbar(master, orient="vertical", command=self.main_canvas.yview)
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")

        self.h_scrollbar = ttk.Scrollbar(master, orient="horizontal", command=self.main_canvas.xview)
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        self.main_canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)

        self.master.bind("<Configure>", lambda event: self.update_scroll_region())
        self.main_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.main_canvas.yview_scroll(-int(event.delta / 120), "units")

    def update_scroll_region(self):
        self.main_canvas.update_idletasks()
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))

    def update_well_colors(self, *args):
        self.visualize_plates()

    def load_picklist(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            picklist = pd.read_csv(file_path)
            picklist['Transfer Volume'] = round(picklist['Transfer Volume'] / 25) * 25  # 25nL transfer unit
            picklist = picklist.loc[picklist['Transfer Volume'] > 0]
            self.picklist = picklist

            if 'Source Plate Name' not in self.picklist.columns:
                self.picklist['Source Plate Name'] = 'sp1'
            picklist['Source Plate Name'] = picklist['Source Plate Name'].astype(str)
            src_plates = tuple(self.picklist['Source Plate Name'].unique())
            self.src_plate_combobox['values'] = src_plates  # must be tuple, not np.array
            self.src_plate_combobox.set(src_plates[0])

            if 'Destination Plate Name' not in self.picklist.columns:
                self.picklist['Destination Plate Name'] = 'dp1'
            picklist['Destination Plate Name'] = picklist['Destination Plate Name'].astype(str)
            dst_plates = tuple(self.picklist['Destination Plate Name'].unique())
            self.dst_plate_combobox['values'] = dst_plates   # must be tuple, not np.array
            self.dst_plate_combobox.set(dst_plates[0])

            self.visualize_plates()

    @staticmethod
    def estimate_time(pklist):
        """can only estimate for calibration AQ_BP"""
        vol = pklist['Transfer Volume'].sum()
        n_transfer = pklist.shape[0]
        seconds = round(6.7 / 30 * n_transfer + vol * 0.8 / 6000)
        return f"{seconds // 60} min {seconds % 60} sec"

    def create_grid_labels(self, row_count, col_count, x_offset, y_offset, cell_size):
        font_size = min(int(cell_size / 1.5), 12)  # Adjust the divisor to change font size scaling
        font = ("TkDefaultFont", font_size)

        for i in range(row_count):
            if i < 26:
                row_label = chr(65 + i)
            else:
                row_label = f"A{chr(65 + i - 26)}"
            self.canvas.create_text(x_offset + col_count * cell_size + 5,
                                    y_offset + i * cell_size + cell_size / 2,
                                    text=row_label, anchor=tk.W, font=font)
        for j in range(col_count):
            self.canvas.create_text(x_offset + j * cell_size + cell_size / 2,
                                    y_offset + row_count * cell_size, text=str(j + 1),
                                    anchor=tk.N, font=font)

    def visualize_plates(self):
        self.canvas.delete("all")

        # Get the selected source and destination plates
        src_plate = self.src_plate_combobox.get()
        dst_plate = self.dst_plate_combobox.get()

        # Filter the picklist based on the selected plates
        self.picklist_cur = self.picklist[(self.picklist['Source Plate Name'] == src_plate) 
                                          & (self.picklist['Destination Plate Name'] == dst_plate)]
        self.picklist_cursrc = self.picklist[self.picklist['Source Plate Name'] == src_plate]
        self.picklist_curdst = self.picklist[self.picklist['Destination Plate Name'] == dst_plate]

        self.src_rows = self.src_rows_var.get()
        self.src_cols = self.src_cols_var.get()
        self.dst_rows = self.dst_rows_var.get()
        self.dst_cols = self.dst_cols_var.get()

        max_plate_width, max_plate_height = 400, 300
        src_rect_size = min(max_plate_width / self.src_cols, max_plate_height / self.src_rows)
        dst_rect_size = min(max_plate_width / self.dst_cols, max_plate_height / self.dst_rows)

        self.create_grid_labels(self.src_rows, self.src_cols, 0, 0, src_rect_size)
        self.create_grid_labels(self.dst_rows, self.dst_cols, 0, 330, dst_rect_size)

        src_wells_used = set(self.picklist_cursrc['Source Well'])
        dst_wells_used = set(self.picklist_curdst['Destination Well'])

        max_src_vol = self.src_max_vol_var.get()
        max_dst_vol = self.dst_max_vol_var.get()

        self.src_fill_colors = np.empty((self.src_rows, self.src_cols)).astype('object')
        for i in range(self.src_rows):
            for j in range(self.src_cols):
                if i < 26:
                    well_name = f"{chr(i + 65)}{j + 1}"
                else:
                    well_name = f"A{chr(i - 26 + 65)}{j + 1}"
                transfers = self.picklist_cursrc[self.picklist_cursrc['Source Well'] == well_name]
                total_volume = transfers['Transfer Volume'].sum()
                if well_name in src_wells_used and total_volume > max_src_vol:
                    fill_color = "red"
                elif well_name in src_wells_used:
                    fill_color = "grey"
                else:
                    fill_color = "white"
                self.src_fill_colors[i, j] = fill_color

                x1, y1 = j * src_rect_size, i * src_rect_size
                x2, y2 = x1 + src_rect_size, y1 + src_rect_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, tags=f"src_{i}_{j}")
                self.canvas.tag_bind(f"src_{i}_{j}", "<Enter>", lambda e, r=i, c=j: self.on_hover(e, r, c, "src"))
                self.canvas.tag_bind(f"src_{i}_{j}", "<Leave>", lambda e, r=i, c=j: self.on_leave(e, r, c, "src"))

        self.dst_fill_colors = np.empty((self.dst_rows, self.dst_cols)).astype('object')
        for i in range(self.dst_rows):
            for j in range(self.dst_cols):
                if i < 26:
                    well_name = f"{chr(i + 65)}{j + 1}"
                else:
                    well_name = f"A{chr(i - 26 + 65)}{j + 1}"
                transfers = self.picklist_curdst[self.picklist_curdst['Destination Well'] == well_name]
                total_volume = transfers['Transfer Volume'].sum()
                if well_name in dst_wells_used and total_volume > max_dst_vol:
                    fill_color = "red"
                elif well_name in dst_wells_used:
                    fill_color = "grey"
                else:
                    fill_color = "white"
                self.dst_fill_colors[i, j] = fill_color

                x1, y1 = j * dst_rect_size, 330 + i * dst_rect_size
                x2, y2 = x1 + dst_rect_size, y1 + dst_rect_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, tags=f"dst_{i}_{j}")
                self.canvas.tag_bind(f"dst_{i}_{j}", "<Enter>", lambda e, r=i, c=j: self.on_hover(e, r, c, "dst"))
                self.canvas.tag_bind(f"dst_{i}_{j}", "<Leave>", lambda e, r=i, c=j: self.on_leave(e, r, c, "dst"))

        timetext = f"Estimated Time: total - {self.estimate_time(self.picklist)}, \n" \
                   f"current plate - {self.estimate_time(self.picklist_cur)}"
        self.time_label.config(text=timetext)

    def update_grids(self, *args):
        self.visualize_plates()

    def highlight_wells(self, wells, color, well_type):
        for well in wells:
            row, col = ord(well[0]) - 65, int(well[1:]) - 1
            tag = f"{well_type}_{row}_{col}"
            self.canvas.itemconfig(tag, fill=color)

    def on_hover(self, event, row, col, well_type):
        # Get the selected source and destination plates
        src_plate = self.src_plate_combobox.get()
        dst_plate = self.dst_plate_combobox.get()

        if row < 26:
            well = f"{chr(row + 65)}{col + 1}"
        else:
            well = f"A{chr(row - 26 + 65)}{col + 1}"

        details = well + "\n"
        if well_type == "src":
            transfers = self.picklist[(self.picklist['Source Well'] == well)
                                      & (self.picklist['Source Plate Name'] == src_plate)]
            total_volume = transfers['Transfer Volume'].sum()

            if not transfers.empty:
                details += f"Total volume: {total_volume} nl\nTransfers:\n"
                for _, transfer in transfers.iterrows():
                    details += f"{transfer['Destination Plate Name']}: " \
                               f"{transfer['Destination Well']} - {transfer['Transfer Volume']} nl\n"
                    if transfer['Destination Plate Name'] == dst_plate:
                        self.highlight_wells([transfer['Destination Well']], "blue", "dst")
            else:
                details += "No transfers from this well."

            self.details_text.delete("1.0", tk.END)
            self.details_text.insert(tk.END, self.simplify_details(details))

        elif well_type == "dst":
            transfers = self.picklist[(self.picklist['Destination Well'] == well)
                                      & (self.picklist['Destination Plate Name'] == dst_plate)]
            total_volume = transfers['Transfer Volume'].sum()

            if not transfers.empty:
                details += f"Total volume: {total_volume} nl\nTransfers:\n"
                for _, transfer in transfers.iterrows():
                    details += f"{transfer['Source Plate Name']}:" \
                               f" {transfer['Source Well']} - {transfer['Transfer Volume']} nl\n"
                    if transfer['Source Plate Name'] == src_plate:
                        self.highlight_wells([transfer['Source Well']], "blue", "src")
            else:
                details += "No transfers to this well."

            self.details_text.delete("1.0", tk.END)
            self.details_text.insert(tk.END, self.simplify_details(details))

    def on_leave(self, event, row, col, well_type):
        # Get the selected source and destination plates
        src_plate = self.src_plate_combobox.get()
        dst_plate = self.dst_plate_combobox.get()

        if row < 26:
            well = f"{chr(row + 65)}{col + 1}"
        else:
            well = f"A{chr(row - 26 + 65)}{col + 1}"

        if well_type == "src":
            transfers = self.picklist[(self.picklist['Source Well'] == well)
                                      & (self.picklist['Source Plate Name'] == src_plate)
                                      & (self.picklist['Destination Plate Name'] == dst_plate)]
            related_wells = transfers['Destination Well'].tolist()
            well_tag_prefix = "dst"
        else:
            transfers = self.picklist[(self.picklist['Destination Well'] == well)
                                      & (self.picklist['Source Plate Name'] == src_plate)
                                      & (self.picklist['Destination Plate Name'] == dst_plate)]
            related_wells = transfers['Source Well'].tolist()
            well_tag_prefix = "src"
        for related_well in related_wells:
            r, c = ord(related_well[0]) - 65, int(related_well[1:]) - 1
            tag = f"{well_tag_prefix}_{r}_{c}"
            if well_tag_prefix == 'src':
                original_color = self.src_fill_colors[r, c]
            else:
                original_color = self.dst_fill_colors[r, c]
            self.canvas.itemconfig(tag, fill=original_color)

        self.canvas.delete("highlight")

    @staticmethod
    def simplify_details(details):
        # when 'details' variable contains the text with repeated transfers
        lines = details.strip().split('\n')
        counter = Counter(lines)

        simplified_details = ""
        for transfer, count in counter.items():
            if count > 1:
                simplified_details += f"{transfer} (*{count})\n"
            else:
                simplified_details += f"{transfer}\n"

        # Now, 'simplified_details' contains the simplified text
        return simplified_details

def new_window(shape="1920x1080"):
    root = tk.Tk()
    root.geometry(shape)
    gui = EchoGUI(root)
    root.mainloop()
        
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1920x1080")
    gui = EchoGUI(root)
    root.mainloop()
