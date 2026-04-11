# Alzheimer Peptide Project - Study Notes

## Everything Applied (End-to-End)

1. Data collection:
   - Scraped peptide records from CPAD pages 1 to 68 using requests + BeautifulSoup.
   - Saved outputs as CSV and XLSX.

2. Data loading:
   - Loaded peptide dataset from `peptides_data.csv`.

3. Column selection:
   - Kept only `Peptide` and `Class` for modeling.

4. Label cleaning:
   - Converted class labels to lowercase and stripped whitespace.
   - Mapped labels to two classes: `amyloid` and `non-amyloid`.

5. Missing value handling:
   - Dropped rows with missing values.

6. Duplicate handling:
   - Removed duplicate peptide sequences.

7. Amino acid encoding setup:
   - Used standard amino acid vocabulary: `ACDEFGHIKLMNPQRSTVWY`.
   - Mapped amino acids to integers 1-20.
   - Reserved index 0 for padding/unknown.

8. Sequence preprocessing:
   - Integer-encoded each peptide sequence.
   - Padded all sequences to a common max length (post-padding).

9. Label encoding:
   - Used LabelEncoder to convert target class labels to numeric form.

10. Dual feature generation:
    - Built `X_padded` for deep learning.
    - Built position-aware one-hot features (`X_onehot`) for machine learning.

11. Data split:
    - 80/20 train-test split.
    - Used `stratify=y` to preserve class balance.
    - Used `random_state=42` for reproducibility.

12. Machine learning models trained:
    - Logistic Regression (`max_iter=1000`).
    - Random Forest (`n_estimators=100`).
    - SVM (`kernel='rbf'`, `probability=True`).

13. Deep learning models trained:
    - CNN.
    - LSTM.
    - BiLSTM.

14. Deep learning training configuration:
    - Loss: binary crossentropy.
    - Optimizer: Adam.
    - Output activation: sigmoid.
    - Epochs: 50.
    - Batch size: 32.
    - EarlyStopping: monitor `val_loss`, patience 5, restore best weights.

15. Evaluation metrics used:
    - Accuracy.
    - Precision.
    - Recall.
    - F1-score.

16. Model comparison and selection:
    - Combined ML and DL results into one comparison table.
    - Selected best model using maximum F1-score.

17. Visualization:
    - Generated model comparison bar chart.
    - Generated performance heatmap.
    - Saved as `model_comparison.png`.

18. Saving artifacts:
    - Saved ML models as `.pkl`.
    - Saved DL models as `.h5`.
    - Saved metadata (`label_encoder`, `max_length`, `vocab_size`, `best_model`) as `metadata.pkl`.

19. Prediction pipeline:
    - Loaded metadata.
    - Encoded and padded new sequence.
    - Loaded selected model type (ML or DL path).
    - Produced probability output.
    - Applied threshold 0.5 for class prediction.
    - Assigned risk levels:
      - High if probability > 0.7
      - Medium if 0.5 < probability <= 0.7
      - Low if probability <= 0.5

20. Demo sequences tested:
    - `KLVFFA`
    - `GVVIA`
    - `AAAQAA`
    - `FGAIL`

21. Runtime setup:
    - Dependencies managed through `requirements.txt`.
    - `run_model.bat` installs dependencies and runs the full training script.

## Preprocessing Only (Short Viva Version)

1. Selected `Peptide` and `Class` columns.
2. Standardized and cleaned class labels.
3. Converted classes into binary labels (`amyloid` / `non-amyloid`).
4. Dropped missing rows.
5. Removed duplicate peptides.
6. Integer-encoded peptide sequences using amino acid mapping.
7. Padded sequences to a fixed length.
8. Label-encoded output classes.
9. Built one-hot features for ML and padded sequence features for DL.

## Final Performance (From model comparison)

| Model | Accuracy | Precision | Recall | F1-Score |
|---|---:|---:|---:|---:|
| Logistic Regression | 0.778 | 0.816 | 0.768 | 0.792 |
| Random Forest | 0.766 | 0.781 | 0.795 | 0.788 |
| SVM | 0.773 | 0.812 | 0.764 | 0.787 |
| CNN | 0.833 | 0.846 | 0.850 | 0.848 |
| LSTM | 0.549 | 0.549 | 1.000 | 0.709 |
| BiLSTM | 0.805 | 0.862 | 0.768 | 0.812 |

Best model in this run: **CNN** (highest F1-score).
