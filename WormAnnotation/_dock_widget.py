from napari_plugin_engine import napari_hook_implementation
from qtpy.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QRadioButton, QHBoxLayout, QLabel, QLineEdit
from qtpy.QtCore import QDir
from magicgui import magic_factory
from qtpy.QtWidgets import QGridLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox
from PyQt5 import QtWidgets
import numpy as np
import os
import h5py
import scipy.interpolate
from pathlib import Path

class Training_label(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        self.lastdir =''
       # print(self.lastdir)
        self.lastfile = '/home/weheliye@cscdom.csc.mrc.ac.uk/Desktop/Correct-Training-Label/Training_data' 
        self.basename = ''
        self.sub_seg_x =[]
        self.sub_seg_y = []
        self.number_of_labels =0
        self.row_num = 0 
        self.name_of_labels = ''

        #%%  Load Training button 
        training_btn = QPushButton("Load Data ('.hdf5')")
        training_btn.setFixedHeight(100)
        training_btn.setFixedWidth(200)
        training_btn.setStyleSheet("font-size: 20px")
        training_btn.clicked.connect(self._add_models)
        

        #%% good label the next label button 
        next_label_btn = QPushButton("Next Label ->")
        next_label_btn.setFixedHeight(100)
        next_label_btn.setFixedWidth(200)
        next_label_btn.setStyleSheet(" color: rgb(0, 0, 0); font-size: 20px")
        next_label_btn.clicked.connect(self._next_label)


        #%% Bad Label 
        prev_label_btn = QPushButton("<-Previous label")
        prev_label_btn.setFixedHeight(100)
        prev_label_btn.setFixedWidth(200)
        prev_label_btn.setStyleSheet("color: rgb(0, 0, 0); font-size: 20px")
        prev_label_btn.clicked.connect(self._prev_label)

        #%% Save Changes 
        self.save_label_btn = QPushButton("Save changes")
        self.save_label_btn.setFixedHeight(100)
        self.save_label_btn.setFixedWidth(200)
        self.save_label_btn.setStyleSheet("background-color: green ; color: rgb(255, 255, 255); font-size: 20px")
        self.save_label_btn.clicked.connect(self._save_label)
        
        #%% Labels training 
        self.Training_label_text = QLabel('Label number: ')
        self.Training_label_text.setStyleSheet("color: rgb(0, 0, 0); font-size: 20px")

        #%%  Delete item 
        self.delete_btn = QPushButton("Delete clip")
        self.delete_btn.setFixedHeight(100)
        self.delete_btn.setFixedWidth(200)
        self.delete_btn.setStyleSheet("background-color: red ; color: rgb(255, 255, 255); font-size: 20px")
        self.delete_btn.clicked.connect(self._delete_clip_)

        #%% String
        self.text_label = QLineEdit('')
        self.text_label.setStyleSheet("color: rgb(0, 0, 0); font-size: 20px")
        self.text_label.editingFinished.connect(lambda: self.pressenter())



       

        #hbox = QVBoxLayout()
        self.setLayout(QVBoxLayout())
        self.layout().addWidget((training_btn))
        self.layout().addWidget(next_label_btn)
        self.layout().addWidget(prev_label_btn)
        self.layout().addWidget(self.save_label_btn)
        self.layout().addWidget(self.Training_label_text)
        self.layout().addWidget(self.text_label)
        self.layout().addWidget(self.delete_btn)
        
        #self.layout().addLayout(hbox)

       # self.layout().addWidget(model_btn)
    def _message_error(self):
        msg = QMessageBox()     
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Error")
        msg.setInformativeText('The number of worms dont match the number of tracks')
        msg.setWindowTitle("Error")
        msg.exec_()
    def _add_models(self):
        fileNames, _ = QFileDialog.getOpenFileNames(self, 'Multiple File', self.lastdir, '*.hdf5', options=QtWidgets.QFileDialog.DontUseNativeDialog)
        print(fileNames, 'Hashi')
        #fileNames = ['Training_data/skeletonNN.hdf5']
        for file in fileNames:
            self.lastdir = os.path.dirname(file)
            name, _      = os.path.splitext(file)

            print(self.lastdir, 'weheliye')
            #print(name)
            self.lastfile = file
            self.basename = os.path.basename(file)
            with h5py.File((file), 'r+') as f:
                arrays_group = f['x_train']
                y_arrays_group = f['y_train']
                self.number_of_labels = len(arrays_group)
                self.name_of_labels = list(arrays_group)
                
                #for dataset_name_x, dataset_name_y in (zip(arrays_group,y_arrays_group)):
                    #self.number_of_labels+=1
                    
                self.sub_seg_x = arrays_group[self.name_of_labels[self.row_num]][:]   
                self.sub_seg_y = y_arrays_group[self.name_of_labels[self.row_num]][:]  
                #self.sub_seg_x = arrays_group[f'array_{self.row_num}'][:]
                #self.sub_seg_y = y_arrays_group[f'array_{self.row_num}'][:]
                      
        self._show_images(0)
        print(self.number_of_labels)
        self.total_num_images = self.number_of_labels-1
        self.Training_label_text.setText(f'Lable number: {self.row_num} out of {self.number_of_labels-1}')
        self.text_label.setText(f'{self.row_num}')
    
    def pressenter(self):
        
        self.viewer.layers.clear()
        self.row_num=int(self.text_label.text())
        row= self.row_num
        self._update_label()
        self._show_images(row)
        self.Training_label_text.setText(f'Lable number: {self.row_num} out of {self.number_of_labels-1}')
        #self.Training_label_text.setText(f'Lable number: {self.row_num} out of {self.number_of_labels-1}')
    
    def _smooth_data(self, x, y, length=49):
        path_t = np.linspace(0,1, x.size)
        r = np.vstack((x.reshape((1,x.size)),y.reshape((1,y.size))))
        spline = scipy.interpolate.interp1d(path_t,r,kind='cubic')
        t = np.linspace(np.min(path_t),np.max(path_t),length)
        r = spline(t)  
        new_x = r[0,:]  
        new_y = r[1,:]
        return new_x, new_y 

    def _save_label(self):
        num_worms = len(self.viewer.layers['Points'].data) 
        I = np.zeros([num_worms,49,3])
        Point_List =[]
        if num_worms%3!= 0:
            self._message_error()
        else:
            Point_List =[]
            for worm_data in (self.viewer.layers['Points'].data):
                x = worm_data[:,2]
                y = worm_data[:,1]
                x_new, y_new = self._smooth_data(x, y)
                Points =np.array (list (zip(np.repeat(worm_data[0,0],49),y_new, x_new)))
                Point_List.append(Points) 
            self._save_corrected_files(Point_List)

    def _save_corrected_files(self, Point_List, filename ="Corrected_training_files.hdf5"):
            if not Path(os.path.join(self.lastdir, filename)).exists():
                with h5py.File(os.path.join(self.lastdir, filename), 'w') as f, h5py.File((self.lastfile), 'a') as f_r:
                    # create group for arrays
                    xtrain_group = f.create_group('x_train')
                    ytrain_group = f.create_group('y_train')
                    dataset_name = self.name_of_labels[self.row_num] #f'array_{self.row_num}'
                    xtrain_group.create_dataset(dataset_name, data=self.viewer.layers['image'].data, compression='gzip')
                    ytrain_group.create_dataset(dataset_name, data=Point_List, compression='gzip')
                    
                    #print(dataset_name, self.total_num_images, self.number_of_labels-1)
                    del  f_r['x_train'][dataset_name]
                    del  f_r['y_train'][dataset_name]
                    self.number_of_labels = len(f_r['x_train'])
                    self.name_of_labels = list(f_r['x_train'])
                    if self.row_num!=0:
                        self.row_num=self.row_num-1
                    else:
                        self.row_num = 0 
                    self.Training_label_text.setText(f'Lable number: {self.row_num} out of {self.number_of_labels-1}')
                    self.text_label.setText(f'{self.row_num}')
            else: 
                  with h5py.File(os.path.join(self.lastdir, filename), 'a') as f, h5py.File((self.lastfile), 'a') as f_r:
                    # create group for arrays
                    xtrain_group = f['x_train']
                    ytrain_group = f['y_train']
                    dataset_name = self.name_of_labels[self.row_num] #f'array_{self.row_num}'
                    xtrain_group.create_dataset(dataset_name, data=self.viewer.layers['image'].data, compression='gzip')
                    ytrain_group.create_dataset(dataset_name, data=Point_List, compression='gzip')
                    
                    #print(dataset_name, self.total_num_images, self.number_of_labels-1)
                    del  f_r['x_train'][dataset_name]
                    del  f_r['y_train'][dataset_name]
                    self.number_of_labels = len(f_r['x_train'])
                    self.name_of_labels = list(f_r['x_train'])
                    if self.row_num!=0:
                        self.row_num=self.row_num-1
                    else:
                        self.row_num = 0 
                    self.Training_label_text.setText(f'Lable number: {self.row_num} out of {self.number_of_labels-1}')
                    self.text_label.setText(f'{self.row_num}')

   


    
    def _update_label(self):
         with h5py.File((self.lastfile), 'r+') as f:
                arrays_group = f['x_train']
                y_arrays_group = f['y_train']
                self.number_of_labels = len(arrays_group)
                
                #for dataset_name_x, dataset_name_y in (zip(arrays_group,y_arrays_group)):
                    #self.number_of_labels+=1
                    
                self.sub_seg_x = arrays_group[self.name_of_labels[self.row_num]][:]   
                self.sub_seg_y = y_arrays_group[self.name_of_labels[self.row_num]][:]     
                #self.sub_seg_x = arrays_group[f'array_{self.row_num}'][:]
                #self.sub_seg_y = y_arrays_group[f'array_{self.row_num}'][:]


    def _next_label(self):
        if self.row_num<self.number_of_labels-1:
            self.viewer.layers.clear()
            self.row_num=self.row_num+1
            row= self.row_num
            self._update_label()
            self._show_images(row)
            self.Training_label_text.setText(f'Lable number: {self.row_num} out of {self.number_of_labels-1}')
            self.text_label.setText(f'{self.row_num}')
        else:
            self.row_num=-1
            
            
    def _prev_label(self):
        #print(self.row_num)
        if self.row_num>=0 and self.row_num<self.number_of_labels-1:
            self.viewer.layers.clear()
            if self.row_num!=0:
                self.row_num=self.row_num-1
            row= self.row_num
            self._update_label()
            self._show_images(row)
            self.Training_label_text.setText(f'Lable number: {self.row_num} out of {self.number_of_labels-1}')
            self.text_label.setText(f'{self.row_num}')
        else:
            self.row_num = self.number_of_labels-1

    def _show_images(self, row_num=0):
        if row_num<=self.number_of_labels-1 and self.basename != 'Corrected_training_files.hdf5':
            self.save_label_btn.setDisabled(False)
            self.save_label_btn.setVisible(True)
            X_batch = self.sub_seg_x
            Y_batch = self.sub_seg_y
            #print(Y_batch.shape)
            batch_num = 0 #X_batch.shape[0]-1
            Point_List =[]

            for j in range(Y_batch.shape[1]):
                k=3
                for i in range(Y_batch.shape[2]):
                    k+=1
                    Points = Y_batch[batch_num, j, i,:,:]
                    Points = (list (zip(np.repeat(k,49),(Points[::4,1]), (Points[::4,0]))))
                    Point_List.append(Points)

            n_worms = int(np.array(Point_List).shape[0]/3)
            edge_color_cycle = ['blue', 'red','green','magenta','yellow','cyan','grey']
            features = {
            'class':  list(np.repeat([f'worm_{i}' for i in range(n_worms)], 3)),
                        }
            self.viewer.add_image(X_batch[batch_num,:,:,:], name='image')
            #self.viewer.add_points(Point_List, size=3, face_color='red')
            #self.viewer.add_shapes(Point_List, shape_type="path", edge_width=2, edge_color='red', opacity=0.6, name ='Points')
            self.viewer.add_shapes(Point_List, shape_type="path", features=features, edge_color='class',edge_width=2, edge_color_cycle=edge_color_cycle[:n_worms], opacity=0.6, name ='Points')
        else:
            #print(self.sub_seg_x[0,:].shape)
            #print(self.sub_seg_y[0].shape)
            self.save_label_btn.setDisabled(True)
            self.save_label_btn.setVisible(False)
            X_batch = self.sub_seg_x
            Point_List = self.sub_seg_y
            n_worms = int(np.array(Point_List).shape[0]/3)
            edge_color_cycle = ['blue', 'red','green','magenta','yellow','cyan','grey']
            features = {
            'class':  list(np.repeat([f'worm_{i}' for i in range(n_worms)], 3)),
                        }
            self.viewer.add_image(X_batch, name='image')
            #self.viewer.add_points(Point_List, size=3, face_color='red')
            self.viewer.add_shapes(Point_List, shape_type="path", features=features, edge_color='class',edge_width=2, edge_color_cycle=edge_color_cycle[:n_worms], opacity=0.6, name ='Points')
            
    def _delete_clip_(self):
         with  h5py.File((self.lastfile), 'a') as f_r:
                    dataset_name = self.name_of_labels[self.row_num] #f'array_{self.row_num}'
                    #print(dataset_name, self.total_num_images, self.number_of_labels-1)
                    del  f_r['x_train'][dataset_name]
                    del  f_r['y_train'][dataset_name]
                    self.number_of_labels = len(f_r['x_train'])
                    self.name_of_labels = list(f_r['x_train'])
                    if self.row_num!=0:
                        self.row_num=self.row_num-1
                    else:
                        self.row_num = 0 
                    self.Training_label_text.setText(f'Lable number: {self.row_num} out of {self.number_of_labels-1}')
                    self.text_label.setText(f'{self.row_num}')

