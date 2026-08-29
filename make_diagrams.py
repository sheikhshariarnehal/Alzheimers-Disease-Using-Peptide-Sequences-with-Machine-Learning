"""Generate simple, real (non-decorative) pipeline / DFD diagrams for the report,
based on the actual implemented pipeline in alzheimer_peptide_model.py."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

os.makedirs('report_figures', exist_ok=True)

plt.rcParams.update({'font.family': 'DejaVu Sans'})


def draw_box(ax, xy, w, h, text, fc='#eef3fb', ec='#2c5f8a', fontsize=9.5):
    box = FancyBboxPatch(xy, w, h, boxstyle="round,pad=0.02,rounding_size=0.02",
                          linewidth=1.2, edgecolor=ec, facecolor=fc)
    ax.add_patch(box)
    cx, cy = xy[0] + w / 2, xy[1] + h / 2
    ax.text(cx, cy, text, ha='center', va='center', fontsize=fontsize, color='#12233a', wrap=True)
    return cx, cy


def arrow(ax, p1, p2):
    a = FancyArrowPatch(p1, p2, arrowstyle='-|>', mutation_scale=14,
                         linewidth=1.2, color='#444444')
    ax.add_patch(a)


# ---------------------------------------------------------------------------
# Figure 3.1 : End-to-end system pipeline
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9.5, 5.2))
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)
ax.axis('off')

stages = [
    ("CPAD 2.0\npeptide records\n(web scraping)", 0.3, 4.6),
    ("Data cleaning\n& deduplication\n(2,001 -> unique\npeptides)", 2.55, 4.6),
    ("Label\nstandardisation\n(amyloid /\nnon-amyloid)", 4.8, 4.6),
    ("Sequence encoding\n(integer padding\n+ one-hot)", 7.05, 4.6),
    ("Stratified\n80/20 train-test\nsplit", 7.05, 1.8),
    ("ML training\n(LR, RF, SVM)\n5-fold CV", 4.8, 1.8),
    ("DL training\n(CNN, LSTM,\nBiLSTM)", 2.55, 1.8),
    ("Evaluation\n(Accuracy, P, R,\nF1, ROC-AUC)\n+ model selection", 0.3, 1.8),
]
w, h = 2.0, 1.15
centers = []
for text, x, y in stages:
    c = draw_box(ax, (x, y), w, h, text)
    centers.append(c)

# top row arrows
for i in range(3):
    arrow(ax, (stages[i][1] + w, stages[i][2] + h / 2), (stages[i + 1][1], stages[i + 1][2] + h / 2))
# down to split
arrow(ax, (stages[3][1] + w / 2, stages[3][2]), (stages[4][1] + w / 2, stages[4][2] + h))
# split -> ML, split -> DL
arrow(ax, (stages[4][1], stages[4][2] + h / 2), (stages[5][1] + w, stages[5][2] + h / 2))
arrow(ax, (stages[5][1], stages[5][2] + h / 2), (stages[6][1] + w, stages[6][2] + h / 2))
# ML, DL -> evaluation
arrow(ax, (stages[6][1], stages[6][2] + h / 2), (stages[7][1] + w, stages[7][2] + h / 2))
arrow(ax, (stages[5][1] + w / 2, stages[5][2]), (stages[7][1] + w * 1.5, stages[7][2] + h))

ax.set_title("Figure 3.1: End-to-end pipeline implemented in alzheimer_peptide_model.py", fontsize=10)
fig.tight_layout()
fig.savefig('report_figures/fig_3_1_pipeline.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 3.2 : Data flow diagram (Level 0/1) for the prediction system
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 4.6))
ax.set_xlim(0, 10)
ax.set_ylim(0, 5)
ax.axis('off')

# External entity: user
ux, uy = 0.3, 2.1
draw_box(ax, (ux, uy), 1.6, 0.9, "User /\nExaminer", fc='#f6e9d7', ec='#a97121')

# Process 1: Flask web app
p1x, p1y = 2.6, 2.1
draw_box(ax, (p1x, p1y), 2.1, 0.9, "P1: Flask app\n(app.py)\n/predict endpoint", fc='#e4f0e6', ec='#2e7d4f')

# Data store: metadata + saved models
dsx, dsy = 5.4, 3.4
draw_box(ax, (dsx, dsy), 2.3, 0.9, "D1: Saved models &\nmetadata.pkl\n(models/)", fc='#eef1f7', ec='#3b4b6b')

# Process 2: encode + predict
p2x, p2y = 5.4, 1.0
draw_box(ax, (p2x, p2y), 2.3, 0.9, "P2: Encode sequence &\nrun model inference", fc='#e4f0e6', ec='#2e7d4f')

# External: response
rx, ry = 8.4, 2.1
draw_box(ax, (rx, ry), 1.4, 0.9, "Prediction\n+ probability\n+ risk level", fc='#f6e9d7', ec='#a97121')

arrow(ax, (ux + 1.6, uy + 0.45), (p1x, p1y + 0.45))
arrow(ax, (p1x + 2.1, p1y + 0.7), (dsx, dsy + 0.3))
arrow(ax, (p1x + 2.1, p1y + 0.2), (p2x, p2y + 0.6))
arrow(ax, (dsx + 0.2, dsy), (p2x + 0.2, p2y + 0.9))
arrow(ax, (p2x + 2.3, p2y + 0.45), (rx, ry + 0.45))
arrow(ax, (rx, ry + 0.2), (p1x + 2.1, p1y + 0.2))

ax.set_title("Figure 3.2: Data flow diagram of the prediction (web demo) subsystem", fontsize=10)
fig.tight_layout()
fig.savefig('report_figures/fig_3_2_dfd.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.close(fig)

print("Diagrams saved to report_figures/")
