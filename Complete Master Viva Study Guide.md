Here is the **Complete Master Viva Study Guide** explaining the entire process of your application: **Goal, End-to-End Pipeline, Web App Architecture, Machine Learning Concepts, and Viva Q&A**.

---

# 🎯 1. The Ultimate Project Goal
* **Problem:** Alzheimer's disease is progressive and currently diagnosed very late using costly procedures (MRI, PET scans, lumbar punctures).
* **Goal:** Create an **AI-driven early detection system** that predicts **amyloid aggregation risk** (a major early marker of Alzheimer's) directly from **peptide sequences** (short chains of amino acids).
* **Target Output:** 
  * **Input:** Peptide string (e.g. `KLVFFA`)
  * **Output:** Classification (`Amyloid` / `Non-amyloid`), Probability score (e.g. `87.4%`), and Risk Level (`High`, `Medium`, `Low`).

---

# 🔄 2. Complete Step-by-Step Technical Process

```
[Raw Web Data (CPAD 2.0)] 
       │ (1. Web Scraping)
[Data Cleaning & Normalization]
       │ (2. Data Preprocessing)
[Feature Encoding: One-Hot & Integer Padding]
       │ (3. Feature Engineering)
[Train-Test Split (80/20) + 5-Fold Cross-Validation]
       │ (4. Model Training)
[6 Models: LR, RF, SVM, CNN, LSTM, BiLSTM]
       │ (5. Evaluation & Chart Generation)
[Best Model Selected: CNN (F1 = 0.848)]
       │ (6. Model Artifact Serialization)
[Flask Web Interface (app.py + index.html)]
```

---

### Step 1: Data Collection (Scraping)
* **File:** `download_peptides.py`
* **Source:** Scraped **68 pages** from **CPAD 2.0** (Curated Peptide Amyloid Database).
* **Output:** Saved raw dataset containing **1,800+ peptides** into `peptides_data.csv` and `peptides_data.xlsx`.

### Step 2: Data Cleaning & Preprocessing
* **File:** `alzheimer_peptide_model.py` (`load_and_preprocess_data()`)
* **Actions:**
  1. Kept relevant columns: `Peptide` sequence & `Class` label.
  2. Standardized text to lowercase.
  3. Mapped all variations into **2 clean classes**:
     * `amyloid` (Positive class - Risk)
     * `non-amyloid` (Negative class - Low risk)
  4. Dropped null/missing entries and **removed duplicate peptides** to prevent data leakage.

### Step 3: Feature Encoding (Converting Letters to Numbers)
* **File:** `alzheimer_peptide_model.py` (`encode_sequences()`)
* Computers cannot read letters (`A, C, D, E...`), so we used **two encoding formats**:
  * **Standard Amino Acid Alphabet (20 letters):** `ACDEFGHIKLMNPQRSTVWY`
  * **Format A — One-Hot Encoding (For ML models: LR, RF, SVM):**
    * Position-aware vector representation (length = `max_sequence_length * 21`).
  * **Format B — Integer Sequence Padding (For DL models: CNN, LSTM, BiLSTM):**
    * Mapped each amino acid to integer IDs (`1 to 20`), using `0` for padding.
    * Padded sequences to uniform length (`max_length`) for batch training.

### Step 4: Data Splitting & Validation Strategy
* **Train / Test Split:** 80% Train, 20% Held-out Test set.
* **Stratified Split:** Kept class proportions consistent in both train and test sets.
* **Validation Strategy:**
  * **For ML:** **5-Fold Stratified Cross-Validation** (evaluates stability across 5 distinct folds).
  * **For DL:** Reserved 10% of training data as internal validation for **Early Stopping** (patience = 5 epochs) to avoid overfitting.

### Step 5: Model Training & Comparison
We trained **6 models** to compare classical ML against modern Deep Learning:

| Model | Type | How it works | Accuracy | F1-Score | Result |
|---|---|---|---:|---:|---|
| **Logistic Regression** | ML | Linear baseline classifier | 77.8% | 0.792 | Good baseline |
| **Random Forest** | ML | Ensemble of decision trees | 76.6% | 0.788 | Strong features |
| **SVM (RBF Kernel)** | ML | Non-linear boundary projection | 77.3% | 0.787 | Robust ML |
| **CNN (1D Conv)** | DL | Learns local 3-to-5 amino acid sequence motifs | **83.3%** | **0.848** | 🏆 **BEST MODEL** |
| **LSTM** | DL | Processes sequence left-to-right | 54.9% | 0.709 | Over-predicts positives |
| **BiLSTM** | DL | Processes sequence forward + backward | 80.5% | 0.812 | Runner-up |

---

# 🌐 3. How the Web Application Works (`app.py` & `index.html`)

```
[User enters 'KLVFFA' in Browser UI]
                  │
        (HTTP POST Request /predict)
                  ▼
         [Flask Server: app.py]
                  │
   (Loads metadata.pkl & cnn_model.h5)
                  │
   (Encodes & Pads input to max_length)
                  │
     (Model predicts probability: 0.874)
                  │
        (HTTP JSON Response)
                  ▼
[UI Updates: Shows 'Amyloid', 87.4% Bar, 'High Risk' Badge]
```

1. **Backend (`app.py`):**
   * Built with **Flask**.
   * Loads saved models from `/models` directory on demand (`.h5` for DL, `.pkl` for ML).
   * Reads `metadata.pkl` to know vocabulary size, max sequence length, and label mappings.
   * Exposes a REST API endpoint `/predict`.

2. **Frontend (`index.html`):**
   * Designed with modern Vanilla CSS (Dark mode, glassmorphism, responsive cards).
   * Uses an animated Canvas particle system background.
   * Sends asynchronous JavaScript `fetch()` request to `/predict`.
   * Dynamically renders risk level badge (`High` / `Medium` / `Low`) and animates the probability bar.

---

# 📚 4. Core Formulas for Viva

Make sure you memorize these 4 formulas:

1. $$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}$$
2. $$\text{Precision} = \frac{TP}{TP + FP} \quad \text{(How many predicted positive were actually positive?)}$$
3. $$\text{Recall} = \frac{TP}{TP + FN} \quad \text{(How many actual positive cases did we catch?)}$$
4. $$\text{F1-Score} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}} \quad \text{(Harmonic mean balancing Precision & Recall)}$$

---

# 🧠 5. Key Questions & Answers for Viva Defence

### Q1: Why did you choose F1-Score instead of Accuracy to select the best model?
**Answer:** Accuracy can be misleading if classes are imbalanced or if false negatives carry higher biological cost. F1-Score balances Precision and Recall, making it the most reliable evaluation metric for bio-sequence classification.

### Q2: Why did CNN outperform LSTM and BiLSTM?
**Answer:** Amyloid formation is primarily driven by short 3-to-6 amino acid local sequence patterns (called **motifs**, like `KLVFFA`). **1D CNNs** excel at extracting local spatial motifs via sliding kernels, whereas LSTMs attempt to model long-term sequential dependencies, which can introduce noise for short peptide chains.

### Q3: What is Data Leakage, and how did you prevent it?
**Answer:** Data leakage happens when test information leaks into model training. We prevented this by:
1. Deduplicating peptides during data cleaning.
2. Keeping the 20% test set completely hidden during feature encoding and model training.
3. Using an internal validation split for deep learning early stopping instead of validating on test data.

### Q4: How does a new sequence get predicted in your system?
**Answer:**
1. The user inputs a sequence string (e.g. `KLVFFA`).
2. The sequence is converted to integer tokens using `aa_to_int` vocabulary mapping.
3. `pad_sequences` pads or truncates it to `max_length` (position-aligned).
4. The trained model outputs a sigmoid probability $p \in [0, 1]$.
5. If $p > 0.5 \rightarrow \text{Amyloid}$; otherwise $\text{Non-amyloid}$.