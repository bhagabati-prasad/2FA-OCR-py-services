import os
import tensorflow as tf


def load_saved_models():
    # Load Saved Model
    cwd = os.getcwd()
    PATH_TO_SAVED_MODEL = os.path.join(cwd, "saved_model_v2")

    # Load saved model and build the detection function
    detect_fn = tf.saved_model.load(PATH_TO_SAVED_MODEL)
    return detect_fn
