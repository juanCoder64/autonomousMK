# Autonomous Mario Kart Driving System

This repository contains code for an autonomous driving system for Mario Kart using computer vision and machine learning. The system uses OpenCV for image processing and a neural network trained with Keras for decision-making. The code is divided into three main files: `mario_kart.py` for running the neural network, capturing and processing game frames, `train_data.py` for training the neural network, and `no_ai.py` for running the autonomous driving system.

## `mario_kart.py`

This Python script captures the game frames using the mss library, processes the images using computer vision techniques, and controls the Mario Kart game through keyboard inputs using inferences by a pretrained model. The key features include:

- Lane detection using color thresholding and contour analysis.
- Detection of item boxes and pipes on the game screen.
- Decision-making based on the position of the player on the lane and the presence of items and pipes.

## `train_data.py`

This script is responsible for training the neural network using pre-recorded gameplay data. It utilizes a dataset (`Ndata.csv`) containing information about the game state (position on the lane, item box presence, pipe presence) and corresponding actions taken by the player. Key functionalities include:

- Loading and preprocessing the dataset.
- Scaling input features using Min-Max scaling.
- Building and tuning a neural network using Keras Tuner.
- Saving the trained model for later use.

## `no_ai.py`

Similar to `mario_kart.py`, this script captures and processes game frames in real-time. However, instead of relying on a pre-trained neural network, it uses predefined rules and logic for decision-making. It serves as a comparison to the autonomous system powered by machine learning.

## Usage

1. Run `train_data.py` to train the neural network and save the model.
2. Run `mario_kart.py` to activate the autonomous driving system using the trained model.
3. Optionally, run `no_ai.py` to compare the performance of the rule-based system.
## Important Adjustments

Before running the scripts, it's crucial to make the following adjustments to ensure compatibility with your specific Mario Kart game setup:

1. **Screen Coordinates:**
   - In both `mario_kart.py` and `no_ai.py`, adjust the `monitor` dictionary to match the coordinates and dimensions of your Mario Kart game window. Update the values for `"top"`, `"left"`, `"width"`, and `"height"` accordingly.

```python
monitor = {"top": 391, "left": 119, "width": 444, "height": 332}
```

2. **Color Thresholds:**
   - Fine-tune the color threshold values in `mario_kart.py` to match the colors of the lanes, item boxes, and pipes in your game. Adjust the values in the `low`, `high`, `tLow`, `tHigh`, `iLow`, and `iHigh` arrays accordingly.

```python
low = np.array([0, 0, 63])
high = np.array([38, 53, 124])
tLow = np.array([53, 173, 108])
tHigh = np.array([56, 202, 255])
iLow = np.array([58, 205, 241])
iHigh = np.array([162, 255, 255])
```

3. **Neural Network Training:**
   - In `train_data.py`, adjust the number of neurons in the layers and other hyperparameters inside the `tunedModel` class based on your dataset and training requirements.

```python
model = Sequential([
    Dense(3, activation='linear', input_shape=(3,)),
    Dense(units=hp.Int("units", min_value=3, max_value=16, step=1), activation='relu'),
    Dense(2, activation='sigmoid'),
])
```

4. **Dataset File:**
   - Ensure that the dataset file (`Ndata.csv`) used in `train_data.py` contains relevant and accurate gameplay data. Adjust the file path if necessary.

```python
df = pd.read_csv('Ndata.csv')
```

Make these adjustments according to your specific game environment to achieve optimal performance with the autonomous driving system. Additionally, experiment with different values and configurations to fine-tune the system for your Mario Kart setup.
**Note:** Ensure that all necessary libraries are installed before running the scripts. You may need to adjust screen coordinates and color threshold values based on your specific game setup.

Feel free to experiment with different models, hyperparameters, and computer vision techniques to enhance the performance of the autonomous driving system.