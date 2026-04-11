# Viva Study Guide: Alzheimer's Early Detection Using Peptide Sequences

## 1. Project in One Line
This project predicts amyloid tendency from peptide sequences (used as an Alzheimer's risk indicator) using both machine learning and deep learning, then selects the best model by F1-score.

## 2. Files You Should Know
- Main training and inference: [alzheimer_peptide_model.py](alzheimer_peptide_model.py)
- Data collection: [download_peptides.py](download_peptides.py)
- Requirements: [requirements.txt](requirements.txt)
- Run script: [run_model.bat](run_model.bat)
- Comparison figure: [model_comparison.png](model_comparison.png)
- Saved models folder: [models](models)

## 3. End-to-End Pipeline (What You Applied)

### 3.1 Data Collection
- Scraped peptide records from CPAD pages 1 to 68.
- Saved outputs in CSV and XLSX.
- Implemented request timeout and polite delay between pages.

### 3.2 Data Preprocessing
- Loaded dataset and selected only two columns: Peptide and Class.
- Standardized labels to lowercase and mapped them to two classes:
  - amyloid
  - non-amyloid
- Dropped missing rows.
- Removed duplicate peptide sequences.

### 3.3 Feature Engineering
- Amino acid vocabulary used: ACDEFGHIKLMNPQRSTVWY (20 residues).
- Built integer mapping where amino acids map to 1..20 and 0 is used for padding/unknown.
- Padded all sequences to max sequence length (post-padding).
- Created two feature formats:
  - X_padded for deep learning models.
  - X_onehot for classical ML models (position-wise one-hot).
- Encoded labels with LabelEncoder.

### 3.4 Data Split
- Train-test split: 80-20.
- random_state = 42 for reproducibility.
- stratify = y to keep class ratio balanced in train and test.

### 3.5 Models Trained

#### Machine Learning
- Logistic Regression (max_iter=1000)
- Random Forest (n_estimators=100)
- SVM (RBF kernel, probability=True)

#### Deep Learning
- CNN
- LSTM
- BiLSTM

### 3.6 DL Training Settings
- Loss: binary_crossentropy
- Optimizer: adam
- Output activation: sigmoid
- Epochs: 50
- Batch size: 32
- EarlyStopping:
  - monitor = val_loss
  - patience = 5
  - restore_best_weights = True

### 3.7 Evaluation and Model Selection
- Metrics used:
  - Accuracy
  - Precision
  - Recall
  - F1-Score
- Best model chosen by highest F1-score.

### 3.8 Saving and Inference
- Saved ML models as .pkl files.
- Saved DL models as .h5 files.
- Saved metadata (label encoder, max_length, vocab_size, best model).
- Built predict function that:
  - loads metadata
  - encodes and pads input sequence
  - loads selected model
  - outputs probability and risk level

## 4. Final Performance (From model_comparison.png)

| Model | Accuracy | Precision | Recall | F1-Score |
|---|---:|---:|---:|---:|
| Logistic Regression | 0.778 | 0.816 | 0.768 | 0.792 |
| Random Forest | 0.766 | 0.781 | 0.795 | 0.788 |
| SVM | 0.773 | 0.812 | 0.764 | 0.787 |
| CNN | 0.833 | 0.846 | 0.850 | 0.848 |
| LSTM | 0.549 | 0.549 | 1.000 | 0.709 |
| BiLSTM | 0.805 | 0.862 | 0.768 | 0.812 |

Best model in this run: CNN (F1 = 0.848).

## 5. Metric Formulas You Should Memorize

Accuracy = (TP + TN) / (TP + TN + FP + FN)

Precision = TP / (TP + FP)

Recall = TP / (TP + FN)

F1 = 2 * (Precision * Recall) / (Precision + Recall)

## 6. Why F1-Score for Best Model
F1-score balances precision and recall. It is more reliable than accuracy alone when class distributions and error types matter.

## 7. Common Viva Questions and Ready Answers

1. Why use peptide sequence data?
Peptide patterns can capture amyloid tendency and may support lower-cost computational screening compared to only imaging-based methods.

2. Why train both ML and DL models?
To compare simpler baselines and sequence-learning architectures under the same pipeline and identify the strongest performer.

3. Why stratified split?
To keep class proportions consistent in train and test, reducing evaluation bias.

4. Why did CNN outperform others?
CNN can efficiently capture local sequence motifs relevant to amyloid behavior.

5. Why is LSTM recall very high but accuracy low?
It likely over-predicted the positive class, which raises recall but increases false positives.

6. Why sigmoid in output layer?
It outputs probability for binary classification.

7. What does EarlyStopping do?
Stops training when validation loss stops improving and restores best weights, reducing overfitting.

8. How is a new sequence predicted?
Encode sequence -> pad to max_length -> model prediction -> threshold at 0.5 -> risk label.

9. What files are needed for prediction deployment?
Saved model file plus metadata.pkl.

10. What is one strong contribution of your project?
Unified comparison of multiple ML and DL models for peptide-based amyloid risk prediction with reproducible preprocessing and saved inference pipeline.

## 8. Limitations You Should State Honestly
- No external clinical validation dataset.
- No k-fold cross-validation in current version.
- Some imported diagnostics (classification report/confusion matrix) are not used in current script output.
- Test set is also used as validation for DL training, so results should be interpreted carefully.

## 9. Future Improvements (Good to Say in Viva)
- Add independent external test set.
- Add k-fold cross-validation.
- Add confusion matrix and ROC-AUC reporting.
- Tune hyperparameters systematically.
- Add explainability methods (feature importance or saliency) for biological interpretation.

## 10. 60-Second Viva Speech
My project predicts Alzheimer's risk signal from peptide sequences by classifying peptides as amyloid or non-amyloid. I first collected CPAD peptide data, cleaned labels, removed missing and duplicate entries, and encoded sequences into two forms: one-hot vectors for machine learning and padded integer sequences for deep learning. I trained Logistic Regression, Random Forest, SVM, CNN, LSTM, and BiLSTM using an 80-20 stratified split with fixed random seed. I evaluated all models using accuracy, precision, recall, and F1-score, then selected the best model based on F1. In my results, CNN achieved the highest F1-score of 0.848. I also saved all trained models and metadata, and implemented a prediction function that takes a peptide sequence and returns probability plus risk level. Current limitations are lack of external clinical validation and cross-validation, which are planned as next steps.
