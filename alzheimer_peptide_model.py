"""
Alzheimer's Early Detection Using Peptide Sequences
ML & DL Model Implementation — Final Version
=====================================================
Pipeline:
  1) Load and clean peptide labels
  2) Encode sequences for ML and DL
  3) Train ML models with 5-fold cross-validation
  4) Train DL models with proper validation split
  5) Evaluate: Accuracy, Precision, Recall, F1, ROC-AUC
  6) Save confusion matrices, ROC curves, training history
  7) Save best model artifacts for inference
"""

import pandas as pd
import numpy as np
import warnings
import os
import pickle

warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    roc_curve
)
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Dense, LSTM, Bidirectional, Conv1D,
    MaxPooling1D, Flatten, Dropout, Embedding
)
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import EarlyStopping

import matplotlib
matplotlib.use('Agg')   # non-interactive backend for saving figures
import matplotlib.pyplot as plt
import seaborn as sns

# ─────────────────────────────────────────────────────────────
# GLOBAL STYLE
# ─────────────────────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor': '#0d1117',
    'axes.facecolor':   '#161b22',
    'axes.edgecolor':   '#30363d',
    'axes.labelcolor':  '#c9d1d9',
    'xtick.color':      '#c9d1d9',
    'ytick.color':      '#c9d1d9',
    'text.color':       '#c9d1d9',
    'grid.color':       '#21262d',
    'font.family':      'DejaVu Sans',
})

RESULTS_DIR = 'results'
MODELS_DIR  = 'models'
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(MODELS_DIR,  exist_ok=True)


# ─────────────────────────────────────────────────────────────
# 1. DATA PREPROCESSING
# ─────────────────────────────────────────────────────────────

def load_and_preprocess_data(filepath: str) -> pd.DataFrame:
    """Load and preprocess the peptide dataset."""
    print("=" * 60)
    print("STEP 1: DATA PREPROCESSING")
    print("=" * 60)

    df = pd.read_csv(filepath)
    print(f"\n📊 Dataset shape: {df.shape}")
    print(f"📋 Columns: {list(df.columns)}")

    df = df[['Peptide', 'Class']].copy()

    # Normalise class labels
    df['Class'] = df['Class'].str.strip().str.lower()
    df['Class'] = df['Class'].apply(
        lambda x: 'amyloid' if ('amyloid' in x and 'non' not in x) else 'non-amyloid'
    )

    df = df.dropna()
    df = df.drop_duplicates(subset=['Peptide'])

    print(f"\n✅ After cleaning: {df.shape[0]} samples")
    print(f"\n📈 Class distribution:")
    print(df['Class'].value_counts())

    return df


# ─────────────────────────────────────────────────────────────
# 2. FEATURE ENCODING
# ─────────────────────────────────────────────────────────────

def encode_sequences(df: pd.DataFrame, max_length: int = None):
    """Encode peptide sequences for both ML and DL models."""
    print("\n" + "=" * 60)
    print("STEP 2: FEATURE ENCODING")
    print("=" * 60)

    amino_acids = 'ACDEFGHIKLMNPQRSTVWY'
    aa_to_int   = {aa: i + 1 for i, aa in enumerate(amino_acids)}

    if max_length is None:
        max_length = df['Peptide'].str.len().max()

    print(f"\n📏 Max sequence length: {max_length}")

    def encode_seq(seq):
        return [aa_to_int.get(aa, 0) for aa in seq.upper()]

    sequences = df['Peptide'].apply(encode_seq).tolist()
    X_padded  = pad_sequences(sequences, maxlen=max_length, padding='post', value=0)

    le = LabelEncoder()
    y  = le.fit_transform(df['Class'])

    print(f"✅ Encoded shape: {X_padded.shape}")
    print(f"✅ Labels: {le.classes_}")

    # Position-aware one-hot for classical ML
    vocab_size = len(amino_acids) + 1
    X_onehot   = np.zeros((len(X_padded), max_length * vocab_size))
    for i, seq in enumerate(X_padded):
        for j, aa_idx in enumerate(seq):
            if aa_idx > 0:
                X_onehot[i, j * vocab_size + aa_idx] = 1

    print(f"✅ One-hot shape for ML: {X_onehot.shape}")
    return X_padded, X_onehot, y, le, max_length, vocab_size


# ─────────────────────────────────────────────────────────────
# 3. MACHINE LEARNING MODELS  (5-fold cross-validation)
# ─────────────────────────────────────────────────────────────

def train_ml_models(X_onehot: np.ndarray, y: np.ndarray,
                    X_test: np.ndarray, y_test: np.ndarray):
    """Train ML models with 5-fold CV and evaluate on held-out test set."""
    print("\n" + "=" * 60)
    print("STEP 3: MACHINE LEARNING MODELS  (5-Fold CV)")
    print("=" * 60)

    models_def = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Random Forest':       RandomForestClassifier(n_estimators=100, random_state=42),
        'SVM':                 SVC(kernel='rbf', probability=True, random_state=42),
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scoring = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']

    results        = {}
    trained_models = {}

    for name, model in models_def.items():
        print(f"\n🔹 {name}  —  5-fold CV …")
        cv_scores = cross_validate(model, X_onehot, y, cv=cv,
                                   scoring=cv_scoring, return_train_score=False)

        # Final fit on full training split, evaluate on test
        model.fit(X_onehot, y)
        y_pred      = model.predict(X_test)
        y_prob      = model.predict_proba(X_test)[:, 1]

        results[name] = {
            'Accuracy':  accuracy_score(y_test, y_pred),
            'Precision': precision_score(y_test, y_pred, zero_division=0),
            'Recall':    recall_score(y_test, y_pred, zero_division=0),
            'F1-Score':  f1_score(y_test, y_pred, zero_division=0),
            'ROC-AUC':   roc_auc_score(y_test, y_prob),
            'CV_Accuracy_Mean': cv_scores['test_accuracy'].mean(),
            'CV_Accuracy_Std':  cv_scores['test_accuracy'].std(),
            'CV_F1_Mean':       cv_scores['test_f1'].mean(),
            'CV_F1_Std':        cv_scores['test_f1'].std(),
            'y_prob': y_prob,
        }

        trained_models[name] = model

        print(f"   Test  Accuracy : {results[name]['Accuracy']:.4f}")
        print(f"   Test  Precision: {results[name]['Precision']:.4f}")
        print(f"   Test  Recall   : {results[name]['Recall']:.4f}")
        print(f"   Test  F1-Score : {results[name]['F1-Score']:.4f}")
        print(f"   Test  ROC-AUC  : {results[name]['ROC-AUC']:.4f}")
        print(f"   CV    Accuracy : {results[name]['CV_Accuracy_Mean']:.4f} "
              f"± {results[name]['CV_Accuracy_Std']:.4f}")
        print(f"   CV    F1-Score : {results[name]['CV_F1_Mean']:.4f} "
              f"± {results[name]['CV_F1_Std']:.4f}")

        # Confusion matrix
        _save_confusion_matrix(y_test, y_pred, name)
        print(f"\n📄 Classification Report — {name}:")
        print(classification_report(y_test, y_pred,
                                    target_names=['Non-amyloid', 'Amyloid']))

    return results, trained_models


# ─────────────────────────────────────────────────────────────
# 4. DEEP LEARNING MODELS
# ─────────────────────────────────────────────────────────────

def _build_cnn(max_length, vocab_size, embedding_dim=64):
    model = Sequential([
        Embedding(vocab_size, embedding_dim, input_length=max_length),
        Conv1D(128, 3, activation='relu'),
        MaxPooling1D(2),
        Conv1D(64, 3, activation='relu'),
        MaxPooling1D(2),
        Flatten(),
        Dense(64, activation='relu'),
        Dropout(0.5),
        Dense(1, activation='sigmoid'),
    ], name='CNN')
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model


def _build_lstm(max_length, vocab_size, embedding_dim=64):
    model = Sequential([
        Embedding(vocab_size, embedding_dim, input_length=max_length),
        LSTM(128, return_sequences=True),
        LSTM(64),
        Dense(64, activation='relu'),
        Dropout(0.5),
        Dense(1, activation='sigmoid'),
    ], name='LSTM')
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model


def _build_bilstm(max_length, vocab_size, embedding_dim=64):
    model = Sequential([
        Embedding(vocab_size, embedding_dim, input_length=max_length),
        Bidirectional(LSTM(128, return_sequences=True)),
        Bidirectional(LSTM(64)),
        Dense(64, activation='relu'),
        Dropout(0.5),
        Dense(1, activation='sigmoid'),
    ], name='BiLSTM')
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model


def train_dl_models(X_train: np.ndarray, X_test: np.ndarray,
                    y_train: np.ndarray, y_test: np.ndarray,
                    max_length: int, vocab_size: int):
    """Train DL models with a proper internal val split (10 % of train)."""
    print("\n" + "=" * 60)
    print("STEP 4: DEEP LEARNING MODELS")
    print("=" * 60)

    # Carve out 10 % of train as validation — test set stays untouched
    X_tr, X_val, y_tr, y_val = train_test_split(
        X_train, y_train, test_size=0.10, random_state=42, stratify=y_train
    )

    early_stop = EarlyStopping(monitor='val_loss', patience=5,
                               restore_best_weights=True)

    dl_builders = {
        'CNN':    _build_cnn,
        'LSTM':   _build_lstm,
        'BiLSTM': _build_bilstm,
    }

    results        = {}
    trained_models = {}

    for name, builder in dl_builders.items():
        print(f"\n🔹 Training {name} …")
        model = builder(max_length, vocab_size)
        print(f"   Parameters: {model.count_params():,}")

        history = model.fit(
            X_tr, y_tr,
            validation_data=(X_val, y_val),
            epochs=50,
            batch_size=32,
            callbacks=[early_stop],
            verbose=0,
        )

        y_prob = model.predict(X_test, verbose=0).flatten()
        y_pred = (y_prob > 0.5).astype(int)

        results[name] = {
            'Accuracy':  accuracy_score(y_test, y_pred),
            'Precision': precision_score(y_test, y_pred, zero_division=0),
            'Recall':    recall_score(y_test, y_pred, zero_division=0),
            'F1-Score':  f1_score(y_test, y_pred, zero_division=0),
            'ROC-AUC':   roc_auc_score(y_test, y_prob),
            'CV_Accuracy_Mean': None,
            'CV_Accuracy_Std':  None,
            'CV_F1_Mean':       None,
            'CV_F1_Std':        None,
            'y_prob': y_prob,
        }

        trained_models[name] = model

        print(f"   Accuracy : {results[name]['Accuracy']:.4f}")
        print(f"   Precision: {results[name]['Precision']:.4f}")
        print(f"   Recall   : {results[name]['Recall']:.4f}")
        print(f"   F1-Score : {results[name]['F1-Score']:.4f}")
        print(f"   ROC-AUC  : {results[name]['ROC-AUC']:.4f}")

        _save_confusion_matrix(y_test, y_pred, name)
        _save_training_history(history, name)

        print(f"\n📄 Classification Report — {name}:")
        print(classification_report(y_test, y_pred,
                                    target_names=['Non-amyloid', 'Amyloid']))

    return results, trained_models


# ─────────────────────────────────────────────────────────────
# 5. VISUALISATIONS
# ─────────────────────────────────────────────────────────────

PALETTE = ['#58a6ff', '#3fb950', '#f78166', '#d2a8ff', '#ffa657', '#79c0ff']


def _save_confusion_matrix(y_true, y_pred, model_name: str):
    cm   = confusion_matrix(y_true, y_pred)
    safe = model_name.lower().replace(' ', '_')

    fig, ax = plt.subplots(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Non-amyloid', 'Amyloid'],
                yticklabels=['Non-amyloid', 'Amyloid'],
                ax=ax, cbar=False,
                annot_kws={'size': 14, 'color': 'white'})
    ax.set_title(f'Confusion Matrix — {model_name}', fontsize=13, pad=10)
    ax.set_xlabel('Predicted', fontsize=11)
    ax.set_ylabel('Actual',    fontsize=11)

    path = os.path.join(RESULTS_DIR, f'confusion_matrix_{safe}.png')
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"   💾 Saved confusion matrix → {path}")


def _save_training_history(history, model_name: str):
    safe = model_name.lower().replace(' ', '_')
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    for ax, metric, title in zip(
        axes,
        [('accuracy', 'val_accuracy'), ('loss', 'val_loss')],
        ['Accuracy', 'Loss']
    ):
        ax.plot(history.history[metric[0]],  color='#58a6ff', label='Train', linewidth=2)
        ax.plot(history.history[metric[1]], color='#f78166', label='Val',   linewidth=2, linestyle='--')
        ax.set_title(f'{model_name} — {title}', fontsize=12)
        ax.set_xlabel('Epoch')
        ax.set_ylabel(title)
        ax.legend()
        ax.grid(True, alpha=0.3)

    fig.suptitle(f'Training History — {model_name}', fontsize=14, y=1.01)
    fig.tight_layout()
    path = os.path.join(RESULTS_DIR, f'training_history_{safe}.png')
    fig.savefig(path, dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"   💾 Saved training history → {path}")


def plot_roc_curves(all_results: dict, y_test: np.ndarray):
    """Plot ROC curves for all models on a single figure."""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot([0, 1], [0, 1], 'k--', alpha=0.4, linewidth=1)

    for (name, res), colour in zip(all_results.items(), PALETTE):
        fpr, tpr, _ = roc_curve(y_test, res['y_prob'])
        auc = res['ROC-AUC']
        ax.plot(fpr, tpr, colour, linewidth=2, label=f"{name}  (AUC={auc:.3f})")

    ax.set_title('ROC-AUC Curves — All Models', fontsize=14)
    ax.set_xlabel('False Positive Rate', fontsize=12)
    ax.set_ylabel('True Positive Rate',  fontsize=12)
    ax.legend(loc='lower right', fontsize=9)
    ax.grid(True, alpha=0.3)

    path = os.path.join(RESULTS_DIR, 'roc_auc_all_models.png')
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"\n📈 Saved ROC-AUC plot → {path}")


def compare_models(all_results: dict) -> pd.DataFrame:
    """Bar-chart + heatmap comparison of all models."""
    print("\n" + "=" * 60)
    print("STEP 5: MODEL COMPARISON")
    print("=" * 60)

    metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC']
    rows    = {n: {m: r[m] for m in metrics} for n, r in all_results.items()}
    df      = pd.DataFrame(rows).T.round(4)

    print("\n📊 Model Comparison:")
    print("-" * 60)
    print(df.to_string())

    best_model = df['F1-Score'].idxmax()
    print(f"\n🏆 Best Model: {best_model} (F1 = {df.loc[best_model,'F1-Score']:.4f})")

    # ── Bar chart ──────────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))

    x    = np.arange(len(df))
    w    = 0.15
    cols = PALETTE

    for i, (metric, colour) in enumerate(zip(metrics, cols)):
        axes[0].bar(x + i * w, df[metric], w, label=metric, color=colour, alpha=0.85)

    axes[0].set_xticks(x + w * 2)
    axes[0].set_xticklabels(df.index, rotation=30, ha='right', fontsize=9)
    axes[0].set_ylim(0, 1.05)
    axes[0].set_title('Model Performance Comparison', fontsize=13)
    axes[0].set_ylabel('Score')
    axes[0].legend(loc='lower right', fontsize=8)
    axes[0].grid(axis='y', alpha=0.3)

    # ── Heatmap ────────────────────────────────────────────────
    sns.heatmap(df, annot=True, cmap='YlGnBu', fmt='.3f',
                ax=axes[1], linewidths=0.5)
    axes[1].set_title('Performance Metrics Heatmap', fontsize=13)

    fig.tight_layout()
    path = os.path.join(RESULTS_DIR, 'model_comparison.png')
    fig.savefig(path, dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"📈 Saved model comparison → {path}")

    # Also save a copy at root for backward-compatibility
    import shutil
    shutil.copy(path, 'model_comparison.png')

    # Metrics CSV
    csv_path = os.path.join(RESULTS_DIR, 'metrics_summary.csv')
    df.to_csv(csv_path)
    print(f"📊 Saved metrics CSV → {csv_path}")

    return df, best_model


# ─────────────────────────────────────────────────────────────
# 6. SAVE MODELS
# ─────────────────────────────────────────────────────────────

def save_models(ml_models, dl_models, le, max_length, vocab_size, best_model_name):
    print("\n" + "=" * 60)
    print("SAVING MODELS")
    print("=" * 60)

    for name, model in ml_models.items():
        path = os.path.join(MODELS_DIR, f"{name.lower().replace(' ', '_')}.pkl")
        with open(path, 'wb') as f:
            pickle.dump(model, f)
        print(f"✅ {path}")

    for name, model in dl_models.items():
        path = os.path.join(MODELS_DIR, f"{name.lower()}_model.h5")
        model.save(path)
        print(f"✅ {path}")

    metadata = {
        'label_encoder': le,
        'max_length':    max_length,
        'vocab_size':    vocab_size,
        'best_model':    best_model_name,
    }
    meta_path = os.path.join(MODELS_DIR, 'metadata.pkl')
    with open(meta_path, 'wb') as f:
        pickle.dump(metadata, f)
    print(f"✅ {meta_path}")


# ─────────────────────────────────────────────────────────────
# 7. PREDICTION
# ─────────────────────────────────────────────────────────────

def predict_alzheimer_risk(sequence: str, model_name: str = 'Random Forest') -> dict:
    """
    Predict Alzheimer risk for a single peptide sequence.

    Args:
        sequence   : Peptide string, e.g. 'KLVFFA'
        model_name : One of 'Logistic Regression', 'Random Forest', 'SVM',
                     'CNN', 'LSTM', 'BiLSTM'
    Returns:
        dict with sequence, prediction, probability, risk_level
    """
    meta_path = os.path.join(MODELS_DIR, 'metadata.pkl')
    with open(meta_path, 'rb') as f:
        metadata = pickle.load(f)

    le         = metadata['label_encoder']
    max_length = metadata['max_length']
    vocab_size = metadata['vocab_size']

    amino_acids = 'ACDEFGHIKLMNPQRSTVWY'
    aa_to_int   = {aa: i + 1 for i, aa in enumerate(amino_acids)}

    encoded  = [aa_to_int.get(aa, 0) for aa in sequence.upper()]
    X_padded = pad_sequences([encoded], maxlen=max_length, padding='post', value=0)

    if model_name in ('CNN', 'LSTM', 'BiLSTM'):
        model_path = os.path.join(MODELS_DIR, f"{model_name.lower()}_model.h5")
        model = tf.keras.models.load_model(model_path)
        prob  = float(model.predict(X_padded, verbose=0)[0][0])
    else:
        model_path = os.path.join(MODELS_DIR,
                                  f"{model_name.lower().replace(' ', '_')}.pkl")
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        X_onehot = np.zeros((1, max_length * vocab_size))
        for j, aa_idx in enumerate(X_padded[0]):
            if aa_idx > 0:
                X_onehot[0, j * vocab_size + aa_idx] = 1
        prob = float(model.predict_proba(X_onehot)[0][1])

    prediction = 'Amyloid (Alzheimer Risk)' if prob > 0.5 else 'Non-amyloid (Low Risk)'
    risk_level = 'High' if prob > 0.7 else ('Medium' if prob > 0.5 else 'Low')

    return {
        'sequence':   sequence,
        'prediction': prediction,
        'probability': prob,
        'risk_level':  risk_level,
    }


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 60)
    print("🧬 ALZHEIMER'S EARLY DETECTION USING PEPTIDE SEQUENCES")
    print("=" * 60)

    # 1. Load data
    df = load_and_preprocess_data('peptides_data.csv')

    # 2. Encode
    X_padded, X_onehot, y, le, max_length, vocab_size = encode_sequences(df)

    # 3. Train / test split (80 / 20)
    X_tr_pad,  X_te_pad,  y_train, y_test = train_test_split(
        X_padded, y, test_size=0.20, random_state=42, stratify=y
    )
    X_tr_oh,   X_te_oh,   _,       _      = train_test_split(
        X_onehot, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"\n📊 Train: {len(X_tr_pad)}  |  Test: {len(X_te_pad)}")

    # 4. ML (cross-validated + test evaluation)
    ml_results, ml_models = train_ml_models(X_tr_oh, y_train, X_te_oh, y_test)

    # 5. DL (proper internal val split)
    dl_results, dl_models = train_dl_models(
        X_tr_pad, X_te_pad, y_train, y_test, max_length, vocab_size
    )

    # 6. Compare
    all_results            = {**ml_results, **dl_results}
    comparison_df, best_model = compare_models(all_results)

    # 7. ROC curves
    plot_roc_curves(all_results, y_test)

    # 8. Save models
    save_models(ml_models, dl_models, le, max_length, vocab_size, best_model)

    # 9. Example predictions
    print("\n" + "=" * 60)
    print("EXAMPLE PREDICTIONS")
    print("=" * 60)
    for seq in ['KLVFFA', 'GVVIA', 'AAAQAA', 'FGAIL']:
        r = predict_alzheimer_risk(seq, best_model)
        print(f"\n🧬 {r['sequence']}")
        print(f"   Prediction : {r['prediction']}")
        print(f"   Probability: {r['probability']:.4f}")
        print(f"   Risk Level : {r['risk_level']}")

    print("\n" + "=" * 60)
    print("✅ ALL DONE!")
    print("=" * 60)
    return comparison_df, best_model


if __name__ == '__main__':
    comparison_df, best_model = main()
