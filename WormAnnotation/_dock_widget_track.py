import os
from pathlib import Path

import h5py
import numpy as np
import scipy.interpolate
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QMessageBox,
    QComboBox,
    QFileDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QShortcut,
    QVBoxLayout,
    QWidget,
)


class Training_label(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        self.lastdir = ""
        self.lastfile = ""
        self.basename = ""
        self.sub_seg_x = []
        self.sub_seg_y = []
        self.number_of_labels = 0
        self.row_num = 0
        self.name_of_labels = ""

        # %% Load Training button
        training_btn = QPushButton("Load Data (*.hdf5)")
        training_btn.setToolTip("Load training data from an HDF5 file.")
        training_btn.setFixedHeight(100)
        training_btn.setFixedWidth(150)
        training_btn.setStyleSheet("font-size: 16px; color: white;")
        training_btn.clicked.connect(self._add_models)

        # %% Next Label button
        next_label_btn = QPushButton("Next Label ->")
        next_label_btn.setFixedHeight(50)
        next_label_btn.setFixedWidth(150)
        next_label_btn.setStyleSheet("font-size: 14px; color: white;")
        next_label_btn.clicked.connect(self._next_label)
        next_label_btn.setToolTip("Shortcut: .")

        # %% Previous Label button
        prev_label_btn = QPushButton("<- Previous Label")
        prev_label_btn.setFixedHeight(50)
        prev_label_btn.setFixedWidth(150)
        prev_label_btn.setStyleSheet("font-size: 14px; color: white;")
        prev_label_btn.clicked.connect(self._prev_label)
        prev_label_btn.setToolTip("Shortcut: ,")

        # %% Reset Canvas button
        reset_canvas_btn = QPushButton("Clear all")
        reset_canvas_btn.setFixedHeight(80)
        reset_canvas_btn.setFixedWidth(150)
        reset_canvas_btn.setStyleSheet("background-color: orange; font-size: 14px; color: black;")
        reset_canvas_btn.clicked.connect(self._reset_canvas)
        reset_canvas_btn.setToolTip("Shortcut: R")

        # %% Save Changes button
        self.save_label_btn = QPushButton("Save Changes")
        self.save_label_btn.setFixedHeight(80)
        self.save_label_btn.setFixedWidth(150)
        self.save_label_btn.setStyleSheet("background-color: green; font-size: 14px; color: black;")
        self.save_label_btn.clicked.connect(self._save_label)
        self.save_label_btn.setToolTip("Shortcut: S")

        # %% Delete item button
        self.delete_btn = QPushButton("Delete Clip")
        self.delete_btn.setFixedHeight(80)
        self.delete_btn.setFixedWidth(150)
        self.delete_btn.setStyleSheet("background-color: red; font-size: 14px; color: black;")
        self.delete_btn.clicked.connect(self._delete_clip_)
        self.delete_btn.setToolTip("Shortcut: D")

        # %% Dropdown list for toggling views
        self.view_toggle_dropdown = QComboBox()
        self.view_toggle_dropdown.addItems(["Show skeletons", "Bounding Box"])
        self.view_toggle_dropdown.setFixedHeight(100)
        self.view_toggle_dropdown.setFixedWidth(150)  # Increased width for better visibility
        self.view_toggle_dropdown.setStyleSheet("""
            QComboBox {
                background-color: lightblue;
                font-size: 14px;  /* Increased font size */
                color: black;
                border: 1px solid black;
            }
            QComboBox QAbstractItemView {
                background-color: white;  /* Dropdown options background */
                color: black;  /* Dropdown options text color */
                selection-background-color: lightgray;  /* Highlight color for selected option */
                selection-color: black;
            }
        """)
        self.view_toggle_dropdown.currentTextChanged.connect(self._toggle_view)

        # %% Labels training
        self.Training_label_text = QLabel("Label number: ")
        self.Training_label_text.setStyleSheet("font-size: 14px; color: white;")

        # %% String input
        self.text_label = QLineEdit("")
        self.text_label.setFixedHeight(50)
        self.text_label.setFixedWidth(150)
        self.text_label.setStyleSheet("font-size: 14px; color: white;")
        self.text_label.editingFinished.connect(lambda: self.pressenter())

        # Layout setup
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(training_btn)
        self.layout().addWidget(next_label_btn)
        self.layout().addWidget(prev_label_btn)
        self.layout().addWidget(self.save_label_btn)
        self.layout().addWidget(self.delete_btn)
        self.layout().addWidget(reset_canvas_btn)
        self.layout().addWidget(self.view_toggle_dropdown)
        self.layout().addWidget(self.Training_label_text)
        self.layout().addWidget(self.text_label)

        # Shortcut keys
        shortcut = QShortcut(QKeySequence("D"), self)
        shortcut.activated.connect(self._delete_clip_)
        shortcut = QShortcut(QKeySequence("S"), self)
        shortcut.activated.connect(self._save_label)
        shortcut = QShortcut(QKeySequence(","), self)
        shortcut.activated.connect(self._prev_label)
        shortcut = QShortcut(QKeySequence("."), self)
        shortcut.activated.connect(self._next_label)
        shortcut = QShortcut(QKeySequence("R"), self)
        shortcut.activated.connect(self._reset_canvas)

    # self.layout().addWidget(model_btn)
    def _message_error(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Error")
        msg.setInformativeText("The number of worms dont match the number of tracks")
        msg.setWindowTitle("Error")
        msg.exec_()

    def _add_models(self):
        fileNames, _ = QFileDialog.getOpenFileNames(
            self,
            "Multiple File",
            self.lastdir,
            "*.hdf5",
            # options=QFileDialog.DontUseNativeDialog,
        )
       
        for file in fileNames:
            self.lastdir = os.path.dirname(file)
            name, _ = os.path.splitext(file)

          
            self.lastfile = file
            self.basename = Path(file).stem  #os.path.basename(file)
            #print(self.basename)
            with h5py.File((file), "r+") as f:
                arrays_group = f["x_train"]
                y_arrays_group = f["y_train"]
                self.number_of_labels = len(arrays_group)
                self.name_of_labels = list(arrays_group)

                # for dataset_name_x, dataset_name_y in (zip(arrays_group,y_arrays_group)):
                # self.number_of_labels+=1

                self.sub_seg_x = arrays_group[self.name_of_labels[self.row_num]][:]
                self.sub_seg_y = y_arrays_group[self.name_of_labels[self.row_num]][:]
                # self.sub_seg_x = arrays_group[f'array_{self.row_num}'][:]
                # self.sub_seg_y = y_arrays_group[f'array_{self.row_num}'][:]

        self._show_images(0)
        print(self.number_of_labels)
        self.total_num_images = self.number_of_labels - 1
        self.Training_label_text.setText(
            f"Label number: {self.row_num} out of {self.number_of_labels-1}"
        )
        self.text_label.setText(f"{self.row_num}")

    def pressenter(self):

        self.viewer.layers.clear()
        self.row_num = int(self.text_label.text())
        row = self.row_num
        self._update_label()
        self._show_images(row)
        self.Training_label_text.setText(
            f"Label number: {self.row_num} out of {self.number_of_labels-1}"
        )
        # self.Training_label_text.setText(f'Lable number: {self.row_num} out of {self.number_of_labels-1}')

    def _smooth_data(self, x, y, length=49):
        path_t = np.linspace(0, 1, x.size)
        r = np.vstack((x.reshape((1, x.size)), y.reshape((1, y.size))))
        spline = scipy.interpolate.interp1d(path_t, r, kind="cubic")
        t = np.linspace(np.min(path_t), np.max(path_t), length)
        r = spline(t)
        new_x = r[0, :]
        new_y = r[1, :]
        return new_x, new_y

    def _reorder_worm_struct(self, Y):
        Y_reshaped = Y.reshape([-1, Y.shape[2]])
        y = Y_reshaped[Y_reshaped[:, 0].argsort(kind="stable")].reshape(
            Y.shape[0], Y.shape[1], Y.shape[2]
        )
        return y

    def _return_DT_C_label(self, Point_List, n_worms):
        Y = np.array(Point_List)
        Y_train = np.zeros([n_worms, 3, 49, 2])
        if n_worms == 1:
            Y_train[0, :] = self._reorder_worm_struct(Y)[:, :, [2, 1]]
        else:
            for s, i in enumerate(range(0, Y.shape[0], 3)):
                Y_train[s, :] = self._reorder_worm_struct(Y[i : i + 1])[:, :, [2, 1]]
        return Y_train

    def _save_label(self):
        num_worms = len(self.viewer.layers["Points"].data)

        if num_worms % 3 != 0:
            self._message_error()
            return

        Point_List = []
        for worm_data in self.viewer.layers["Points"].data:
            x, y = worm_data[:, 2], worm_data[:, 1]
            if x.any():
                x_new, y_new = self._smooth_data(x, y)
                Points = np.array(
                    list(zip(np.repeat(worm_data[0, 0], 49), y_new, x_new))
                )
                Point_List.append(Points)

        n_worms_t = len(Point_List) // 3
        Y_train = self._return_DT_C_label(Point_List, n_worms_t)
        self._save_corrected_files(Point_List, Y_train)

    def _save_corrected_files(self, Point_List, Y_train):
        # Check if self.basename contains "_Corrected_training_file.hdf5"
        if "_Corrected_training_file" in self.basename:
            # Open the existing file for editing
            file_path = os.path.join(self.lastdir, f"{self.basename}.hdf5")
            with h5py.File(file_path, "a") as f:
                xtrain_group = f["x_train"]
                ytrain_group = f["y_train"]
                ytrain_DT_C = f["y_train_dt_c"]

                dataset_name = self.name_of_labels[self.row_num]

                # Replace existing datasets with updated data
                if dataset_name in xtrain_group:
                    del xtrain_group[dataset_name]
                xtrain_group.create_dataset(dataset_name, data=self.viewer.layers["image"].data, compression="gzip")

                if dataset_name in ytrain_group:
                    del ytrain_group[dataset_name]
                ytrain_group.create_dataset(dataset_name, data=Point_List, compression="gzip")

                if dataset_name in ytrain_DT_C:
                    del ytrain_DT_C[dataset_name]
                ytrain_DT_C.create_dataset(dataset_name, data=Y_train, compression="gzip")

                # Update label information
                self.number_of_labels = len(xtrain_group)
                self.name_of_labels = list(xtrain_group)
                self.row_num = max(0, self.row_num - 1)

                self.Training_label_text.setText(f"Label number: {self.row_num} out of {self.number_of_labels-1}")
                self.text_label.setText(f"{self.row_num}")
        else:
            # Remove "annotations" from self.basename
            sanitized_basename = self.basename.replace("annotations", "")
            filename = f"{sanitized_basename}_Corrected_training_file.hdf5"
            file_path = os.path.join(self.lastdir, filename)
            mode = "w" if not Path(file_path).exists() else "a"

            with h5py.File(file_path, mode) as f, h5py.File(self.lastfile, "a") as f_r:
                xtrain_group = f.require_group("x_train")
                ytrain_group = f.require_group("y_train")
                ytrain_DT_C = f.require_group("y_train_dt_c")

                dataset_name = self.name_of_labels[self.row_num]
                xtrain_group.create_dataset(dataset_name, data=self.viewer.layers["image"].data, compression="gzip")
                ytrain_group.create_dataset(dataset_name, data=Point_List, compression="gzip")
                ytrain_DT_C.create_dataset(dataset_name, data=Y_train, compression="gzip")

                del f_r["x_train"][dataset_name]
                del f_r["y_train"][dataset_name]

                self.number_of_labels = len(f_r["x_train"])
                self.name_of_labels = list(f_r["x_train"])
                self.row_num = max(0, self.row_num - 1)

                self.Training_label_text.setText(f"Label number: {self.row_num} out of {self.number_of_labels-1}")
                self.text_label.setText(f"{self.row_num}")

        self._next_label()

    def _update_label(self):
        with h5py.File(self.lastfile, "r+") as f:
            arrays_group = f["x_train"]
            y_arrays_group = f["y_train"]
            self.number_of_labels = len(arrays_group)
            self.sub_seg_x = arrays_group[self.name_of_labels[self.row_num]][:]
            self.sub_seg_y = y_arrays_group[self.name_of_labels[self.row_num]][:]

    def _next_label(self):

        if self.row_num < self.number_of_labels - 1:
            self.viewer.layers.clear()
            self.row_num += 1
            self._update_label()
            self._show_images(self.row_num)
            self.Training_label_text.setText(
                f"Label number: {self.row_num} out of {self.number_of_labels-1}"
            )
            self.text_label.setText(f"{self.row_num}")
        else:
            self.row_num = -1

    def _prev_label(self):
        # print(self.row_num)
        if 0 <= self.row_num < self.number_of_labels - 1:
            self.viewer.layers.clear()
            self.row_num = max(0, self.row_num - 1)
            self._update_label()
            self._show_images(self.row_num)
            self.Training_label_text.setText(
                f"Label number: {self.row_num} out of {self.number_of_labels-1}"
            )
            self.text_label.setText(f"{self.row_num}")
        else:
            self.row_num = self.number_of_labels - 1

    def _show_images(self, row_num=0):
        if row_num <= self.number_of_labels - 1 and "_Corrected_training_file" not in self.basename: #self.basename != "Corrected_training_files.hdf5":
            # print("wrong file",self.basename)
            self.save_label_btn.setDisabled(False)
            self.save_label_btn.setVisible(True)
            X_batch, Y_batch = self.sub_seg_x, self.sub_seg_y
            Point_List = [
                list(zip(np.repeat(3 + i + 1, 49), Points[::4, 1], Points[::4, 0]))
                for j in range(Y_batch.shape[1])
                for i, Points in enumerate(Y_batch[0, j])
            ]
        else:
            # self.save_label_btn.setDisabled(True)
            # self.save_label_btn.setVisible(False)
            X_batch = self.sub_seg_x 
            Point_List = [[pt for i, pt in enumerate(path) if i % 4 == 0] for path in self.sub_seg_y]
            

        n_worms = len(Point_List) // 3
        edge_color_cycle = ["blue", "red", "green", "magenta", "yellow", "cyan", "grey"]
        features = {"class": list(np.repeat([f"worm_{i}" for i in range(n_worms)], 3))}

        self.viewer.add_image(X_batch, name="image")
        self.viewer.add_shapes(
            Point_List,
            shape_type="path",
            features=features,
            edge_color="class",
            edge_width=2,
            edge_color_cycle=edge_color_cycle[:n_worms],
            opacity=0.6,
            name="Points",
        )

    def _delete_clip_(self):
        with h5py.File((self.lastfile), "a") as f_r:
            dataset_name = self.name_of_labels[self.row_num]  # f'array_{self.row_num}'
            # print(dataset_name, self.total_num_images, self.number_of_labels-1)
            del f_r["x_train"][dataset_name]
            del f_r["y_train"][dataset_name]
            self.number_of_labels = len(f_r["x_train"])
            self.name_of_labels = list(f_r["x_train"])
            if self.row_num != 0:
                self.row_num = self.row_num - 1
            else:
                self.row_num = 0
            self.Training_label_text.setText(
                f"Label number: {self.row_num} out of {self.number_of_labels-1}"
            )
            self.text_label.setText(f"{self.row_num}")
        self._next_label()

    def _reset_canvas(self):
        """Clears all layers, images, and data from Napari and resets to the initial state."""
        self.viewer.layers.clear()  # Remove all layers from Napari
        self.sub_seg_x = []  # Reset image data
        self.sub_seg_y = []  # Reset label data
        self.number_of_labels = 0  # Reset label count
        self.row_num = 0  # Reset row number
        self.name_of_labels = ""  # Reset label names
        self.Training_label_text.setText("Label number: ")  # Reset label text
        self.text_label.setText("")  # Clear text input

    def _toggle_view(self, selected_view):
        """Toggle between showing images and bounding box."""
        if selected_view == "Bounding Box":
            self._show_bounding_box()
        elif selected_view == "Show skeletons":
            # Clear the bounding box layer if it exists
            if "Bounding Boxes" in self.viewer.layers:
                self.viewer.layers.remove("Bounding Boxes")
            
            # Activate the "Points" layer
            points_layer = next((layer for layer in self.viewer.layers if layer.name == "Points"), None)
            if points_layer:
                self.viewer.layers.selection.active = points_layer
            
            # Show skeletons
            #self._show_images(self.row_num)

    def _show_bounding_box(self):
        """Display bounding box around skeletons for frames 4, 5, and 6."""
        # Ensure the "Points" layer exists
        points_layer = next((layer for layer in self.viewer.layers if layer.name == "Points"), None)
        if points_layer is None:
            self._message_warning("Please draw at least one skeleton before viewing a bounding box.")
            return

        # Remove origin data points (e.g., [0, 0]) and filter for frames 4, 5, and 6
        filtered_data = [
            worm_data for worm_data in points_layer.data
            if not np.all(worm_data == 0) 
        ]

        if not filtered_data:
            self._message_warning("No skeletons found for frames 4, 5, or 6.")
            return

        bounding_boxes = []
        for worm_data in filtered_data:
            x, y = worm_data[:, 2], worm_data[:, 1]
            if x.any():
                y_min, y_max = np.min(x)-10, np.max(x)+10
                x_min, x_max = np.min(y)-10, np.max(y)+10
                for frame in range(4, 7):
                    bounding_boxes.append([[frame,x_min, y_min], [frame,x_max, y_min], [frame, x_max, y_max], [frame,x_min, y_max]])
       
        n_worms = len(bounding_boxes) // 3
        edge_color_cycle = ["blue", "red", "green", "magenta", "yellow", "cyan", "grey"]
        features = {"class": list(np.repeat([f"worm_{i}" for i in range(n_worms)], 3))}


        self.viewer.add_shapes(
            bounding_boxes,
            shape_type="rectangle",
            features=features,
            face_color="transparent",
            edge_color="class",
            edge_width=2,
            edge_color_cycle=edge_color_cycle[:n_worms],
            # edge_color="yellow",
            # face_color="transparent",
            # edge_width=2,
            opacity=1,
            name="Bounding Boxes",
        )

    def _message_warning(self, message):
        """Display a warning message."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("Warning")
        msg.setInformativeText(message)
        msg.setWindowTitle("Warning")
        msg.exec_()
