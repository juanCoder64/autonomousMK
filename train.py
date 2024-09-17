import pandas as pd
import matplotlib.pyplot as plt
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from keras.models import Sequential, save_model
from keras.layers import Dense
import keras_tuner
import joblib

df = pd.read_csv('data.csv')
dataset = df.values
x = dataset[:, 0:3]
y = dataset[:, 3:8]

min_max_scaler = preprocessing.MinMaxScaler()
X_scale = min_max_scaler.fit_transform(x)
joblib.dump(min_max_scaler, '../../AppData/Roaming/JetBrains/PyCharm2024.1/extensions/com.intellij.database/sc.joblib')

print(X_scale)

X_train, X_val_and_test, Y_train, Y_val_and_test = train_test_split(X_scale, y, test_size=0.3)
X_val, X_test, Y_val, Y_test = train_test_split(X_val_and_test, Y_val_and_test, test_size=0.5)

class tunedModel(keras_tuner.HyperModel):
    def build(self, hp):
        model = Sequential([
            Dense(3, activation='linear', input_shape=(3,)),
            Dense(units=hp.Int("units", min_value=3, max_value=16, step=1), activation='relu'),
            Dense(5, activation='sigmoid'),
        ])
        # Configure the model for training
        model.compile(optimizer='sgd',
                      loss='binary_crossentropy',
                      metrics=['accuracy'])
        return model

tuner = keras_tuner.RandomSearch(
    hypermodel=tunedModel(),
    objective="val_accuracy",
    max_trials=10,
    executions_per_trial=2,
    overwrite=True,
    directory="model",
    project_name="autoMK",
)

tuner.search(X_train, Y_train, epochs=20, validation_data=(X_val, Y_val))
best_model = tuner.get_best_models(num_models=1)[0]
hist = best_model.fit(X_train, Y_train,
                      validation_data=(X_val, Y_val),
                      epochs=20)

# Evaluate
_, acc = best_model.evaluate(X_test, Y_test)
print("Accuracy: ", acc)

# Plot
plt.plot(hist.history['loss'])
plt.plot(hist.history['val_loss'])
plt.title('Model loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Val'], loc='upper right')
plt.show()

# Save
filepath = './model/player.keras'
save_model(best_model, filepath)
