"""
Flask web application for Alzheimer's peptide risk prediction demo.
Run:  python app.py
Open: http://localhost:5000
"""

import os
import pickle
import numpy as np
from flask import Flask, render_template, request, jsonify
from tensorflow.keras.preprocessing.sequence import pad_sequences
import tensorflow as tf

app = Flask(__name__)

MODELS_DIR  = 'models'
AMINO_ACIDS = 'ACDEFGHIKLMNPQRSTVWY'
AA_TO_INT   = {aa: i + 1 for i, aa in enumerate(AMINO_ACIDS)}

ML_MODELS = {}   # cached sklearn models
DL_MODELS = {}   # cached keras models
METADATA   = {}


def load_metadata():
    global METADATA
    path = os.path.join(MODELS_DIR, 'metadata.pkl')
    with open(path, 'rb') as f:
        METADATA = pickle.load(f)


def get_ml_model(name: str):
    if name not in ML_MODELS:
        path = os.path.join(MODELS_DIR, f"{name.lower().replace(' ', '_')}.pkl")
        with open(path, 'rb') as f:
            ML_MODELS[name] = pickle.load(f)
    return ML_MODELS[name]


def get_dl_model(name: str):
    if name not in DL_MODELS:
        path = os.path.join(MODELS_DIR, f"{name.lower()}_model.h5")
        DL_MODELS[name] = tf.keras.models.load_model(path)
    return DL_MODELS[name]


def encode_and_predict(sequence: str, model_name: str) -> dict:
    max_length = METADATA['max_length']
    vocab_size = METADATA['vocab_size']

    encoded  = [AA_TO_INT.get(aa, 0) for aa in sequence.upper()]
    X_padded = pad_sequences([encoded], maxlen=max_length, padding='post', value=0)

    if model_name in ('CNN', 'LSTM', 'BiLSTM'):
        model = get_dl_model(model_name)
        prob  = float(model.predict(X_padded, verbose=0)[0][0])
    else:
        model    = get_ml_model(model_name)
        X_onehot = np.zeros((1, max_length * vocab_size))
        for j, aa_idx in enumerate(X_padded[0]):
            if aa_idx > 0:
                X_onehot[0, j * vocab_size + aa_idx] = 1
        prob = float(model.predict_proba(X_onehot)[0][1])

    prediction = 'Amyloid' if prob > 0.5 else 'Non-amyloid'
    risk_level = 'High' if prob > 0.7 else ('Medium' if prob > 0.5 else 'Low')

    return {
        'sequence':    sequence.upper(),
        'model':       model_name,
        'prediction':  prediction,
        'probability': round(prob * 100, 2),
        'risk_level':  risk_level,
    }


@app.route('/')
def index():
    return render_template('index.html', best_model=METADATA.get('best_model', 'CNN'))


@app.route('/predict', methods=['POST'])
def predict():
    data     = request.get_json()
    sequence = data.get('sequence', '').strip()
    model    = data.get('model', 'CNN')

    if not sequence:
        return jsonify({'error': 'No sequence provided'}), 400

    # Validate amino acids
    valid = set(AMINO_ACIDS)
    invalid = [c for c in sequence.upper() if c not in valid]
    if invalid:
        return jsonify({'error': f"Invalid amino acids: {set(invalid)}"}), 400

    result = encode_and_predict(sequence, model)
    return jsonify(result)


if __name__ == '__main__':
    load_metadata()
    print("🧬  Alzheimer Peptide Risk Predictor  —  http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
