"""
Alzheimer's Early Detection Using Peptide Sequences
ML & DL Model Implementation
"""

# High-level workflow:
# 1) Load and clean peptide labels
# 2) Encode sequences for ML and DL
# 3) Train multiple models
# 4) Compare using common metrics
# 5) Save best artifacts for inference

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (Dense, LSTM, Bidirectional, Conv1D, 
                                      MaxPooling1D, Flatten, Dropout, Embedding)
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping

import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import os

# ============================================================
# 1. DATA PREPROCESSING
# ============================================================

def load_and_preprocess_data(filepath):
    """Load and preprocess the peptide dataset"""
    print("=" * 60)
    print("STEP 1: DATA PREPROCESSING")
    print("=" * 60)
    
    # Load data
    df = pd.read_csv(filepath)
    print(f"\n📊 Dataset shape: {df.shape}")
    print(f"📋 Columns: {list(df.columns)}")
    
    # Keep only columns needed by the classifier.
    df = df[['Peptide', 'Class']].copy()
    
    # Normalize class strings so labels are consistent across sources.
    df['Class'] = df['Class'].str.strip().str.lower()
    # Map any amyloid-like label to "amyloid", otherwise "non-amyloid".
    df['Class'] = df['Class'].apply(lambda x: 'amyloid' if 'amyloid' in x and 'non' not in x else 'non-amyloid')
    
    # Remove any rows with missing values
    df = df.dropna()
    
    # Remove duplicate peptides to reduce repeated-sample bias.
    df = df.drop_duplicates(subset=['Peptide'])
    
    print(f"\n✅ After cleaning: {df.shape[0]} samples")
    print(f"\n📈 Class distribution:")
    print(df['Class'].value_counts())
    
    return df


def encode_sequences(df, max_length=None):
    """Encode peptide sequences for ML and DL models"""
    print("\n" + "=" * 60)
    print("STEP 2: FEATURE ENCODING")
    print("=" * 60)
    
    # Standard 20 amino acids; index 0 reserved for padding/unknown tokens.
    amino_acids = 'ACDEFGHIKLMNPQRSTVWY'
    aa_to_int = {aa: i+1 for i, aa in enumerate(amino_acids)}  # 1-20, 0 for padding
    
    # Find max sequence length if not provided
    if max_length is None:
        max_length = df['Peptide'].str.len().max()
    
    print(f"\n📏 Max sequence length: {max_length}")
    
    # Convert each peptide string to integer token IDs.
    def encode_sequence(seq):
        return [aa_to_int.get(aa, 0) for aa in seq.upper()]
    
    sequences = df['Peptide'].apply(encode_sequence).tolist()
    
    # Pad shorter sequences to the same length for batch training.
    X_padded = pad_sequences(sequences, maxlen=max_length, padding='post', value=0)
    
    # Encode labels
    le = LabelEncoder()
    y = le.fit_transform(df['Class'])
    
    print(f"✅ Encoded shape: {X_padded.shape}")
    print(f"✅ Labels: {le.classes_}")
    
    # Build fixed-size one-hot features for classical ML models.
    # Shape: (num_samples, max_length * vocab_size)
    vocab_size = len(amino_acids) + 1  # +1 for padding
    X_onehot = np.zeros((len(X_padded), max_length * vocab_size))
    
    for i, seq in enumerate(X_padded):
        for j, aa_idx in enumerate(seq):
            if aa_idx > 0:  # Skip padding
                # Position-aware one-hot index.
                X_onehot[i, j * vocab_size + aa_idx] = 1
    
    print(f"✅ One-hot shape for ML: {X_onehot.shape}")
    
    return X_padded, X_onehot, y, le, max_length, vocab_size


# ============================================================
# 2. MACHINE LEARNING MODELS
# ============================================================

def train_ml_models(X_train, X_test, y_train, y_test):
    """Train and evaluate ML models"""
    print("\n" + "=" * 60)
    print("STEP 3: MACHINE LEARNING MODELS")
    print("=" * 60)
    
    results = {}
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        # probability=True enables predict_proba for inference consistency.
        'SVM': SVC(kernel='rbf', probability=True, random_state=42)
    }
    
    trained_models = {}
    
    for name, model in models.items():
        print(f"\n🔹 Training {name}...")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        results[name] = {
            'Accuracy': accuracy_score(y_test, y_pred),
            'Precision': precision_score(y_test, y_pred),
            'Recall': recall_score(y_test, y_pred),
            'F1-Score': f1_score(y_test, y_pred)
        }
        
        trained_models[name] = model
        
        print(f"   Accuracy: {results[name]['Accuracy']:.4f}")
        print(f"   Precision: {results[name]['Precision']:.4f}")
        print(f"   Recall: {results[name]['Recall']:.4f}")
        print(f"   F1-Score: {results[name]['F1-Score']:.4f}")
    
    return results, trained_models


# ============================================================
# 3. DEEP LEARNING MODELS
# ============================================================

def build_cnn_model(max_length, vocab_size, embedding_dim=64):
    """Build CNN model for sequence classification"""
    # CNN captures local motif patterns in peptide sequences.
    model = Sequential([
        Embedding(vocab_size, embedding_dim, input_length=max_length),
        Conv1D(128, 3, activation='relu'),
        MaxPooling1D(2),
        Conv1D(64, 3, activation='relu'),
        MaxPooling1D(2),
        Flatten(),
        Dense(64, activation='relu'),
        Dropout(0.5),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model


def build_lstm_model(max_length, vocab_size, embedding_dim=64):
    """Build LSTM model for sequence classification"""
    # Stacked LSTMs learn sequential dependencies from left to right.
    model = Sequential([
        Embedding(vocab_size, embedding_dim, input_length=max_length),
        LSTM(128, return_sequences=True),
        LSTM(64),
        Dense(64, activation='relu'),
        Dropout(0.5),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model


def build_bilstm_model(max_length, vocab_size, embedding_dim=64):
    """Build Bidirectional LSTM model for sequence classification"""
    # BiLSTM reads sequence in both forward and backward directions.
    model = Sequential([
        Embedding(vocab_size, embedding_dim, input_length=max_length),
        Bidirectional(LSTM(128, return_sequences=True)),
        Bidirectional(LSTM(64)),
        Dense(64, activation='relu'),
        Dropout(0.5),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model


def train_dl_models(X_train, X_test, y_train, y_test, max_length, vocab_size):
    """Train and evaluate DL models"""
    print("\n" + "=" * 60)
    print("STEP 4: DEEP LEARNING MODELS")
    print("=" * 60)
    
    results = {}
    trained_models = {}
    
    # Stop when validation loss stops improving to reduce overfitting.
    early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    
    dl_models = {
        'CNN': build_cnn_model(max_length, vocab_size),
        'LSTM': build_lstm_model(max_length, vocab_size),
        'BiLSTM': build_bilstm_model(max_length, vocab_size)
    }
    
    for name, model in dl_models.items():
        print(f"\n🔹 Training {name}...")
        print(f"   Model parameters: {model.count_params():,}")
        
        history = model.fit(
            X_train, y_train,
            # Reuse held-out split as validation for this compact pipeline.
            validation_data=(X_test, y_test),
            epochs=50,
            batch_size=32,
            callbacks=[early_stop],
            verbose=0
        )
        
        # Convert probability output to class label using 0.5 decision threshold.
        y_pred_prob = model.predict(X_test, verbose=0)
        y_pred = (y_pred_prob > 0.5).astype(int).flatten()
        
        results[name] = {
            'Accuracy': accuracy_score(y_test, y_pred),
            'Precision': precision_score(y_test, y_pred),
            'Recall': recall_score(y_test, y_pred),
            'F1-Score': f1_score(y_test, y_pred)
        }
        
        trained_models[name] = model
        
        print(f"   Accuracy: {results[name]['Accuracy']:.4f}")
        print(f"   Precision: {results[name]['Precision']:.4f}")
        print(f"   Recall: {results[name]['Recall']:.4f}")
        print(f"   F1-Score: {results[name]['F1-Score']:.4f}")
    
    return results, trained_models


# ============================================================
# 4. MODEL COMPARISON & VISUALIZATION
# ============================================================

def compare_models(ml_results, dl_results, save_path='model_comparison.png'):
    """Compare and visualize all model results"""
    print("\n" + "=" * 60)
    print("STEP 5: MODEL COMPARISON")
    print("=" * 60)
    
    # Combine results
    all_results = {**ml_results, **dl_results}
    
    # Create comparison DataFrame
    comparison_df = pd.DataFrame(all_results).T
    comparison_df = comparison_df.round(4)
    
    print("\n📊 Model Comparison:")
    print("-" * 60)
    print(comparison_df.to_string())
    
    # Pick best model by highest F1-score.
    best_model = comparison_df['F1-Score'].idxmax()
    best_f1 = comparison_df.loc[best_model, 'F1-Score']
    
    print(f"\n🏆 Best Model: {best_model} (F1-Score: {best_f1:.4f})")
    
    # Plot both chart styles to make comparison easier in reports/viva.
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Bar plot
    comparison_df.plot(kind='bar', ax=axes[0], rot=45)
    axes[0].set_title('Model Performance Comparison', fontsize=14)
    axes[0].set_ylabel('Score')
    axes[0].legend(loc='lower right')
    axes[0].set_ylim(0, 1)
    
    # Heatmap
    sns.heatmap(comparison_df, annot=True, cmap='YlGnBu', fmt='.3f', ax=axes[1])
    axes[1].set_title('Performance Metrics Heatmap', fontsize=14)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\n📈 Comparison plot saved: {save_path}")
    
    return comparison_df, best_model


def save_models(ml_models, dl_models, le, max_length, vocab_size, best_model_name):
    """Save trained models"""
    print("\n" + "=" * 60)
    print("SAVING MODELS")
    print("=" * 60)
    
    # Create models directory
    os.makedirs('models', exist_ok=True)
    
    # Save classical ML models as pickle files.
    for name, model in ml_models.items():
        filepath = f'models/{name.lower().replace(" ", "_")}.pkl'
        with open(filepath, 'wb') as f:
            pickle.dump(model, f)
        print(f"✅ Saved: {filepath}")
    
    # Save deep learning models in Keras H5 format.
    for name, model in dl_models.items():
        filepath = f'models/{name.lower()}_model.h5'
        model.save(filepath)
        print(f"✅ Saved: {filepath}")
    
    # Metadata is required to encode future input exactly like training.
    metadata = {
        'label_encoder': le,
        'max_length': max_length,
        'vocab_size': vocab_size,
        'best_model': best_model_name
    }
    with open('models/metadata.pkl', 'wb') as f:
        pickle.dump(metadata, f)
    print(f"✅ Saved: models/metadata.pkl")


# ============================================================
# 5. PREDICTION FUNCTION
# ============================================================

def predict_alzheimer_risk(sequence, model_name='Random Forest'):
    """
    Predict Alzheimer risk for a given peptide sequence
    
    Args:
        sequence: Peptide sequence string (e.g., 'KLVFFA')
        model_name: Model to use for prediction
    
    Returns:
        dict: Prediction result with probability
    """
    # Load metadata
    with open('models/metadata.pkl', 'rb') as f:
        metadata = pickle.load(f)
    
    le = metadata['label_encoder']
    max_length = metadata['max_length']
    vocab_size = metadata['vocab_size']
    
    # Encode incoming peptide with same vocabulary used at train time.
    amino_acids = 'ACDEFGHIKLMNPQRSTVWY'
    aa_to_int = {aa: i+1 for i, aa in enumerate(amino_acids)}
    
    encoded = [aa_to_int.get(aa, 0) for aa in sequence.upper()]
    X_padded = pad_sequences([encoded], maxlen=max_length, padding='post', value=0)
    
    # Route prediction based on model family (DL vs ML).
    if model_name in ['CNN', 'LSTM', 'BiLSTM']:
        model = tf.keras.models.load_model(f'models/{model_name.lower()}_model.h5')
        prob = model.predict(X_padded, verbose=0)[0][0]
    else:
        with open(f'models/{model_name.lower().replace(" ", "_")}.pkl', 'rb') as f:
            model = pickle.load(f)
        # Recreate one-hot vector because ML models were trained on one-hot features.
        X_onehot = np.zeros((1, max_length * vocab_size))
        for j, aa_idx in enumerate(X_padded[0]):
            if aa_idx > 0:
                X_onehot[0, j * vocab_size + aa_idx] = 1
        prob = model.predict_proba(X_onehot)[0][1]
    
    # Binary decision threshold and user-friendly risk bucketing.
    prediction = 'Amyloid (Alzheimer Risk)' if prob > 0.5 else 'Non-amyloid (Low Risk)'
    
    return {
        'sequence': sequence,
        'prediction': prediction,
        'probability': float(prob),
        'risk_level': 'High' if prob > 0.7 else 'Medium' if prob > 0.5 else 'Low'
    }


# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    print("\n" + "=" * 60)
    print("🧬 ALZHEIMER'S EARLY DETECTION USING PEPTIDE SEQUENCES")
    print("=" * 60)
    
    # 1. Load and preprocess data
    df = load_and_preprocess_data('peptides_data.csv')
    
    # 2. Encode sequences
    X_padded, X_onehot, y, le, max_length, vocab_size = encode_sequences(df)
    
    # 3. Split data once, then feed each model family with its matching feature format.
    X_train_padded, X_test_padded, y_train, y_test = train_test_split(
        X_padded, y, test_size=0.2, random_state=42, stratify=y
    )
    
    X_train_onehot, X_test_onehot, _, _ = train_test_split(
        X_onehot, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\n📊 Train size: {len(X_train_padded)}, Test size: {len(X_test_padded)}")
    
    # 4. Train ML models
    ml_results, ml_models = train_ml_models(X_train_onehot, X_test_onehot, y_train, y_test)
    
    # 5. Train DL models
    dl_results, dl_models = train_dl_models(
        X_train_padded, X_test_padded, y_train, y_test, max_length, vocab_size
    )
    
    # 6. Compare models
    comparison_df, best_model = compare_models(ml_results, dl_results)
    
    # 7. Save models
    save_models(ml_models, dl_models, le, max_length, vocab_size, best_model)
    
    # 8. Test prediction
    print("\n" + "=" * 60)
    print("EXAMPLE PREDICTIONS")
    print("=" * 60)
    
    test_sequences = ['KLVFFA', 'GVVIA', 'AAAQAA', 'FGAIL']
    
    for seq in test_sequences:
        result = predict_alzheimer_risk(seq, best_model)
        print(f"\n🧬 Sequence: {result['sequence']}")
        print(f"   Prediction: {result['prediction']}")
        print(f"   Probability: {result['probability']:.4f}")
        print(f"   Risk Level: {result['risk_level']}")
    
    print("\n" + "=" * 60)
    print("✅ MODEL TRAINING COMPLETE!")
    print("=" * 60)
    
    return comparison_df, best_model


if __name__ == "__main__":
    comparison_df, best_model = main()
