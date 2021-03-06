# -*- coding: utf-8 -*-
"""Untitled7.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/103aPljurAD_fdeqXhTsLqQpjlr6ufFIQ
"""

# Commented out IPython magic to ensure Python compatibility.
# % cp drive/'My Drive'/Val.zip -d ./
! unzip Val.zip

! pip install -U segmentation-models

import segmentation_models as sm
import keras
from keras import optimizers
from keras.preprocessing.image import ImageDataGenerator
keras.backend.set_image_data_format('channels_last')
import os

!nvidia-smi

############ online learning ##########################
############ run the block at bottom first##########
model = sm.Unet('resnet34',classes=1, activation='sigmoid',input_shape=(None, None, 3))
# for layer in model.layers:
#   layer.trainable=True
#   layerName=str(layer.name)
#   if layerName.startswith("decoder") or layerName.startswith("Final_"):
#     layer.trainable=True
#   else: layer.trainable=False       #freeze/unfreeze the encoder

folder = 'kite-surf'
sgd = optimizers.SGD(lr=0.0001, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(optimizer=sgd,loss=sm.losses.bce_jaccard_loss,
  metrics=[sm.metrics.iou_score],)
load_shot(folder,'00')
train_generator, val_generator = val_loader(folder)
model.load_weights('drive/My Drive/65iou.h5') #load parent model
history = model.fit_generator(
    train_generator,
    steps_per_epoch=1000,
    epochs=20,verbose = 1,
    validation_data=val_generator, validation_steps=dict[folder],
    initial_epoch=0)
model.save(folder+'.h5')
##########################end#######################

# Commented out IPython magic to ensure Python compatibility.
##########################parent model training#################
# % cp drive/'My Drive'/DAVIS.zip -d ./
! unzip DAVIS.zip

image_datagen = ImageDataGenerator( rotation_range=90,
                   width_shift_range=0.1,
                   height_shift_range=0.1,
                   zoom_range=0.2, horizontal_flip=True,
                   vertical_flip = True, rescale= 1./255)
mask_datagen = ImageDataGenerator( rotation_range=90,
                   width_shift_range=0.1,
                   height_shift_range=0.1,
                   zoom_range=0.2, horizontal_flip=True,
                   vertical_flip = True, rescale= 1./255)
image_datagen1 = ImageDataGenerator(featurewise_center=False,
                                   featurewise_std_normalization=False,
                                   rescale= 1./255)
mask_datagen1 = ImageDataGenerator(rescale= 1./255)
seed = 1
image_generator = image_datagen.flow_from_directory(
    'DAVIS/JPEGImages/480p/atrain',target_size=(480,832),
    class_mode=None,batch_size=8,
    seed=seed)
mask_generator = mask_datagen.flow_from_directory(
    'DAVIS/Annotations/480p/atrain',target_size=(480,832),
    class_mode=None,batch_size=8,
    color_mode = 'grayscale',
    seed=seed)
image_generator1 = image_datagen1.flow_from_directory(
    'DAVIS/JPEGImages/480p/aval',target_size=(480,832),
    class_mode=None,batch_size=8,
    seed=1)
mask_generator1 = mask_datagen1.flow_from_directory(
    'DAVIS/Annotations/480p/aval',target_size=(480,832),
    class_mode=None,batch_size=8,
    color_mode = 'grayscale',
    seed=seed)
#merge
def combine_generator(gen1, gen2):
    while True:
        yield(gen1.next(), gen2.next())   
train_generator = combine_generator(image_generator, mask_generator)
val_generator = combine_generator(image_generator1, mask_generator1)

sgd = optimizers.SGD(lr=0.001, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(optimizer=sgd,loss=sm.losses.bce_jaccard_loss,
    metrics=[sm.metrics.iou_score],)
model.fit_generator(
    train_generator,
    steps_per_epoch=1000,
    epochs=,
    validation_data=val_generator,validation_steps=172,initial_epoch = 0)
model.save('parent.h5')
##################### end #####################

from keras.preprocessing import image
import numpy as np
import cv2
import os
from matplotlib import pyplot as plt
def img2np(src):
  img = image.load_img(src, target_size=(480, 832))
  x = image.img_to_array(img)
  x = np.expand_dims(x, axis=0)
  x = x*(1./255)
  return x
def let_me_see(dir,num):
  src = dir+'/'+num
  x=img2np(src)
  y=model.predict(x)
  y=y*255
  plt.imshow(y[0].squeeze(2))
  save_name ='a/'+num   #directory configure
  plt.savefig(save_name)
  plt.show()


###### example###########
outer_path = 'Val/data_Pic/kite-surf/kite-surf'
folderlist = os.listdir(outer_path)          #列举文件夹
for folder in folderlist:
  let_me_see(outer_path,folder)

# Commented out IPython magic to ensure Python compatibility.
####### functions for online learning ###############
import os
def load_shot(folder,idx):
  outer_path = 'Val/data_Mask'
  folderlist = os.listdir(outer_path)          #列举文件夹
  index='000'+idx+'.png'
  src = os.path.join(outer_path, folder, folder, index)
  dst = os.path.join('Val/data_One_mask',folder,folder,'shot.png')
#   % cp {src} {dst}
  outer_path = 'Val/data_Pic'
  folderlist = os.listdir(outer_path)          #列举文件夹
  index='000'+idx+'.jpg'
  src = os.path.join(outer_path, folder, folder, index)
  dst = os.path.join('Val/data_One_shot',folder,folder,'shot.jpg')
#   % cp {src} {dst}
dict = {'blackswan': 50,
 'bmx-trees': 80,
 'breakdance': 84,
 'camel': 90,
 'car-roundabout': 75,
 'car-shadow': 40,
 'cows': 104,
 'dance-twirl': 90,
 'dog': 60,
 'drift-chicane': 52,
 'drift-straight': 50,
 'goat': 90,
 'horsejump-high': 50,
 'kite-surf': 50,
 'libby': 49,
 'motocross-jump': 40,
 'paragliding-launch': 80,
 'parkour': 100,
 'scooter-black': 43,
 'soapbox': 99}
def combine_generator(gen1, gen2):
      while True:
          yield(gen1.next(), gen2.next()) 
def val_loader(folder):
  image_datagen = ImageDataGenerator(
                                   rescale= 1./255)
  mask_datagen = ImageDataGenerator(rescale= 1./255)
  image_datagen1 = ImageDataGenerator( rotation_range=90,
                   width_shift_range=0.1,
                   height_shift_range=0.1,
                   zoom_range=0.2, horizontal_flip=True,
                   vertical_flip = True, rescale= 1./255)
  mask_datagen1 = ImageDataGenerator( rotation_range=90,
                   width_shift_range=0.1,
                   height_shift_range=0.1,
                   zoom_range=0.2, horizontal_flip=True,
                   vertical_flip = True, rescale= 1./255)
  seed = 1
#path
  one_shot = 'Val/data_One_shot/'+folder
  one_mask = 'Val/data_One_mask/'+folder
  val_pic = 'Val/data_Pic/'+folder
  val_mask = 'Val/data_Mask/'+folder
  image_generator = image_datagen1.flow_from_directory(
      one_shot,target_size=(480,832),
      class_mode=None,batch_size=1,
      seed=1)
  mask_generator = mask_datagen1.flow_from_directory(
      one_mask,target_size=(480,832),
      class_mode=None,batch_size=1,
      color_mode = 'grayscale',
      seed=seed)
  image_generator1 = image_datagen.flow_from_directory(
      val_pic,target_size=(480,832),
      class_mode=None,batch_size=1,
      seed=1)
  mask_generator1 = mask_datagen.flow_from_directory(
      val_mask,target_size=(480,832),
      class_mode=None,batch_size=1,
      color_mode = 'grayscale',
      seed=seed)
#merge two generators 
  train_generator = combine_generator(image_generator, mask_generator)
  val_generator = combine_generator(image_generator1, mask_generator1)
  return train_generator, val_generator