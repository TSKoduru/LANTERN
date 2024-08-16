# IMPORTS
# ------------ 

import flask # To handle the API calls
from flask_cors import CORS, cross_origin # To handle CORS
import open_clip # For the tokenizer
import keras # To load the model
import torch # To generate embeddings

# Base64 and PIL for image processing
from PIL import Image 
from io import BytesIO
import base64

# INITALIZING TOKENIZER AND CLASSIFICATION MODEL
# ------------

CLIP_model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32',
                                       pretrained = 'laion2b_s34b_b79k')
tokenizer = open_clip.get_tokenizer('ViT-B-32')
classification_model = keras.models.load_model('./models/export_model.keras')
print(classification_model.summary())

# DEFINING HELPER METHODS
# ------------

def generate_embedding(base64_image):

    # First, extract the base64 data into a string. Before the first comma,
    # we need to see 'base64'. If not, we return an error.

    first_semicolon = base64_image.find(';')

    if base64_image[first_semicolon + 1: first_semicolon + 7] == 'base64':
        base64_image = base64_image[first_semicolon+8:]
    else:
        # Bad request. Return an error that the user can see.
        flask.abort(400, 'Invalid image data.  Enter data as a base64 string.')

     
    # Load image
    loaded = Image.open(BytesIO(base64.b64decode(base64_image)))
    image = preprocess(loaded).unsqueeze(0)
    with torch.no_grad():
        image_features = CLIP_model.encode_image(image)
    return image_features

def classify_image(base64_image):

    # Get the embedding, and feed it through the classification
    # model that we trained earlier.

    image_features = generate_embedding(base64_image)
    classification = classification_model.predict(
                     image_features.detach().numpy())
    return classification

# INITIALIZING FLASK APP
# ------------

app = flask.Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# DEFINING API ENDPOINTS
# ------------

@app.route('/')
def hello():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LANTERN API</title>
    <link rel="icon" href="./static/logo.png" type="image/x-icon">
    <style>
        body {
            background-color: #peachpuff;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            color: black;
            font-family: monospace;
        }
        .container {
            text-align: center;
        }
        img {
            max-width: 100px; /* Adjust size as needed */
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <img src="./static/logo.png" alt="LANTERN Logo9">
        <h1>LANTERN</h1>
        <p>Made by Teja Koduru</p>
        <hr/>
    </div>
</body>
</html>
"""

@app.route('/classify', methods=['POST'])
@cross_origin()
def classify():
    image = flask.request.json['image']
    classification = classify_image(image)
    return flask.jsonify({'classification': classification.tolist()[0][0]})


# RUNNING THE FLASK APP
# ------------

# For testing, we can run on a local server. We can host it later on
# if we wish to do so.

if __name__ == '__main__':
   app.run(port=5000)