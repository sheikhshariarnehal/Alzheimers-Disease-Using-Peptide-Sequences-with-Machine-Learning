# 🧬 Alzheimer's Early Detection Using Peptide Sequences

> **DIU Final Year Defence Project**  
> Early detection of Alzheimer's Disease risk from peptide sequences using Machine Learning and Deep Learning.

---

## 📌 Overview

This project predicts whether a peptide sequence is **amyloid-forming** (high Alzheimer's risk) or **non-amyloid** (low risk) by training six different ML/DL models on the [CPAD 2.0](https://web.iitm.ac.in/bioinfo2/cpad2/) database.

| Model | Type | Best for |
|---|---|---|
| Logistic Regression | ML | Baseline, interpretable |
| Random Forest | ML | Feature importance |
| SVM (RBF) | ML | Non-linear boundaries |
| CNN | DL | Local sequence motifs |
| LSTM | DL | Sequential dependencies |
| BiLSTM | DL | Bidirectional context |

---

## 📁 Project Structure

```
Poject/
├── alzheimer_peptide_model.py   # Main training & evaluation pipeline
├── app.py                       # Flask web demo
├── download_peptides.py         # CPAD 2.0 scraper
├── requirements.txt
├── peptides_data.csv            # Dataset (1800+ sequences)
├── models/                      # Saved trained models
│   ├── cnn_model.h5
│   ├── lstm_model.h5
│   ├── bilstm_model.h5
│   ├── logistic_regression.pkl
│   ├── random_forest.pkl
│   ├── svm.pkl
│   └── metadata.pkl
├── results/                     # All output charts & metrics
│   ├── confusion_matrix_*.png   (6 files)
│   ├── training_history_*.png   (3 files)
│   ├── roc_auc_all_models.png
│   ├── model_comparison.png
│   └── metrics_summary.csv
└── templates/
    └── index.html               # Web demo frontend
```

---

## ⚙️ Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. (Optional) Re-download dataset

```bash
python download_peptides.py
```

---

## 🚀 Usage

### Train all models & generate all charts

```bash
python alzheimer_peptide_model.py
```

This will:
- Load and clean `peptides_data.csv`
- Encode peptide sequences (one-hot for ML, padded integers for DL)
- Train ML models with **5-fold cross-validation**
- Train DL models with **proper internal validation split** (10% of train)
- Save confusion matrices, ROC-AUC curves, training history plots to `results/`
- Save all models to `models/`
- Print example predictions

### Run the interactive web demo

```bash
python app.py
```

Then open **http://localhost:5000** in your browser.

---

## 📊 Results

| Model | Accuracy | F1-Score | ROC-AUC |
|---|---:|---:|---:|
| Logistic Regression | ~0.778 | ~0.792 | — |
| Random Forest | ~0.766 | ~0.788 | — |
| SVM | ~0.773 | ~0.787 | — |
| **CNN** | **~0.833** | **~0.848** | — |
| LSTM | ~0.549 | ~0.709 | — |
| BiLSTM | ~0.805 | ~0.812 | — |

> Exact numbers are updated in `results/metrics_summary.csv` after each run.

---

## 🧪 Example Prediction

```
Input  : KLVFFA
Model  : CNN
Output : Amyloid (Alzheimer Risk)
Prob   : 0.87
Risk   : High
```

---

## ⚠️ Limitations

- No independent clinical validation dataset
- LSTM showed high recall but low accuracy (over-predicts positives)
- Results depend on CPAD 2.0 label quality

## 💡 Future Work

- Add external test set (independent clinical data)
- Hyperparameter tuning (grid search / Bayesian)
- Transformer-based sequence model (e.g., ESM-2)
- SHAP/saliency explainability for all models

---

## 👤 Author

**Sheikh Shariar Nehal**  
Daffodil International University (DIU)  
Department of Computer Science & Engineering
