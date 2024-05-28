import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator # type: ignore

 
train_data_dir = 'asd'
 
image_size = (224, 224)
# Количество эпох обучения
epochs = 20
# Размер пакета (batch size)
batch_size = 32

def train_model_f():
    # Создание генератора для аугментации данных
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )

    # Загрузка данных для обучения
    train_generator = train_datagen.flow_from_directory(
        train_data_dir,
        target_size=image_size,
        batch_size=batch_size,
        class_mode='categorical'
    )

    
    base_model = tf.keras.applications.MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

    # Добавление слоев для финальной классификации
    model = tf.keras.models.Sequential([
        base_model,
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dense(512, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(train_generator.num_classes, activation='softmax')
    ])

    # Замораживаем базовую модель
    base_model.trainable = False

    # Компиляция модели
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    # Обучение модели
    model.fit(train_generator, epochs=epochs)

    # Сохранение обученной модели
    model.save('data\\trained_model.h5')


    # Получение списка классов
    class_names = list(train_generator.class_indices.keys())

    # Сохранение списка классов в текстовый файл
    with open('data\class_names.txt', 'w') as f:
        for class_name in class_names:
            print(class_name + '\n')
            f.write(class_name + '\n')

            
 