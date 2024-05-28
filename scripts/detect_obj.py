import cv2
import numpy as np
import os
import tensorflow as tf

model = tf.keras.models.load_model('data\\trained_model.h5')

def get_class_names_from_file(filename):
    with open(filename, 'r') as file:
        class_names = [line.strip() for line in file.readlines()]
    return class_names

def detect_objects_f(image_path):
    class_names_file = 'data\class_names.txt'
    class_names = get_class_names_from_file(class_names_file)
    
    image = cv2.imread(image_path)
    image = cv2.resize(image, (224, 224))
    image = np.expand_dims(image, axis=0) / 255.0

    predictions = model.predict(image)

    class_index = np.argmax(predictions[0])
    confidence = predictions[0][class_index]

    object_name = class_names[class_index]

    return object_name, confidence
