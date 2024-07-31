from app import create_app
import socket
import logging
import os

# import tensorflow as tf

app = create_app()

# # Load Saved Model
# cwd = os.getcwd()
# PATH_TO_SAVED_MODEL = os.path.join(cwd, "saved_model_v2")

# # Load saved model and build the detection function
# detect_fn = tf.saved_model.load(PATH_TO_SAVED_MODEL)

# logging for error tracking
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

if __name__ == "__main__":
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    print("Running on: ", ip_address)
    app.run(host="0.0.0.0", port=5000, debug=True)
