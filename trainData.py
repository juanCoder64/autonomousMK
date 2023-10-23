import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_csv('Ndata.csv')
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from keras.models import Sequential , save_model
from keras.layers import Dense
import keras_tuner
import joblib

dataset=df.values
x=dataset[:,0:3]
y=dataset[:,3:6]

min_max_scaler = preprocessing.MinMaxScaler()
X_scale = min_max_scaler.fit_transform(x)

joblib.dump(min_max_scaler, 'sc.joblib') 

print(X_scale)
# splits the data into training and testing sets
X_train, X_val_and_test, Y_train, Y_val_and_test = train_test_split(X_scale, y, test_size=0.3)
X_val, X_test, Y_val, Y_test = train_test_split(X_val_and_test, Y_val_and_test, test_size=0.5)
# prepares the model with 3 layers, 2 layers with 3 neurons and 1 layer with 2 neurons 


class tunedModel (keras_tuner.HyperModel):
    def build(self, hp):
        model = Sequential([
            Dense(3, activation='linear', input_shape=(3,)),
            Dense(units=hp.Int("units", min_value=3, max_value=16, step=1), activation='relu'),
            Dense(2, activation='sigmoid'),
        ])
        # configures the model for training 
        model.compile(optimizer='sgd',
            loss='binary_crossentropy',
            metrics=['accuracy'])
        return model
    def fit(self,hp,model,*args,**kwargs):
        return model.fit(*args,batch_size=hp.Int("batchSize",min_value=4,max_value=64,step=8) ,**kwargs)
        


tuner = keras_tuner.RandomSearch(
    hypermodel=tunedModel(), 
    objective="val_accuracy",
    max_trials=10,
    executions_per_trial=2,
    overwrite=True,
    directory="my_dir",
    project_name="helloworld",
)
hp=keras_tuner.HyperParameters()
hypermodel=tunedModel()
tuner.search(X_train, Y_train, epochs=20, validation_data=(X_val, Y_val))
best_hyperparameters = tuner.get_best_hyperparameters(5)[0]
model=hypermodel.build(best_hyperparameters)
print("fitting")
hist=hypermodel.fit(hp,model,X_train, Y_train, validation_data=(X_val, Y_val))
#models = tuner.get_best_models(num_models=2)
#model = models[0]
# Build the model.
# Needed for `Sequential` without specified `input_shape`.
#model.build(input_shape=(None, 28, 28))
#model.summary()

# trains the model for a given number of epochs and validates it.
#hist = model.fit(hp,model,X_train, Y_train,
#           epochs=20,
#          validation_data=(X_val, Y_val))
# evaluates the model on the test data
_, acc=model.evaluate(X_test, Y_test)
print("Accuracy: ", acc)
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
