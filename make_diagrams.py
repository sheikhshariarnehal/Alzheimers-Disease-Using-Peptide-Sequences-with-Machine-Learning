"""Generate clean, publication-grade pipeline and DFD diagrams for the FYDP report."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

os.makedirs('report_figures', exist_ok=True)

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'DejaVu Sans', 'Helvetica'],
})


def draw_card(ax, xy, w, h, title, subtitle, fc='#F0F4F9', ec='#1A73E8', title_color='#174EA6', sub_color='#3C4043', title_size=9.2, sub_size=7.8):
    box = FancyBboxPatch(xy, w, h, boxstyle='round,pad=0.02,rounding_size=0.04',
                          linewidth=1.3, edgecolor=ec, facecolor=fc, zorder=3)
    ax.add_patch(box)
    cx, cy = xy[0] + w / 2, xy[1] + h / 2
    if subtitle:
        ax.text(cx, cy + h * 0.15, title, ha='center', va='center', fontsize=title_size, fontweight='bold', color=title_color, zorder=4)
        ax.text(cx, cy - h * 0.18, subtitle, ha='center', va='center', fontsize=sub_size, color=sub_color, zorder=4)
    else:
        ax.text(cx, cy, title, ha='center', va='center', fontsize=title_size, fontweight='bold', color=title_color, zorder=4)
    return cx, cy


def draw_arrow(ax, p1, p2, color='#5F6368', lw=1.3):
    a = FancyArrowPatch(p1, p2, arrowstyle='-|>', mutation_scale=12,
                         linewidth=lw, color=color, zorder=2)
    ax.add_patch(a)


# ---------------------------------------------------------------------------
# Figure 3.1 : End-to-End System Pipeline
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10.5, 5.2), dpi=300)
ax.set_xlim(0, 10.5)
ax.set_ylim(0, 5.6)
ax.axis('off')

# Stage 1: Data Preprocessing (Top Row)
draw_card(ax, (0.3, 3.8), 2.1, 1.3, 'CPAD 2.0 Database', '2,001 Raw Sequences\nScraped from Web', fc='#E8F0FE', ec='#1A73E8', title_color='#174EA6')
draw_card(ax, (2.8, 3.8), 2.2, 1.3, 'Data Preprocessing', 'Deduplication &\nLabel Standardisation', fc='#E8F0FE', ec='#1A73E8', title_color='#174EA6')
draw_card(ax, (5.4, 3.8), 2.2, 1.3, 'Sequence Encoding', 'Padded Integer (DL) &\nOne-Hot Vectors (ML)', fc='#E8F0FE', ec='#1A73E8', title_color='#174EA6')
draw_card(ax, (8.0, 3.8), 2.2, 1.3, 'Dataset Splitting', 'Stratified 80/20\nTrain-Test Partition', fc='#FEF7E0', ec='#F29900', title_color='#B06000')

# Top Row Arrows
draw_arrow(ax, (2.4, 4.45), (2.8, 4.45))
draw_arrow(ax, (5.0, 4.45), (5.4, 4.45))
draw_arrow(ax, (7.6, 4.45), (8.0, 4.45))

# Branching arrows down from Split
draw_arrow(ax, (9.1, 3.8), (9.1, 2.9))
draw_arrow(ax, (9.1, 2.9), (7.8, 2.9))
draw_arrow(ax, (9.1, 2.9), (7.8, 1.2))

# Stage 2: Model Training Branches
draw_card(ax, (5.4, 2.3), 2.4, 1.2, 'Classical ML Models', 'LR, RF, SVM\n(5-Fold Cross-Validation)', fc='#E6F4EA', ec='#137333', title_color='#0D652D')
draw_card(ax, (5.4, 0.6), 2.4, 1.2, 'Deep Learning Models', 'CNN, LSTM, BiLSTM\n(Val Split & Early Stopping)', fc='#E6F4EA', ec='#137333', title_color='#0D652D')

# Connecting Training Branches to Evaluation
draw_arrow(ax, (5.4, 2.9), (4.5, 2.3))
draw_arrow(ax, (5.4, 1.2), (4.5, 1.7))

# Stage 3: Evaluation & Selection
draw_card(ax, (2.1, 1.3), 2.4, 1.4, 'Model Evaluation', 'Held-Out Test Set (F1 & AUC)\n→ Best Model: CNN (81.05%)', fc='#FCE8E6', ec='#D93025', title_color='#C5221F')

# Stage 4: Deployment
draw_arrow(ax, (2.1, 2.0), (1.5, 2.0))
draw_card(ax, (0.3, 1.3), 1.2, 1.4, 'Web Demo', 'Flask App\n(app.py)', fc='#F3E8FD', ec='#9334E6', title_color='#7627BB')

fig.tight_layout()
fig.savefig('report_figures/fig_3_1_pipeline.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 3.2 : Data Flow Diagram (Level 1)
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10.5, 4.4), dpi=300)
ax.set_xlim(0, 10.5)
ax.set_ylim(0, 4.5)
ax.axis('off')

# 1. User Entity (Left)
draw_card(ax, (0.3, 1.3), 1.6, 1.2, 'User / Client', 'Browser Interface', fc='#FEF7E0', ec='#F29900', title_color='#B06000')

# Arrow: User -> Process 1.0
draw_arrow(ax, (1.9, 1.9), (2.6, 1.9))
ax.text(2.25, 2.15, 'Peptide\nString', ha='center', fontsize=7.5, color='#444444', fontweight='bold')

# 2. Process 1.0 (Validation)
draw_card(ax, (2.6, 1.3), 2.1, 1.2, '1.0 Input Validation', 'FASTA & Alphabet Filter\n(Flask /predict)', fc='#E8F0FE', ec='#1A73E8', title_color='#174EA6')

# Arrow: Process 1.0 -> Process 2.0
draw_arrow(ax, (4.7, 1.9), (5.4, 1.9))
ax.text(5.05, 2.15, 'Validated\nSequence', ha='center', fontsize=7.5, color='#444444', fontweight='bold')

# Data Store (D1) directly above Process 2.0
draw_card(ax, (5.4, 2.9), 2.3, 1.1, 'D1: Model Repository', 'Saved Weights & Vocab\n(models/ directory)', fc='#F1F3F4', ec='#5F6368', title_color='#202124')

# Arrow: D1 -> Process 2.0 (Read weights)
draw_arrow(ax, (6.55, 2.9), (6.55, 2.5))
ax.text(6.85, 2.7, 'Load Weights', ha='left', fontsize=7.0, color='#5F6368')

# 3. Process 2.0 (Encoding & Inference)
draw_card(ax, (5.4, 1.3), 2.3, 1.2, '2.0 Inference Engine', 'Encoding & Forward Pass\n(CNN / BiLSTM / ML)', fc='#E6F4EA', ec='#137333', title_color='#0D652D')

# Arrow: Process 2.0 -> Process 3.0
draw_arrow(ax, (7.7, 1.9), (8.4, 1.9))
ax.text(8.05, 2.15, 'Prediction\n& Score', ha='center', fontsize=7.5, color='#444444', fontweight='bold')

# 4. Process 3.0 / UI Output (Right)
draw_card(ax, (8.4, 1.3), 1.8, 1.2, '3.0 Risk Dashboard', 'Probability & Badge\n(Low / Medium / High)', fc='#FCE8E6', ec='#D93025', title_color='#C5221F')

fig.tight_layout()
fig.savefig('report_figures/fig_3_2_dfd.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close(fig)

print("Diagrams successfully generated with clean two-tier card typography.")
