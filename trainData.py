import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_csv('Ndata.csv')
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from keras.models import Sequential , save_model
from keras.layers import Dense
import joblib

dataset=df.values
x=dataset[:,0:3]
y=dataset[:,3:5]

min_max_scaler = preprocessing.MinMaxScaler()
X_scale = min_max_scaler.fit_transform(x)

joblib.dump(min_max_scaler, 'sc.joblib') 

print(X_scale)
# splits the data into training and testing sets
X_train, X_val_and_test, Y_train, Y_val_and_test = train_test_split(X_scale, y, test_size=0.3)
X_val, X_test, Y_val, Y_test = train_test_split(X_val_and_test, Y_val_and_test, test_size=0.5)

# prepares the model with 3 layers, 2 layers with 3 neurons and 1 layer with 2 neurons 
model = Sequential([
    Dense(3, activation='relu', input_shape=(3,)),
    Dense(3, activation='relu'),
    Dense(2, activation='sigmoid'),
])
# configures the model for training 
model.compile(optimizer='sgd',
              loss='binary_crossentropy',
              metrics=['accuracy'])

# trains the model for a given number of epochs and validates it.
hist = model.fit(X_train, Y_train,
          batch_size=16, epochs=20,
          validation_data=(X_val, Y_val))
# evaluates the model on the test data
model.evaluate(X_test, Y_test)[1]

# plots the training and validation accuracy and loss at each epoch
plt.plot(hist.history['loss'])
plt.plot(hist.history['val_loss'])
plt.title('Model loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Val'], loc='upper right')
plt.show()

# saves the model
filepath = './model'
save_model(model, filepath)
