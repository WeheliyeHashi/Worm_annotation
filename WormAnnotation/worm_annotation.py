# %%

import warnings

import napari

from WormAnnotation._dock_widget_track import Training_label

warnings.filterwarnings("ignore")

viewer = napari.Viewer(title="Behavgenom: Worm Annotator ")
viewer.window.add_dock_widget(Training_label(viewer), area="right")
napari.run()
# %%
