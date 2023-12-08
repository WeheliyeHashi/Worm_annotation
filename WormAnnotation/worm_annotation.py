#%%

import napari
from WormAnnotation._dock_widget import Training_label
import warnings
warnings.filterwarnings("ignore")

viewer = napari.Viewer(title='Behavgenom: Worm Annotator ')
viewer.window.add_dock_widget(Training_label(viewer), area="right")
napari.run()
# %%
