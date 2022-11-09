from tkinter.ttk import Notebook
from HeaderFrame import HeaderFrame
from HistogramFrame import HistogramFrame
from FiltersFrame import FiltersFrame


# Frame that displays the metadata/headers
class MetadataFrame(Notebook):
    def __init__(self, parent):
        # Root Window
        self.parent = parent
        self.parent.update_idletasks()

        # Constants
        self.window_dimensions = (
            int(self.parent.winfo_width() * 0.3) - 35,
            self.parent.winfo_height())

        super(MetadataFrame, self).__init__(
            self.parent,
            width=self.window_dimensions[0],
            height=int(self.window_dimensions[1] * 0.9)
        )
        self.update_idletasks()

        # Child Frame configs
        child_configs = {
            "bg": "#3e5c76",
            "width": self.window_dimensions[0],
            "height": self.window_dimensions[1]
        }

        # Instantiate header frame tab
        self.header_frame = HeaderFrame(self, child_configs)
        self.add(self.header_frame, text="Headers")

        # Instantiate histogram frame tab
        self.histogram_frame = HistogramFrame(self, child_configs)
        self.add(self.histogram_frame, text="Histograms")

        # Instantiate filters frame tab
        self.filters_frame = FiltersFrame(self, child_configs)
        self.add(self.filters_frame, text="Filters")

        self.grid(column=1, row=0, pady=10)
        self.grid_propagate(False)
