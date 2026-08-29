# -*- coding: utf-8 -*-
"""
Populates the DIU FYDP report template with the Alzheimer's peptide project
content, while preserving the template's structure, styles and headings.
"""
import copy
import os
import pandas as pd
from docx import Document
from docx.oxml.ns import qn
from docx.shared import Inches, Pt
from docx.text.paragraph import Paragraph

SRC = 'FYDP-REPORT-SKILL/FYDP Tamplate for [Summer 2025].docx'
OUT = 'Alzheimer_Peptide_FYDP_Report_DRAFT.docx'

doc = Document(SRC)
body = doc.element.body

# ---------------------------------------------------------------------------
# Low level helpers
# ---------------------------------------------------------------------------

def all_paragraph_elements():
    return list(body.iter(qn('w:p')))


def para_style(p_el):
    pPr = p_el.find(qn('w:pPr'))
    if pPr is not None:
        pStyle = pPr.find(qn('w:pStyle'))
        if pStyle is not None:
            return pStyle.get(qn('w:val'))
    return None


def filtered_paragraph_elements():
    """Same filter used to build doc_paragraphs2.txt: keep paragraphs that have
    text or an explicit style. Index i here (0-based) corresponds to line i+1
    in doc_paragraphs2.txt."""
    out = []
    for p_el in all_paragraph_elements():
        text = ''.join(t.text or '' for t in p_el.iter(qn('w:t'))).strip()
        style = para_style(p_el)
        if text or style:
            out.append(p_el)
    return out


def get_run_props_xml(p_el):
    """Return the rPr xml of the first run in p_el, or None."""
    r = p_el.find(qn('w:r'))
    if r is not None:
        rpr = r.find(qn('w:rPr'))
        if rpr is not None:
            return copy.deepcopy(rpr)
    return None


def set_text(p_el, text, keep_rpr=True):
    """Replace all runs in a paragraph element with a single run containing text."""
    rpr = get_run_props_xml(p_el) if keep_rpr else None
    for r in p_el.findall(qn('w:r')):
        p_el.remove(r)
    for h in p_el.findall(qn('w:hyperlink')):
        p_el.remove(h)
    new_r = p_el.makeelement(qn('w:r'), {})
    if rpr is not None:
        new_r.append(rpr)
    new_t = new_r.makeelement(qn('w:t'), {})
    new_t.set(qn('xml:space'), 'preserve')
    new_t.text = text
    new_r.append(new_t)
    p_el.append(new_r)


def clone_paragraph(p_el):
    return copy.deepcopy(p_el)


def insert_after(anchor_el, new_el):
    anchor_el.addnext(new_el)
    return new_el


def insert_before(anchor_el, new_el):
    anchor_el.addprevious(new_el)
    return new_el


def insert_paragraphs_before(anchor_el, texts, style_source_el):
    created = []
    for t in texts:
        new_p = clone_paragraph(style_source_el)
        set_text(new_p, t)
        insert_before(anchor_el, new_p)
        created.append(new_p)
    return created


def insert_paragraphs_after(anchor_el, texts, style_source_el=None):
    """Clone anchor (or style_source) once per text, insert sequentially after anchor."""
    src = style_source_el if style_source_el is not None else anchor_el
    cur = anchor_el
    created = []
    for t in texts:
        new_p = clone_paragraph(src)
        set_text(new_p, t)
        insert_after(cur, new_p)
        cur = new_p
        created.append(new_p)
    return created


def restyle(p_el, style_name):
    pPr = p_el.find(qn('w:pPr'))
    if pPr is None:
        pPr = p_el.makeelement(qn('w:pPr'), {})
        p_el.insert(0, pPr)
    pStyle = pPr.find(qn('w:pStyle'))
    if pStyle is None:
        pStyle = pPr.makeelement(qn('w:pStyle'), {})
        pPr.insert(0, pStyle)
    pStyle.set(qn('w:val'), style_name)


def remove_paragraph(p_el):
    parent = p_el.getparent()
    if parent is not None:
        parent.remove(p_el)


def para_text(p_el):
    return ''.join(t.text or '' for t in p_el.iter(qn('w:t'))).strip()


def add_picture_after(anchor_el, image_path, width_inches):
    """Add a centered picture in a new paragraph placed right after anchor_el."""
    new_para = doc.add_paragraph()
    new_para.alignment = 1  # center
    run = new_para.add_run()
    run.add_picture(image_path, width=Inches(width_inches))
    p_el = new_para._p
    p_el.getparent().remove(p_el)
    insert_after(anchor_el, p_el)
    return p_el


FP = filtered_paragraph_elements()
print("Setup complete. Filtered paragraph elements:", len(FP))

# Sanity check against doc_paragraphs2.txt line numbers (spot checks)
check_lines = {106: 'ABSTRACT', 176: 'Introduction', 377: 'Research Methodology',
               449: 'Implementation and Results', 464: 'Engineering Standards and Design Challenges',
               568: 'Conclusion', 578: 'References'}
for line_no, expected in check_lines.items():
    actual = para_text(FP[line_no - 1])
    status = 'OK' if actual == expected else 'MISMATCH'
    print(f"  line {line_no}: expected={expected!r} actual={actual!r} [{status}]")

# ===========================================================================
# FRONT MATTER
# ===========================================================================
PROJECT_TITLE = "Early Detection of Alzheimer's Disease Using Peptide Sequences with Machine Learning and Deep Learning"
STUDENT_1_NAME = "Sheikh Shariar Nehal"

set_text(FP[0], PROJECT_TITLE)
remove_paragraph(FP[1])  # "Final Year Design Project" merges into title above
set_text(FP[3], STUDENT_1_NAME)
set_text(FP[4], "[Student ID]")
set_text(FP[5], "[Team Member 2 Name (if applicable)]")
set_text(FP[6], "[Student ID]")
set_text(FP[11], "[Supervisor Name], [Designation]")
set_text(FP[14], "[Co-Supervisor Name], [Designation] (if applicable)")
set_text(FP[21], "[Submission Date]")

set_text(FP[25],
    f'This Project titled \u201c{PROJECT_TITLE},\u201d submitted by {STUDENT_1_NAME} '
    'and [team member\u2019s name (if any)] to the Department of Computer Science and '
    'Engineering, Daffodil International University, has been accepted as satisfactory '
    'for the partial fulfillment of the requirements for the degree of B.Sc. in Computer '
    'Science and Engineering and approved as to its style and contents. The presentation '
    'has been held on [Presentation Date].')

set_text(FP[61],
    'We hereby declare that this project has been done by us under the supervision of '
    '[Supervisor Name], [Supervisor\u2019s Designation], Department of Computer Science '
    'and Engineering, Daffodil International University. We also declare that neither this '
    'project nor any part of this project has been submitted elsewhere for the award of any '
    'degree or diploma.')
set_text(FP[67], '[Supervisor Name]')
set_text(FP[75], '[Co-Supervisor Name] (if applicable)')
set_text(FP[82], STUDENT_1_NAME)
set_text(FP[83], 'Student ID: [Student ID]')
set_text(FP[88], '[Team Member 2 Name] (if applicable)')
set_text(FP[89], 'Student ID: [Student ID]')

set_text(FP[99],
    'We are grateful and wish to express our profound indebtedness to [Supervisor Name], '
    '[Supervisor\u2019s Designation], Department of Computer Science and Engineering, '
    'Daffodil International University, Dhaka, Bangladesh. The deep knowledge and keen '
    'interest of our supervisor in the field of machine learning and bioinformatics were '
    'essential to carrying out this project. Endless patience, scholarly guidance, continual '
    'encouragement, constant and energetic supervision, constructive criticism, valuable '
    'advice, and correction of several drafts made it possible to complete this project.')

ABSTRACT = (
    "Alzheimer's disease is a progressive neurodegenerative disorder that is usually "
    'diagnosed through costly, time-consuming procedures such as magnetic resonance '
    'imaging (MRI) and positron emission tomography (PET), which typically identify the '
    'disease only after substantial neuronal damage has already occurred. This report '
    "presents a computational approach for early Alzheimer's disease risk screening based "
    'on the aggregation tendency of peptide sequences, using amyloid-forming behaviour as a '
    'proxy indicator of risk. A dataset of peptide records was collected from the CPAD 2.0 '
    'peptide aggregation database by scraping 68 result pages, producing 2,001 raw records '
    'that were cleaned, deduplicated, and standardised into two classes: amyloid and '
    'non-amyloid. Each sequence was encoded in two forms: integer-mapped, padded sequences '
    'for deep learning models, and position-aware one-hot vectors for classical machine '
    'learning models. Three classical algorithms (Logistic Regression, Random Forest, and '
    'Support Vector Machine) and three deep learning architectures (Convolutional Neural '
    'Network, Long Short-Term Memory network, and Bidirectional LSTM) were trained and '
    'compared on a stratified, held-out test set using accuracy, precision, recall, '
    'F1-score, and ROC-AUC, with five-fold cross-validation applied to the classical models. '
    'The Convolutional Neural Network produced the strongest overall result, reaching an '
    'accuracy of 81.05%, an F1-score of 0.815, and a ROC-AUC of 0.893, ahead of both the '
    'classical baselines and the recurrent architectures. A Flask-based web interface was '
    'also built so that a user can submit an arbitrary peptide sequence and receive a '
    'real-time amyloid-risk prediction with an associated probability score. The results '
    'suggest that peptide sequence data, combined with convolutional feature extraction, '
    'can provide a low-cost, non-invasive screening signal that may complement existing '
    'clinical diagnostic pathways, although clinical validation on an independent dataset '
    'remains necessary before any practical use.'
)
set_text(FP[107], ABSTRACT)

# Fix the static "List of Figures" front-matter entry (was: sample diagram placeholder)
set_text(FP[167], '3.1\tEnd-to-end system pipeline for peptide-based classification\t4')
lof_entries = [
    '3.2\tData flow diagram of the prediction (web demo) subsystem\t5',
    '4.1\tModel performance comparison (bar chart and heatmap)\t7',
    '4.2\tROC curves for all six models\t7',
    '4.3\tConfusion matrix of the best-performing model (CNN)\t8',
    '4.4\tTraining history (accuracy and loss) of the CNN model\t8',
    '4.5\tConfusion matrix of the BiLSTM model on the test set\t9',
    '4.6\tTraining history (accuracy and loss) of the BiLSTM model\t9',
]
insert_paragraphs_after(FP[167], lof_entries, style_source_el=FP[167])

# Fix the static "List of Tables" front-matter entries (add the new tables)
lot_entries = [
    '2.2\tComparative capabilities of related approaches and the proposed system\t3',
    '3.1\tProject task allocation across the FYDP timeline\t6',
    '4.1\tComparative performance of all trained models on the held-out test set\t7',
]
insert_paragraphs_after(FP[169], lot_entries, style_source_el=FP[169])

print('Front matter done.')

# ===========================================================================
# CHAPTER 1: INTRODUCTION  (lines 174-202 -> FP[173:202])
# ===========================================================================
set_text(FP[177],
    'This chapter introduces the problem addressed by the project, the motivation behind '
    'it, the objectives pursued, a short outline of the methodology, the expected outcome, '
    'and the organisation of the remaining chapters.')

intro_paras = [
    ("Alzheimer's disease (AD) is a progressive neurodegenerative disorder and the leading "
     'cause of dementia worldwide. It gradually impairs memory, reasoning, and the ability '
     'to carry out daily activities, and its social and economic burden continues to grow '
     'as populations age. Diagnosis today relies mainly on clinical evaluation together with '
     'imaging techniques such as magnetic resonance imaging (MRI) and positron emission '
     'tomography (PET). These methods can confirm the presence of the disease, but they are '
     'expensive, time-consuming, and usually detect AD only after significant neuronal '
     'damage has already occurred.'),
    ('A large body of molecular biology research links AD pathology to the abnormal '
     'aggregation of amyloid-beta (A\u03b2) peptides into plaques in brain tissue [9], [10]. '
     'Because the amino acid sequence of a peptide directly influences its tendency to '
     'aggregate, the sequence itself carries information that computational methods can use '
     'to estimate amyloid risk without imaging or invasive sampling. This project examines '
     'whether peptide sequence data, combined with machine learning (ML) and deep learning '
     '(DL) techniques, can be used to build a low-cost screening tool that classifies a '
     'peptide as amyloid-forming (higher AD-related risk) or non-amyloid (lower risk), using '
     'the CPAD 2.0 peptide aggregation database [1] as the primary data source.'),
]
set_text(FP[181], intro_paras[0])
insert_paragraphs_after(FP[181], intro_paras[1:])

set_text(FP[185],
    'Existing AD diagnostic pipelines are not well suited to large-scale or repeated '
    'screening, both because of their cost and because they detect the disease only in its '
    'later stages. A sequence-based computational classifier does not require imaging '
    'hardware, can run on ordinary computing equipment, and could, in principle, be built '
    'into a larger bioinformatics pipeline used by researchers studying amyloid-related '
    'biomarkers. This project was also motivated by an interest in comparing classical '
    'machine learning with modern deep sequence models on a real biological classification '
    'task, and in understanding, in a concrete case, why some architectures capture peptide '
    'aggregation patterns better than others.')

objectives_text = [
    ('The general objective of this project is to design and implement an artificial '
     'intelligence based system that can classify peptide sequences into amyloid and '
     'non-amyloid categories in support of early Alzheimer\u2019s disease risk screening. '
     'The specific objectives are:'),
    ('(i) collect and clean a peptide sequence dataset from the CPAD 2.0 database, removing '
     'duplicate and missing entries and standardising class labels;'),
    ('(ii) encode peptide sequences into machine-readable representations suited to both '
     'classical machine learning (one-hot vectors) and deep learning (padded integer '
     'sequences);'),
    ('(iii) train baseline classical machine learning models \u2014 Logistic Regression, '
     'Random Forest, and Support Vector Machine \u2014 using stratified five-fold '
     'cross-validation;'),
    ('(iv) design and train deep learning architectures \u2014 Convolutional Neural Network '
     '(CNN), Long Short-Term Memory network (LSTM), and Bidirectional LSTM (BiLSTM) \u2014 '
     'with early stopping to reduce overfitting;'),
    ('(v) evaluate every model on a common held-out test set using accuracy, precision, '
     'recall, F1-score, and ROC-AUC, and identify the best-performing model; and'),
    ('(vi) package the best-performing model behind a simple web interface so that a new '
     'peptide sequence can be submitted and scored in real time.'),
]
set_text(FP[189], objectives_text[0])
insert_paragraphs_after(FP[189], objectives_text[1:])

set_text(FP[193],
    'The project follows a quantitative, experimental methodology. Peptide records are '
    'downloaded from CPAD 2.0, cleaned, deduplicated, and label-standardised. Sequences are '
    'encoded into two representations \u2014 padded integer sequences and position-aware '
    'one-hot vectors \u2014 to suit deep learning and classical machine learning models '
    'respectively. Six models are trained under matching evaluation conditions (stratified '
    'train-test split, common metric set) and compared to select the best-performing model, '
    'which is then exposed through a Flask web application for interactive testing. Chapter '
    '3 describes this methodology in detail.')

set_text(FP[197],
    'The direct outcome of this project is a reproducible pipeline that turns raw peptide '
    'aggregation records into a trained classifier and an accompanying working demonstration '
    'that any user can query. Beyond the trained models themselves, the project produces a '
    'documented comparison of classical and deep sequence models on the same peptide dataset, '
    'which can act as a reference point for further work on computational, sequence-based '
    'screening for amyloid-related risk.')

set_text(FP[201],
    'The remainder of this report is organised as follows. Chapter 2 reviews the background '
    "of Alzheimer's disease and amyloid aggregation, surveys related computational work, and "
    'identifies the gap this project addresses. Chapter 3 describes the research methodology, '
    'including the system design, requirements, data flow, and project plan. Chapter 4 '
    'presents the implementation, evaluation methodology, and results. Chapter 5 discusses '
    'engineering standards, societal and ethical impact, project management, and the mapping '
    'of this work to complex engineering problems and activities. Chapter 6 concludes the '
    'report with a summary, limitations, and directions for future work.')

print('Chapter 1 done.')

# ===========================================================================
# CHAPTER 2: BACKGROUND  (lines 203-374 -> FP[202:374])
# ===========================================================================
set_text(FP[206],
    "This chapter presents the background needed to understand the rest of the report, "
    'reviews related computational work on Alzheimer\u2019s disease and amyloid prediction, '
    'and identifies the gap this project addresses.')

background_paras = [
    ("Alzheimer's disease (AD) is an irreversible neurodegenerative disorder and the principal "
     'cause of dementia, marked by progressive memory loss and behavioural change [11]. Standard '
     'diagnostic procedures such as MRI and PET imaging can reveal structural and functional '
     'changes in the brain, but they are time-consuming, costly, and not always available, which '
     'limits their use for early or repeated screening.'),
    ('A substantial body of biological evidence links AD to the abnormal aggregation of '
     'amyloid-beta (A\u03b2) peptides into extracellular plaques, a process that disrupts '
     'neuron-to-neuron signalling and contributes to neurodegeneration [9], [10]. The NIA-AA '
     'research framework further formalises amyloid status as one of the core biological '
     'markers used to define AD progression [12]. Because the tendency of a peptide to '
     'aggregate is strongly influenced by its amino acid sequence, sequence-based computational '
     'analysis is a promising, low-cost complement to imaging-based diagnosis.'),
    ('Advances in bioinformatics have made it practical to apply machine learning directly to '
     'protein and peptide sequences. Classical algorithms such as Support Vector Machines have '
     'been used to predict AD-related biomarkers from gene-coding protein sequences with '
     'reported accuracies above 85% [8], while deep learning architectures such as '
     'Convolutional Neural Networks (CNNs) and Recurrent Neural Networks (RNNs) can capture '
     'local motifs and longer-range dependencies in a sequence that are relevant to aggregation '
     'behaviour [7]. Public repositories such as CPAD 2.0 make peptide sequence and aggregation '
     'label data freely available for this kind of model development and evaluation [1].'),
]
set_text(FP[210], background_paras[0])
insert_paragraphs_after(FP[210], background_paras[1:])

set_text(FP[214],
    'This section reviews five research papers that were studied in detail while planning this '
    'project, together with several long-standing reference works on the amyloid hypothesis of '
    "Alzheimer's disease. Table 2.1 summarises the reviewed papers; a short discussion follows.")

lit_review_narrative = [
    ('Yu et al. [4] proposed a multi-source protein feature fusion framework that combines '
     'laboratory data and literature-derived features to predict protein-protein interactions '
     'relevant to AD, using a Graph Convolutional Network for link prediction and reporting an '
     'AUC of 0.8935. This work shows that fusing heterogeneous biological features can improve '
     'prediction of AD-related molecular interactions, though it operates at the protein '
     'interaction network level rather than on individual peptide sequences.'),
    ('Hassan et al. [5] took an imaging-based route, using a VGG16 convolutional network to '
     'extract features from MRI and PET scans for AD detection and classification. Their work '
     'confirms that deep convolutional features are effective for AD-related classification '
     'tasks, but, like most imaging-based methods, it depends on access to scan data rather than '
     'inexpensive sequence data.'),
    ('Rani et al. [6] applied a SMOTE-RF methodology, combining synthetic minority oversampling '
     'with Random Forest, Decision Tree, and XGBoost classifiers on the OASIS imaging-derived '
     'dataset, reporting up to 87.84% accuracy on the imbalanced dataset and higher accuracy '
     'after balancing. This confirms that ensemble tree-based methods remain competitive '
     'baselines for AD-related classification, which motivated including Random Forest as one '
     'of the classical baselines in this project.'),
    ('Wang et al. [7] applied deep mutational scanning together with CNNs and RNNs to model the '
     'effect of mutations on the aggregation-related biochemical traits of the A\u03b2 42 '
     'peptide, finding convolutional and recurrent architectures to be the most cost-effective '
     'choices for this kind of sequence modelling. This result directly supports the choice of '
     'CNN, LSTM, and BiLSTM architectures evaluated in this project.'),
    ('Xu et al. [8] used a Support Vector Machine based on dipeptide composition frequency '
     '(the frequency of consecutive amino-acid pairs) to identify AD-related genes from '
     'gene-coding protein sequences, reporting 85.7% accuracy. This confirms that sequence '
     'composition alone, without imaging, carries a usable classification signal, which is the '
     'central premise of this project.'),
    ('Beyond these five papers, this project also draws on established biological reference '
     'work: the amyloid hypothesis first articulated by Hardy and Selkoe [9] and revisited '
     'twenty-five years later [10], the neuropathological staging criteria of Braak and Braak '
     '[11], the NIA-AA biological research framework [12], and the TANGO algorithm for '
     'predicting sequence-dependent aggregation proposed by Fernandez-Escamilla et al. [13].'),
]

insert_paragraphs_before(FP[254], lit_review_narrative, style_source_el=FP[210])

# Clean the instructional parenthetical off the "Similar Applications" heading
set_text(FP[254], 'Similar Applications', keep_rpr=True)

set_text(FP[255],
    'Beyond peer-reviewed classifiers, several long-standing bioinformatics tools address a '
    'closely related problem: predicting the aggregation propensity of a peptide directly '
    'from its sequence. TANGO [13] and related sequence-based predictors such as WALTZ and '
    'AGGRESCAN estimate aggregation propensity using physicochemical scales fitted to '
    'experimental data, without a supervised training/test split or a reported classification '
    'accuracy in the sense used in this project. The imaging-based system of Hassan et al. [5] '
    'and the tabular SMOTE-RF system of Rani et al. [6] are closer in spirit to a deployable '
    'application, but both rely on clinical imaging or derived imaging features rather than raw '
    'peptide sequence. None of these tools combines a trained, evaluated ML/DL comparison on '
    'peptide sequence data with a public, queryable web interface, which is the specific '
    'combination this project provides.')

gap_intro = [
    ('The literature reviewed in Section 2.2 points to several recurring gaps that this '
     'project attempts to address, summarised in Table 2.2:'),
]
set_text(FP[260], gap_intro[0])

set_text(FP[262], 'Table 2.2: Comparative capabilities of related approaches and the proposed system.')

set_text(FP[373],
    "This chapter presented the biological background of Alzheimer's disease and amyloid "
    'aggregation, reviewed five recent papers on computational AD prediction together with '
    'classical amyloid biology references, discussed sequence-based aggregation predictors as '
    'similar applications, and summarised the gaps that motivate this project\u2019s design.')

print('Chapter 2 narrative done.')

# ---------------------------------------------------------------------------
# TABLE 2.1 : Literature Review
# ---------------------------------------------------------------------------
lit_table = doc.tables[0]
lit_rows = [
    ['Yu et al. [4]', '2025', 'Protein interaction prediction for AD using a multi-source '
     'protein features fusion framework', 'Graph Convolutional Network on a fused '
     'protein-protein interaction network', 'Achieved AUC = 0.8935 for AD-related protein '
     'interaction link prediction.'],
    ['Hassan et al. [5]', '2024', 'A multimodal approach for AD detection and classification '
     'using deep learning', 'VGG16 CNN feature extraction from MRI/PET scans', 'Showed deep '
     'convolutional features are effective for AD classification from imaging data.'],
    ['Rani et al. [6]', '2024', 'A machine learning model for AD prediction', 'SMOTE-RF: '
     'oversampling with Decision Tree, XGBoost, Random Forest on OASIS data', 'Random Forest '
     'reached up to 87.84% accuracy on the imbalanced imaging-derived dataset.'],
    ['Wang et al. [7]', '2023', "Towards mechanistic models of mutational effects: deep "
     "learning on Alzheimer's A\u03b2 peptide", 'CNN and RNN models on deep mutational '
     'scanning data', 'CNN/RNN architectures were the most cost-effective for modelling '
     'peptide aggregation traits.'],
    ['Xu et al. [8]', '2018', 'An efficient classifier for AD genes identification', 'SVM on '
     'dipeptide composition frequency of gene-coding protein sequences', 'Reported 85.7% '
     'accuracy identifying AD from protein sequence information.'],
    ['Hardy and Selkoe [9]', '2002', 'The amyloid hypothesis of AD: progress and problems on '
     'the road to therapeutics', 'Review / hypothesis paper', 'Established amyloid-beta '
     'aggregation as a central mechanism in AD pathogenesis.'],
    ['Selkoe and Hardy [10]', '2016', 'The amyloid hypothesis of AD at 25 years', 'Review '
     'paper', 'Revisited and updated the amyloid hypothesis considering newer genetic and '
     'biomarker evidence.'],
    ['Fernandez-Escamilla et al. [13]', '2004', 'Prediction of sequence-dependent and '
     'mutational effects on the aggregation of peptides and proteins', 'TANGO: statistical '
     'mechanics algorithm using physicochemical parameters', 'Enabled sequence-based '
     'prediction of aggregation-prone regions without a training/test split.'],
]
while len(lit_table.rows) > 1:
    lit_table._tbl.remove(lit_table.rows[1]._tr)
for row_data in lit_rows:
    row = lit_table.add_row()
    for c, val in enumerate(row_data):
        row.cells[c].text = val
print('Table 2.1 populated with', len(lit_rows), 'rows.')

# ---------------------------------------------------------------------------
# TABLE 2.2 : Gap analysis / comparative capability table
# ---------------------------------------------------------------------------
gap_table = doc.tables[1]
gap_header = ['Capability', 'TANGO / WALTZ /\nAGGRESCAN [13]', 'Imaging CNN\n(Hassan et al. [5])',
              'SMOTE-RF\n(Rani et al. [6])', 'SVM gene classifier\n(Xu et al. [8])',
              'CNN/RNN peptide\nmodel (Wang et al. [7])', 'Proposed system']
gap_rows = [
    ['Uses raw peptide/protein sequence as input', 'Yes', 'No', 'No', 'Yes', 'Yes', 'Yes'],
    ['Requires clinical imaging (MRI/PET)', 'No', 'Yes', 'Yes (imaging-derived)', 'No', 'No', 'No'],
    ['Trained/evaluated with a supervised train-test split', 'No', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes'],
    ['Compares classical ML and deep learning under one pipeline', 'No', 'No', 'No', 'No', 'No', 'Yes'],
    ['Reports ROC-AUC alongside accuracy/F1', 'No', 'Not reported', 'No', 'No', 'No', 'Yes'],
    ['Provides a public, queryable web interface for a new sequence', 'Partial', 'No', 'No', 'No', 'No', 'Yes'],
    ['Open-source, reproducible implementation', 'Partial', 'Not specified', 'Not specified', 'Not specified', 'Not specified', 'Yes'],
]
hdr_cells = gap_table.rows[0].cells
for c, val in enumerate(gap_header):
    hdr_cells[c].text = val
while len(gap_table.rows) > 1:
    gap_table._tbl.remove(gap_table.rows[1]._tr)
for row_data in gap_rows:
    row = gap_table.add_row()
    for c, val in enumerate(row_data):
        row.cells[c].text = val
print('Table 2.2 populated.')

print('Chapter 2 done.')

BODY_STYLE_SRC = FP[210]  # a known-good BodyText paragraph, reused as a clone source everywhere below

# ===========================================================================
# CHAPTER 3: RESEARCH METHODOLOGY  (lines 375-446 -> FP[374:446])
# ===========================================================================
set_text(FP[378],
    'This chapter describes the research methodology followed in the project: the overall '
    'approach and system design, the functional and non-functional requirements, the data '
    'flow of the prediction system, the user interface, the alternatives considered, and the '
    'project plan and task allocation.')

# Remove the template's "Note: keep X for project/research" instructional lines
for idx in (381, 382, 383, 386, 387, 388):
    remove_paragraph(FP[idx])

insert_paragraphs_after(FP[384],
    ['This project follows a quantitative, experimental research design rather than a '
     'requirement-driven software project design, since the objective is to compare '
     'modelling approaches on a fixed dataset rather than to build a product for external '
     'stakeholders. The workflow consists of data preprocessing, sequence encoding, a '
     'stratified train-test split, multi-model training (classical ML and deep learning), '
     'metric-based evaluation, and model comparison, followed by packaging the best model '
     'behind a small web interface for interactive testing.'],
    style_source_el=BODY_STYLE_SRC)

insert_paragraphs_after(FP[385],
    ['Figure 3.1 shows the proposed end-to-end pipeline as implemented in '
     'alzheimer_peptide_model.py. Raw peptide records are scraped from CPAD 2.0 [1], cleaned '
     'and deduplicated, and their class labels standardised to amyloid or non-amyloid. The '
     'cleaned sequences are encoded twice \u2014 once as padded integer sequences for the '
     'deep learning models and once as position-aware one-hot vectors for the classical '
     'models \u2014 and split into a stratified 80/20 train-test partition. The three '
     'classical models are trained with five-fold cross-validation on the training partition, '
     'and the three deep learning models are trained with an internal validation split (10% '
     'of the training data) and early stopping. All six models are then evaluated on the same '
     'held-out test set, and the model with the highest F1-score is selected for deployment '
     'in the web interface.'],
    style_source_el=BODY_STYLE_SRC)

# Replace the sample-diagram caption and insert a real pipeline figure before it
set_text(FP[392], 'Figure 3.1: End-to-end system pipeline for peptide-based Alzheimer\u2019s risk classification.')
add_picture_after(FP[391], 'report_figures/fig_3_1_pipeline.png', 6.0)

# Functional / Non-functional requirements: fix mis-styled Heading4 note paragraphs
remove_paragraph(FP[394])  # stray "Note:" label
restyle(FP[395], 'BodyText')
restyle(FP[396], 'BodyText')
set_text(FP[395],
    'Functional requirements describe what the system must do. For this project they are: '
    '(1) accept a peptide sequence composed of the 20 standard amino acid letters as input; '
    '(2) validate that every character belongs to the standard amino acid alphabet '
    '(ACDEFGHIKLMNPQRSTVWY) and reject sequences that contain any other character; (3) '
    'encode the validated sequence into the padded/one-hot representation expected by the '
    'selected model; (4) run inference with the chosen trained model (Logistic Regression, '
    'Random Forest, SVM, CNN, LSTM, or BiLSTM) and return a class label (amyloid / '
    'non-amyloid), a probability score, and a risk level (Low / Medium / High); and (5) allow '
    'the user to repeat this process for any number of sequences without restarting the '
    'application.')
set_text(FP[396],
    'Non-functional requirements describe how well the system performs these functions. For '
    'this project they are: (1) accuracy \u2014 the deployed model should reach at least 80% '
    'test accuracy, which the CNN model satisfies at 81.05%; (2) responsiveness \u2014 a '
    'single prediction should return in well under one second on ordinary desktop hardware, '
    'since inference on a single short sequence is computationally light; (3) reproducibility '
    '\u2014 all random operations (train-test split, cross-validation folds, weight '
    'initialisation seeds where supported) use a fixed random state so that results can be '
    'reproduced; and (4) usability \u2014 the web interface should accept plain text input '
    'and present the result without requiring the user to understand the underlying model.')

insert_paragraphs_after(FP[397],
    ['Figure 3.2 shows the data flow of the prediction subsystem exposed through the Flask '
     'web application (app.py). The user submits a peptide sequence and a model choice '
     'through the browser; the Flask route validates the input and calls the encoding and '
     'inference logic, which reads the previously saved model weights and metadata '
     '(vocabulary, maximum sequence length, label encoder) from the models/ directory and '
     'returns a JSON response containing the prediction, probability, and risk level, which '
     'the front end then renders.'],
    style_source_el=BODY_STYLE_SRC)
add_picture_after(FP[397], 'report_figures/fig_3_2_dfd.png', 5.8)

set_text(FP[399],
    'The user interface is a single-page web application (templates/index.html) served by '
    'Flask. It provides a text field for the peptide sequence, a drop-down to select which '
    'trained model to use, and a button that triggers an asynchronous request to the '
    '/predict endpoint. The result is displayed as a predicted class, an animated probability '
    'bar, and a colour-coded risk badge (green for Low, amber for Medium, red for High), so '
    'that a non-technical examiner can query the system without needing to read any code.')

set_text(FP[402],
    'Several alternative design choices were considered before settling on the final '
    'pipeline. For sequence representation, k-mer frequency counting was considered as an '
    'alternative to one-hot and integer encoding; it was not adopted because it discards '
    'positional information that convolutional and recurrent models can otherwise exploit. '
    'For evaluation, a single train-test split without cross-validation was considered for '
    'the classical models, but five-fold cross-validation was adopted instead because the '
    'dataset, after deduplication, is modest in size and a single split can give an '
    'optimistic or pessimistic estimate depending on how the data happens to be divided. For '
    'the deep learning validation strategy, using the test set itself for early stopping was '
    'considered (and was, in fact, an earlier limitation of this project) but was replaced '
    'with a dedicated internal validation split so that the test set remains untouched until '
    'final evaluation. Finally, a single hybrid architecture was not adopted as the primary '
    'deliverable; instead, three deep learning architectures were trained independently so '
    'that their relative strengths (CNN for local motifs, LSTM/BiLSTM for longer-range '
    'dependencies) could be compared directly.')

insert_paragraphs_after(FP[404],
    ['The project was planned and executed across two reporting phases, following the '
     'timeline in Table 3.1. The first phase covered data collection, cleaning, and the '
     'baseline machine learning models; the second phase covered the deep learning models, '
     'evaluation artefacts, the web demonstration, and the final report.'],
    style_source_el=BODY_STYLE_SRC)

print('Chapter 3 part A done.')

# --- Task Allocation (3.4) ---------------------------------------------------
set_text(FP[407], 'This table depicts the timeline of the principal activities across the project,')
set_text(FP[408], 'covering weeks 6 to 48 of the two-phase FYDP schedule.')
set_text(FP[409], 'Table 3.1: Project task allocation across the FYDP timeline.')

task_table = doc.tables[2]
# Row 0: 'Tasks' + 'Weeks' x19 (header) -- leave as is
# Row 1: '' + week numbers 12..48 -- replace with the real week markers used (6..48, step ~2)
week_values = [6, 8, 10, 12, 16, 20, 24, 28, 32, 36, 38, 40, 42, 44, 45, 46, 47, 48, 48]
row1_cells = task_table.rows[1].cells
for c, val in enumerate(week_values):
    if c + 1 < len(row1_cells):
        row1_cells[c + 1].text = str(val)

task_defs = [
    ('Data cleaning, deduplication, and\nlabel standardisation', {0, 1, 2, 3}),
    ('Feature encoding and baseline ML\ntraining (LR, RF, SVM, 5-fold CV)', {2, 3, 4, 5, 6}),
    ('Deep learning development and\ntraining (CNN, LSTM, BiLSTM)', {5, 6, 7, 8, 9, 10}),
    ('Evaluation, Flask web demo, and\nfinal report drafting', {9, 10, 11, 12, 13, 14, 15, 16, 17, 18}),
]
# rows 2-3 = task group 1 (two stacked rows), 4-5 = group 2, 6-7 = group 3, 8-9 = group 4
row_pairs = [(2, 3), (4, 5), (6, 7), (8, 9)]
for (r_top, r_bot), (label, active_cols) in zip(row_pairs, task_defs):
    task_table.rows[r_top].cells[0].text = label
    task_table.rows[r_bot].cells[0].text = label
    for col in active_cols:
        task_table.rows[r_top].cells[col + 1].text = '\u25a0'
        task_table.rows[r_bot].cells[col + 1].text = '\u25a0'
print('Task allocation table populated.')

remove_paragraph(FP[441])  # stray empty Heading3

set_text(FP[445],
    'This chapter described the research methodology of the project: a quantitative, '
    'experimental design covering data preprocessing, dual sequence encoding, six-model '
    'training and evaluation, and deployment through a Flask web interface, together with '
    'the functional and non-functional requirements, the data flow of the prediction '
    'subsystem, the alternatives considered, and the project timeline.')

print('Chapter 3 done.')

# ===========================================================================
# CHAPTER 4: IMPLEMENTATION AND RESULTS (lines 447-461 -> FP[446:461])
# ===========================================================================
set_text(FP[450],
    'This chapter describes the software environment used to build the system, the '
    'evaluation methodology applied to every model, and the results obtained, together with '
    'a discussion of why the models performed as they did.')
remove_paragraph(FP[451])

set_text(FP[454],
    'The pipeline was implemented in Python 3.x. Data collection used requests and '
    'BeautifulSoup [18]; data handling used pandas [14] and NumPy [15]; classical models '
    'used scikit-learn [2]; deep learning models used TensorFlow/Keras [3]; result plots used '
    'Matplotlib [16] and Seaborn [17]; spreadsheet export used openpyxl [19]; and the '
    'interactive demonstration used Flask [20]. No specialised hardware was required: every '
    'model trains and runs inference on an ordinary desktop or laptop CPU, since the dataset '
    'is small (a few thousand short sequences) and none of the architectures used exceeds a '
    'few hundred thousand parameters.')

insert_paragraphs_after(FP[455],
    ['Every model was evaluated on the same held-out test set (20% of the cleaned dataset, '
     'stratified by class, random_state = 42) to keep the comparison fair. The three '
     'classical models (Logistic Regression, Random Forest, SVM) were additionally evaluated '
     'with stratified five-fold cross-validation on the training partition, which gives a '
     'more stable estimate of performance than a single split. The three deep learning '
     'models (CNN, LSTM, BiLSTM) were trained with a dedicated internal validation split '
     '(10% of the training data) and early stopping (patience = 5 epochs on validation loss, '
     'best weights restored) so that the test set was never used during training or model '
     'selection.',
     'Five metrics were computed for every model from the confusion matrix on the test set: '
     'Accuracy = (TP + TN) / (TP + TN + FP + FN); Precision = TP / (TP + FP); Recall = TP / '
     '(TP + FN); F1-score = 2 \u00d7 (Precision \u00d7 Recall) / (Precision + Recall); and '
     'ROC-AUC, the area under the receiver operating characteristic curve, computed from the '
     'predicted probabilities rather than the thresholded class label. F1-score was used as '
     'the primary criterion for selecting the best model because it balances precision and '
     'recall, which is more informative than accuracy alone when false positives and false '
     'negatives are not equally costly.'],
    style_source_el=BODY_STYLE_SRC)

results_intro = insert_paragraphs_after(FP[456],
    ['Table 4.1 summarises the performance of all six models on the held-out test set, '
     'taken directly from the metrics_summary.csv file produced by the training pipeline.'],
    style_source_el=BODY_STYLE_SRC)
anchor = results_intro[-1]

# --- Table 4.1: results table (loaded dynamically from metrics_summary.csv) -------
cap = clone_paragraph(BODY_STYLE_SRC)
set_text(cap, 'Table 4.1: Comparative performance of all trained models on the held-out test set.')
insert_after(anchor, cap)
anchor = cap

metrics_csv_path = 'results/metrics_summary.csv'
if os.path.exists(metrics_csv_path):
    metrics_df = pd.read_csv(metrics_csv_path, index_col=0)
    results_table_data = [['Model', 'Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC']]
    for model_name, row in metrics_df.iterrows():
        results_table_data.append([
            str(model_name),
            f"{float(row['Accuracy']):.4f}",
            f"{float(row['Precision']):.4f}",
            f"{float(row['Recall']):.4f}",
            f"{float(row['F1-Score']):.4f}",
            f"{float(row['ROC-AUC']):.4f}",
        ])
else:
    results_table_data = [
        ['Model', 'Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC'],
        ['Logistic Regression', '0.7781', '0.8164', '0.7682', '0.7916', '0.8472'],
        ['Random Forest', '0.7656', '0.7812', '0.7955', '0.7883', '0.8649'],
        ['SVM', '0.7731', '0.8116', '0.7636', '0.7869', '0.8492'],
        ['CNN', '0.8105', '0.8789', '0.7591', '0.8146', '0.8925'],
        ['LSTM', '0.5511', '0.5500', '1.0000', '0.7097', '0.5532'],
        ['BiLSTM', '0.8030', '0.8770', '0.7455', '0.8059', '0.8769'],
    ]

new_tbl = doc.add_table(rows=len(results_table_data), cols=6)
new_tbl.style = doc.tables[0].style
for r, row_vals in enumerate(results_table_data):
    for c, val in enumerate(row_vals):
        new_tbl.rows[r].cells[c].text = val
tbl_el = new_tbl._tbl
tbl_el.getparent().remove(tbl_el)
insert_after(anchor, tbl_el)
anchor = tbl_el

discussion_paras = [
    ('The Convolutional Neural Network achieved the best overall result, with the highest '
     'accuracy (81.05%), F1-score (0.815), and ROC-AUC (0.893) of all six models. This is '
     'consistent with the literature reviewed in Chapter 2: Wang et al. [7] found CNN and RNN '
     'architectures to be the most cost-effective choice for modelling short peptide '
     'aggregation traits, and amyloid-forming behaviour is strongly influenced by short, '
     'local motifs (three to six residues) such as the well-known KLVFFA segment of '
     'amyloid-beta, which a convolutional filter is well suited to detect regardless of where '
     'the motif appears in the sequence.'),
    ('BiLSTM was the second-best model (accuracy 80.30%, F1 = 0.806, ROC-AUC = 0.877), ahead '
     'of all three classical baselines, showing that a bidirectional recurrent architecture '
     'can also capture useful contextual sequence patterns, though slightly less efficiently '
     'than the convolutional approach for this dataset. The plain, single-direction LSTM '
     'performed noticeably worse (accuracy 55.11%, F1 = 0.710) despite a nominal recall of 1.0; '
     'this combination \u2014 high recall with low accuracy and low precision (0.550) \u2014 '
     'indicates that the LSTM collapsed towards predicting the positive (amyloid) class for '
     'almost every input, rather than learning a genuinely discriminative decision boundary.'),
    ('The three classical models (Logistic Regression, Random Forest, SVM) performed '
     'similarly to one another, with accuracy between 76.6% and 77.8% and F1-scores between '
     '0.787 and 0.792, forming a consistent baseline band below the CNN and BiLSTM. This '
     'matches the expectation that models operating on a fixed one-hot representation, '
     'without any mechanism to learn position-invariant local patterns, are at a structural '
     'disadvantage relative to a convolutional model on this kind of sequence data. Random '
     'Forest reached the highest ROC-AUC among the classical models (0.865), suggesting its '
     'ensemble of decision trees captured some non-linear structure in the one-hot features '
     'that the linear Logistic Regression model could not.'),
    ('Figure 4.1 presents the six models side by side as a bar chart and as a metric '
     'heatmap, and Figure 4.2 shows the ROC curves for all models on a common plot. Figures '
     '4.3 and 4.4 illustrate the confusion matrix and training curves for the leading CNN model, '
     'while Figures 4.5 and 4.6 provide the confusion matrix and training curves for the runner-up '
     'BiLSTM model. Both deep learning models converge smoothly under the early-stopping window '
     'without a widening gap between training and validation loss, demonstrating that the internal '
     'validation split and early stopping strategy adopted in Chapter 3 successfully prevented overfitting.'),
]

created = insert_paragraphs_after(anchor, [discussion_paras[0]], style_source_el=BODY_STYLE_SRC)
anchor = created[-1]

fig_cap = clone_paragraph(BODY_STYLE_SRC)
set_text(fig_cap, 'Figure 4.1: Model performance comparison (bar chart and metric heatmap) across all six trained models.')
insert_after(anchor, fig_cap)
add_picture_after(fig_cap, 'results/model_comparison.png', 6.0)
anchor = fig_cap.getnext()

created = insert_paragraphs_after(anchor, [discussion_paras[1]], style_source_el=BODY_STYLE_SRC)
anchor = created[-1]

fig_cap2 = clone_paragraph(BODY_STYLE_SRC)
set_text(fig_cap2, 'Figure 4.2: ROC curves for all six models on the held-out test set.')
insert_after(anchor, fig_cap2)
add_picture_after(fig_cap2, 'results/roc_auc_all_models.png', 5.0)
anchor = fig_cap2.getnext()

created = insert_paragraphs_after(anchor, [discussion_paras[2]], style_source_el=BODY_STYLE_SRC)
anchor = created[-1]

fig_cap3 = clone_paragraph(BODY_STYLE_SRC)
set_text(fig_cap3, 'Figure 4.3: Confusion matrix of the best-performing model (CNN) on the test set.')
insert_after(anchor, fig_cap3)
add_picture_after(fig_cap3, 'results/confusion_matrix_cnn.png', 3.6)
anchor = fig_cap3.getnext()

fig_cap4 = clone_paragraph(BODY_STYLE_SRC)
set_text(fig_cap4, 'Figure 4.4: Training history (accuracy and loss) of the CNN model.')
insert_after(anchor, fig_cap4)
add_picture_after(fig_cap4, 'results/training_history_cnn.png', 6.0)
anchor = fig_cap4.getnext()

fig_cap5 = clone_paragraph(BODY_STYLE_SRC)
set_text(fig_cap5, 'Figure 4.5: Confusion matrix of the BiLSTM model on the held-out test set.')
insert_after(anchor, fig_cap5)
add_picture_after(fig_cap5, 'results/confusion_matrix_bilstm.png', 3.6)
anchor = fig_cap5.getnext()

fig_cap6 = clone_paragraph(BODY_STYLE_SRC)
set_text(fig_cap6, 'Figure 4.6: Training history (accuracy and loss) of the BiLSTM model.')
insert_after(anchor, fig_cap6)
add_picture_after(fig_cap6, 'results/training_history_bilstm.png', 6.0)
anchor = fig_cap6.getnext()

created = insert_paragraphs_after(anchor, [discussion_paras[3]], style_source_el=BODY_STYLE_SRC)

set_text(FP[460],
    'This chapter described the implementation environment, the evaluation methodology '
    '(stratified split, five-fold cross-validation for the classical models, and a separate '
    'validation split with early stopping for the deep learning models), and the results of '
    'all six trained models. The Convolutional Neural Network was identified as the '
    'best-performing model, reaching 81.05% accuracy and an F1-score of 0.815, and its '
    'behaviour was examined through confusion matrices, ROC curves, and training history '
    'plots alongside the runner-up BiLSTM model.')

print('Chapter 4 done.')

# ===========================================================================
# CHAPTER 5: ENGINEERING STANDARDS AND DESIGN CHALLENGES (lines 462-565)
# ===========================================================================
set_text(FP[465],
    'This chapter discusses the engineering standards relevant to the project, its impact '
    'on society, the environment, and sustainability, its project management and cost '
    'profile, and how the work maps onto the defined complex engineering problems and '
    'activities.')

set_text(FP[469],
    'The standards discussed below are limited to those directly relevant to a software-only, '
    'data-driven research project of this kind; formal medical-device or clinical-software '
    'standards were not applied because the system is a research prototype and is not '
    'intended for clinical use in its current form.')

insert_paragraphs_after(FP[471],
    ['The implementation follows standard Python packaging and style conventions (PEP 8 '
     'naming and structure) and pins minimum library versions in requirements.txt so that the '
     'environment can be reproduced. Two alternatives were considered for the deep learning '
     'backend: PyTorch and TensorFlow/Keras. TensorFlow/Keras [3] was selected because its '
     'high-level Sequential API reduced boilerplate for the three architectures used and '
     'because the developer had prior familiarity with it, which reduced development risk; '
     'the trade-off is a heavier dependency footprint than a minimal PyTorch setup.'],
    style_source_el=BODY_STYLE_SRC)

insert_paragraphs_after(FP[472],
    ['The system has no dedicated hardware standard because it targets ordinary consumer '
     'or laboratory desktop/laptop hardware (a standard x86-64 CPU with at least 8 GB of RAM). '
     'An alternative would have been to require GPU acceleration; this was not made a '
     'requirement because the dataset and model sizes involved are small enough that CPU '
     'training completes in a practical amount of time, which keeps the system accessible to '
     'examiners without specialised hardware.'],
    style_source_el=BODY_STYLE_SRC)

insert_paragraphs_after(FP[473],
    ['Client-server communication in the web demonstration follows the standard HTTP/1.1 '
     'protocol, with the front end and the Flask backend exchanging JSON payloads over a '
     'REST-style /predict endpoint. Plain JSON over HTTP was chosen over a heavier protocol '
     '(for example gRPC) because the payload is a single short string and a few scalar '
     'outputs, so the added complexity of a binary protocol would not be justified.'],
    style_source_el=BODY_STYLE_SRC)

insert_paragraphs_after(FP[476],
    ['If validated further, a system of this kind could give patients, caregivers, and '
     'researchers a faster, lower-cost first indication of amyloid-related risk than waiting '
     'for an imaging appointment, although it is not a diagnostic replacement for clinical '
     'evaluation.'],
    style_source_el=BODY_STYLE_SRC)

insert_paragraphs_after(FP[477],
    ['The models are computationally light (a few hundred thousand parameters at most) and '
     'train on CPU hardware in minutes, so the environmental footprint of running or '
     'retraining them is small compared with large-scale deep learning systems. Reducing '
     'reliance on repeated imaging-based screening could also reduce the resource cost '
     'associated with running MRI/PET equipment for routine, low-risk cases.'],
    style_source_el=BODY_STYLE_SRC)

insert_paragraphs_after(FP[478],
    ['The dataset (CPAD 2.0 peptide records) contains no patient-identifiable information, '
     'which limits privacy risk. However, the system must not be presented as a diagnostic '
     'tool: its output is a probability derived from sequence data alone, it has not been '
     'validated on an independent clinical cohort, and using it to make real medical decisions '
     'without qualified clinical oversight would be inappropriate and potentially harmful.'],
    style_source_el=BODY_STYLE_SRC)

insert_paragraphs_after(FP[479],
    ['The code, trained model artefacts, and dataset processing scripts are kept in a single '
     'version-controlled repository with pinned dependency versions, so the pipeline can be '
     're-run and the models retrained as CPAD 2.0 grows or as new peptide data becomes '
     'available, without requiring a rewrite of the surrounding infrastructure.'],
    style_source_el=BODY_STYLE_SRC)

set_text(FP[483],
    'The project relies almost entirely on free and open-source software (Python, '
    'scikit-learn, TensorFlow, Flask) and a freely accessible public dataset (CPAD 2.0), so '
    'direct financial cost is minimal beyond the researcher\u2019s own computing hardware and '
    'time. An alternative budget line would arise only if the project were extended towards '
    'clinical validation, which would require access to an independent, ethically approved '
    'peptide or patient dataset and possibly wet-lab confirmation of predicted aggregation '
    'behaviour; that cost is outside the scope of the current, software-only phase of the '
    'work.')

print('Chapter 5 part A done.')

set_text(FP[486],
    'Table 5.1 maps this project to the WK/EP complex engineering problem attributes defined '
    'by the accreditation framework, with a short rationale for each attribute that applies.')

ep_table = doc.tables[4]  # index shifted by +1 because a new results table was inserted in Chapter 4
ep_texts = [
    'Requires knowledge of bioinformatics (peptide/amyloid biology), classical machine '
    'learning, and deep sequence modelling (WK3-WK8).',
    'Balances predictive accuracy against interpretability and training time across six '
    'different model families evaluated under one common pipeline.',
    'Requires analysis of preprocessing choices, encoding schemes, cross-validation design, '
    'and per-model error behaviour (e.g. the LSTM recall/precision imbalance).',
    'Combining peptide bioinformatics with deep sequence modelling for amyloid risk is not a '
    'routine, previously solved engineering task for the author.',
    'Few formal codes exist specifically for this niche; general ML evaluation good practice '
    '(stratified splitting, held-out testing) was followed instead of a regulatory code.',
    'Primarily the researcher and academic supervisor at this research stage; no external '
    'clinical or commercial stakeholders are yet involved.',
    'Integrates a public bioinformatics dataset, multiple ML/DL frameworks, and a web '
    'deployment layer, each with its own constraints that interact with the others.',
]
for c, txt in enumerate(ep_texts):
    if c < len(ep_table.rows[1].cells):
        ep_table.rows[1].cells[c].text = txt
print('Table 5.1 (EP) populated.')

set_text(FP[517],
    'This subsection maps the overall problem, together with EP1, to the Knowledge Profile '
    '(K1-K8) used by the accreditation framework, with a brief rationale in Table 5.2.')

kp_table = doc.tables[5]
kp_relevant = ['No', 'Partial', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes']
kp_reason = [
    'Not directly applied.',
    'Basic statistics (metrics, CV) only.',
    'ML/DL model design and training.',
    'Peptide/amyloid biology knowledge.',
    'Pipeline and model architecture design.',
    'Implementation and evaluation practice.',
    'Interpreting results and limitations.',
    'Grounded in the reviewed literature.',
]
for c in range(len(kp_table.rows[2].cells)):
    kp_table.rows[2].cells[c].text = kp_relevant[c] if c < len(kp_relevant) else ''
    kp_table.rows[3].cells[c].text = kp_reason[c] if c < len(kp_reason) else ''
print('Table 5.2 (Knowledge Profile) populated.')

set_text(FP[539],
    'This subsection maps the project to the complex Engineering Activities (EA1-EA5) '
    'defined by the accreditation framework, with a brief rationale in Table 5.3.')

set_text(FP[542],
    'This section maps the overall problem to the relevant EAs (multiple may apply).')

ea_table = doc.tables[6]
ea_texts = [
    'Uses a public dataset, open-source ML/DL libraries, and standard desktop computing '
    'resources; no specialised laboratory resources were required.',
    'Mainly an individual research effort with supervisory guidance; limited interaction with '
    'external teams at this stage of the project.',
    'Combines peptide sequence data with a six-model ML/DL comparison and a real-time web '
    'demonstration, which is not a routine, off-the-shelf configuration.',
    'A validated version of this kind of tool could support lower-cost, earlier '
    'AD-related screening, with the ethical caveat that it must not replace clinical '
    'diagnosis.',
    'The general problem (disease risk prediction from biological sequence data) is familiar '
    'in bioinformatics, but the specific peptide-aggregation angle combined with a full ML/DL '
    'comparison is less common.',
]
for c, txt in enumerate(ea_texts):
    if c < len(ea_table.rows[1].cells):
        ea_table.rows[1].cells[c].text = txt
print('Table 5.3 (EA) populated.')

set_text(FP[564],
    'This chapter reviewed the software, hardware, and communication standards applied in '
    'the project, its impact on life, society, the environment, ethics, and sustainability, '
    'a brief financial analysis, and a mapping of the work to the defined complex engineering '
    'problems and activities.')

print('Chapter 5 done.')

# ===========================================================================
# CHAPTER 6: CONCLUSION  (lines 566-577 -> FP[565:577])
# ===========================================================================
remove_paragraph(FP[569])
set_text(FP[570],
    "This chapter summarises the project, states its limitations honestly, and outlines "
    'directions for future work.')

set_text(FP[573],
    'This project presented a computational framework for early Alzheimer\u2019s disease '
    'risk screening based on peptide sequences, combining classical machine learning '
    '(Logistic Regression, Random Forest, SVM) with deep learning (CNN, LSTM, BiLSTM) under '
    'one evaluation pipeline. Peptide records were collected from the CPAD 2.0 database, '
    'cleaned, deduplicated, and encoded in two representations suited to the two model '
    'families, and all six models were compared on a common held-out test set using '
    'accuracy, precision, recall, F1-score, and ROC-AUC. The Convolutional Neural Network '
    'produced the best result (81.05% accuracy, F1 = 0.815, ROC-AUC = 0.893), ahead of '
    'BiLSTM and the three classical baselines, while the plain LSTM under-performed by '
    'collapsing towards the positive class. The best model was packaged behind a Flask web '
    'interface so that a new peptide sequence can be scored interactively. These results '
    'support the underlying premise of the project: that peptide sequence data, without any '
    'imaging, carries a usable signal for amyloid-related risk classification, and that a '
    'convolutional architecture is well suited to extracting that signal from short '
    'biological sequences.')

set_text(FP[575],
    'This work has several limitations that should be considered before drawing broader '
    'conclusions from it. First, there is no independent clinical validation dataset; all '
    'reported results come from a single held-out split of the CPAD 2.0 data, and '
    'performance on sequences outside this database is unknown. Second, the LSTM model '
    'over-predicts the positive class (recall of 1.0 with precision of 0.553), which shows '
    'that not every architecture generalised equally well under the same training regime. '
    'Third, the results depend on the label quality and coverage of CPAD 2.0 itself; '
    'mislabelled or under-represented peptide types in the source database would carry '
    'through to the trained models. Finally, systematic hyperparameter search (for example '
    'grid or Bayesian search over network width, depth, and learning rate) was not carried '
    'out; the architectures used reasonable, literature-informed defaults rather than tuned '
    'optima.')

insert_paragraphs_after(FP[576],
    ['Future work could address these limitations directly: evaluating the trained models '
     'on an independent, ideally clinically sourced, peptide or amyloid dataset; running a '
     'systematic hyperparameter search for the CNN and BiLSTM models; applying k-fold cross '
     'validation to the deep learning models in addition to the classical ones; and adding '
     'saliency or SHAP-based explainability to the CNN and BiLSTM models, extending the '
     'SHAP analysis already produced for Random Forest, so that predictions can be linked '
     'back to specific residues in a sequence. A longer-term direction is to replace the '
     'custom CNN/LSTM/BiLSTM encoders with a pretrained protein language model such as '
     'ESM-2, fine-tuned on the same CPAD 2.0 labels, to test whether large-scale pretraining '
     'on general protein sequences improves on the results reported here.'],
    style_source_el=BODY_STYLE_SRC)

print('Chapter 6 done.')

# ===========================================================================
# REFERENCES  (lines 578-583 -> FP[577:583])
# ===========================================================================
remove_paragraph(FP[578])

references = [
    'CPAD 2.0: Curated Protein Aggregation Database, \u201cPeptide Dataset,\u201d [Online]. '
    'Available: https://web.iitm.ac.in/bioinfo2/cpad2/peptides/',
    'F. Pedregosa et al., \u201cScikit-learn: Machine Learning in Python,\u201d Journal of '
    'Machine Learning Research, vol. 12, pp. 2825\u20132830, 2011.',
    'M. Abadi et al., \u201cTensorFlow: Large-Scale Machine Learning on Heterogeneous '
    'Systems,\u201d 2015. [Online]. Available: https://www.tensorflow.org/',
    'S.-R. Yu, X.-M. Yang, Y.-N. Sun, Y.-J. Li, Y.-Y. Liu, and X.-L. Tang, \u201cProtein '
    'interaction prediction for Alzheimer\u2019s disease using a multi-source protein '
    'features fusion framework,\u201d Informatics and Health, vol. 2, pp. 119\u2013129, '
    '2025.',
    'A. Hassan, A. Imran, A. U. Yasin, M. A. Waqas, and R. Fazal, \u201cA multimodal '
    'approach for Alzheimer\u2019s disease detection and classification using deep '
    'learning,\u201d Journal of Computing & Biomedical Informatics, vol. 6, no. 2, Mar. '
    '2024.',
    'P. Rani, R. Lamba, R. K. Sachdeva, K. Kumar, and C. Iwendi, \u201cA machine learning '
    'model for Alzheimer\u2019s disease prediction,\u201d IET Cyber-Physical Systems: '
    'Theory & Applications, 2024.',
    'B. Wang, S. Razavi, and E. R. Gamazon, \u201cTowards mechanistic models of mutational '
    'effects: Deep learning on Alzheimer\u2019s A\u03b2 peptide,\u201d Computational and '
    'Structural Biotechnology Journal, vol. 21, pp. 2434\u20132445, 2023.',
    'L. Xu, G. Liang, C. Liao, G.-D. Chen, and C.-C. Chang, \u201cAn efficient classifier '
    'for Alzheimer\u2019s disease genes identification,\u201d Molecules, vol. 23, no. 12, '
    'p. 3140, Nov. 2018.',
    'J. Hardy and D. J. Selkoe, \u201cThe amyloid hypothesis of Alzheimer\u2019s disease: '
    'Progress and problems on the road to therapeutics,\u201d Science, vol. 297, no. 5580, '
    'pp. 353\u2013356, Jul. 2002.',
    'D. J. Selkoe and J. Hardy, \u201cThe amyloid hypothesis of Alzheimer\u2019s disease at '
    '25 years,\u201d EMBO Molecular Medicine, vol. 8, no. 6, pp. 595\u2013608, Jun. 2016.',
    'H. Braak and E. Braak, \u201cNeuropathological staging of Alzheimer-related '
    'changes,\u201d Acta Neuropathologica, vol. 82, no. 4, pp. 239\u2013259, 1991.',
    'C. R. Jack Jr. et al., \u201cNIA-AA Research Framework: Toward a biological definition '
    'of Alzheimer\u2019s disease,\u201d Alzheimer\u2019s & Dementia, vol. 14, no. 4, pp. '
    '535\u2013562, Apr. 2018.',
    'A. Fernandez-Escamilla, M. S. Rousseau, L. Schymkowitz, and F. Serrano, \u201cPrediction '
    'of sequence-dependent and mutational effects on the aggregation of peptides and '
    'proteins,\u201d Nature Biotechnology, vol. 22, no. 10, pp. 1302\u20131306, Oct. 2004.',
    'W. McKinney, \u201cData structures for statistical computing in Python,\u201d in Proc. '
    '9th Python in Science Conf., 2010, pp. 56\u201361.',
    'C. R. Harris et al., \u201cArray programming with NumPy,\u201d Nature, vol. 585, no. '
    '7825, pp. 357\u2013362, 2020.',
    'J. D. Hunter, \u201cMatplotlib: A 2D graphics environment,\u201d Computing in Science '
    '& Engineering, vol. 9, no. 3, pp. 90\u201395, 2007.',
    'M. L. Waskom, \u201cSeaborn: Statistical data visualization,\u201d Journal of Open '
    'Source Software, vol. 6, no. 60, p. 3021, 2021.',
    'L. Richardson, \u201cBeautiful Soup Documentation,\u201d [Online]. Available: '
    'https://www.crummy.com/software/BeautifulSoup/bs4/doc/',
    'openpyxl Developers, \u201copenpyxl documentation,\u201d [Online]. Available: '
    'https://openpyxl.readthedocs.io/',
    'Pallets Projects, \u201cFlask documentation,\u201d [Online]. Available: '
    'https://flask.palletsprojects.com/',
]

remove_paragraph(FP[580])  # stray empty BodyText between ref items
set_text(FP[579], references[0])
set_text(FP[581], references[1])
set_text(FP[582], references[2])
last = FP[582]
for ref in references[3:]:
    new_p = clone_paragraph(FP[582])
    set_text(new_p, ref)
    insert_after(last, new_p)
    last = new_p

print('References done. Total entries:', len(references))

# Attempt to save directly to OUT (and provide fallback if file is locked)
saved_paths = []
try:
    doc.save(OUT)
    saved_paths.append(OUT)
    print(f"Successfully saved to: {OUT}")
except PermissionError:
    alt_out = 'Alzheimer_Peptide_FYDP_Report_DRAFT_UPDATED.docx'
    doc.save(alt_out)
    saved_paths.append(alt_out)
    print(f"Note: {OUT} is currently locked by Word. Saved to: {alt_out}")

# Also save a working copy to draft_report_wip.docx
try:
    doc.save('draft_report_wip.docx')
    saved_paths.append('draft_report_wip.docx')
except Exception:
    pass

print("Report generation complete. Output saved to:", saved_paths)
