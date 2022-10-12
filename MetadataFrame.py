from tkinter.ttk import Notebook
from HeaderFrame import HeaderFrame
from HistogramFrame import HistogramFrame
from FiltersFrame import FiltersFrame


# Frame that displays the metadata/headers
class MetadataFrame:
    def __init__(self, parent):
        # Root Window
        self.parent = parent
        self.parent.update_idletasks()

        # Constants
        self.window_dimensions = (
            int(self.parent.winfo_width() * 0.3) - 35,
            self.parent.winfo_height())

        # Child Frame configs
        child_configs = {
            "bg": "#3e5c76",
            "width": self.window_dimensions[0],
            "height": self.window_dimensions[1]
        }

        self.metadata_tabs = Notebook(self.parent,
                                      width=self.window_dimensions[0],
                                      height=int(self.window_dimensions[1] * 0.9))
        self.metadata_tabs.update_idletasks()

        # Instantiate upper right frame
        self.header_frame = HeaderFrame(self.metadata_tabs, child_configs)
        self.metadata_tabs.add(self.header_frame, text="Headers")

        # Instantiate lower right frame
        self.histogram_frame = HistogramFrame(self.metadata_tabs, child_configs)
        self.metadata_tabs.add(self.histogram_frame, text="Histograms")

        self.filters_frame = FiltersFrame(self.metadata_tabs, child_configs)
        self.metadata_tabs.add(self.filters_frame, text="Filters")

        self.metadata_tabs.grid(column=1, row=0, pady=10)
        self.metadata_tabs.grid_propagate(False)
        self.header_frame.update_idletasks()
