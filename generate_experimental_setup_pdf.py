#!/usr/bin/env python3
"""
Generate Experimental_Setup.pdf for Master Thesis.
Matches the style of Methodology_Section.pdf (A4, ReportLab).
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.colors import black, HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.lib import colors

PAGE_W, PAGE_H = A4  # 595.27 x 841.89 points

def build_styles():
    """Build paragraph styles matching Methodology_Section.pdf."""
    ss = getSampleStyleSheet()

    title = ParagraphStyle(
        "Title1",
        parent=ss["Title"],
        fontName="Times-Bold",
        fontSize=18,
        leading=24,
        spaceAfter=18,
        alignment=TA_LEFT,
    )
    heading2 = ParagraphStyle(
        "H2",
        fontName="Times-Bold",
        fontSize=13,
        leading=17,
        spaceBefore=14,
        spaceAfter=6,
        textColor=black,
    )
    heading3 = ParagraphStyle(
        "H3",
        fontName="Times-Bold",
        fontSize=11,
        leading=14,
        spaceBefore=10,
        spaceAfter=4,
        textColor=black,
    )
    body = ParagraphStyle(
        "Body1",
        fontName="Times-Roman",
        fontSize=10.5,
        leading=14,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
    )
    body_indent = ParagraphStyle(
        "BodyIndent",
        parent=body,
        leftIndent=18,
    )
    bullet = ParagraphStyle(
        "Bullet1",
        parent=body,
        leftIndent=24,
        bulletIndent=12,
        spaceAfter=3,
    )
    code_style = ParagraphStyle(
        "Code",
        fontName="Courier",
        fontSize=8.5,
        leading=11,
        leftIndent=18,
        spaceAfter=4,
        textColor=HexColor("#333333"),
    )
    table_header_style = ParagraphStyle(
        "TableHeader",
        fontName="Times-Bold",
        fontSize=9.5,
        leading=12,
        alignment=TA_CENTER,
    )
    table_cell_style = ParagraphStyle(
        "TableCell",
        fontName="Times-Roman",
        fontSize=9.5,
        leading=12,
        alignment=TA_CENTER,
    )
    table_cell_left = ParagraphStyle(
        "TableCellLeft",
        fontName="Times-Roman",
        fontSize=9.5,
        leading=12,
        alignment=TA_LEFT,
    )
    caption = ParagraphStyle(
        "Caption",
        fontName="Times-Bold",
        fontSize=10,
        leading=13,
        spaceBefore=6,
        spaceAfter=6,
        alignment=TA_LEFT,
    )
    return dict(
        title=title, h2=heading2, h3=heading3,
        body=body, body_indent=body_indent, bullet=bullet,
        code=code_style, th=table_header_style,
        tc=table_cell_style, tcl=table_cell_left,
        caption=caption,
    )


def make_table(header_row, data_rows, col_widths, styles_dict):
    """Helper to create a formatted table."""
    th = styles_dict["th"]
    tc = styles_dict["tc"]
    tcl = styles_dict["tcl"]

    table_data = [[Paragraph(c, th) for c in header_row]]
    for row in data_rows:
        cells = []
        for i, c in enumerate(row):
            style = tcl if i == 0 else tc
            cells.append(Paragraph(str(c), style))
        table_data.append(cells)

    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#E8E8E8")),
        ("TEXTCOLOR", (0, 0), (-1, 0), black),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, HexColor("#F7F7F7")]),
    ]))
    return t


def build_story(s):
    """Build the document story (list of flowables)."""
    story = []
    sp = Spacer(1, 8)

    # ── Title ──────────────────────────────────────────────────
    story.append(Paragraph("Experimental Setup", s["title"]))
    story.append(Spacer(1, 4))

    # ── 4.1 Overview ──────────────────────────────────────────
    story.append(Paragraph("4.1 Overview", s["h2"]))
    story.append(Paragraph(
        "This chapter details the complete experimental setup used to evaluate the accuracy\u2013privacy "
        "trade-offs in federated learning for mobile movie recommendation systems. The experiments "
        "are designed to answer three research questions: (RQ1) the impact of differential privacy "
        "budgets on recommendation accuracy, (RQ2) the effectiveness of privacy attacks under varying "
        "DP configurations, and (RQ3) the influence of data heterogeneity on federated learning "
        "performance. The experimental pipeline encompasses dataset preparation, non-IID data "
        "partitioning, in-memory federated learning simulation, differential privacy integration, "
        "privacy attack evaluation, and comprehensive metric collection. A companion mobile client "
        "built with Flutter demonstrates real-device deployment feasibility.", s["body"]))

    # ── 4.2 Hardware and Software Environment ─────────────────
    story.append(Paragraph("4.2 Hardware and Software Environment", s["h2"]))

    story.append(Paragraph("4.2.1 Computation Platform", s["h3"]))
    story.append(Paragraph(
        "All experiments are executed on a single workstation equipped with a multi-core CPU. "
        "No GPU acceleration is employed; the relatively compact model size (approximately 168K "
        "parameters) and the moderate dataset scale (100K interactions) make CPU-only training "
        "practical. The complete experiment suite of 30 configurations finishes in approximately "
        "2.5\u20133 hours of wall-clock time. Peak memory consumption is approximately 4 GB RAM per "
        "full experiment run, and the aggregate disk footprint for all result artifacts (JSON, CSV, "
        "and PNG figures) is under 500 MB.", s["body"]))

    story.append(Paragraph("4.2.2 Software Stack", s["h3"]))
    story.append(Paragraph(
        "The server-side implementation is written entirely in Python. The core deep-learning "
        "framework is PyTorch, which handles model definition, forward and backward passes, "
        "and gradient manipulation for DP-SGD. NumPy is used for data partitioning via the "
        "Dirichlet distribution and general numerical operations. Pandas handles tabular data "
        "loading and result aggregation. Scikit-learn provides the Random Forest classifier "
        "used in the membership inference attack as well as standard evaluation utilities "
        "(e.g., roc_auc_score). Matplotlib and Seaborn generate all publication-quality figures. "
        "FastAPI powers the optional HTTP-based server for distributed and mobile client "
        "deployment.", s["body"]))

    # Table: Software dependencies
    story.append(Paragraph("Table 3: Core Software Dependencies", s["caption"]))
    story.append(make_table(
        ["Component", "Library / Framework", "Version", "Purpose"],
        [
            ["Deep Learning", "PyTorch", "\u2265 2.0.0", "Model training, DP-SGD gradient operations"],
            ["Numerical", "NumPy", "\u2265 1.24.0", "Dirichlet partitioning, array operations"],
            ["Data Processing", "Pandas", "\u2265 2.0.0", "CSV loading, result aggregation"],
            ["ML Utilities", "Scikit-learn", "\u2265 1.3.0", "Attack classifier, AUC computation"],
            ["Visualization", "Matplotlib / Seaborn", "\u2265 3.7 / \u2265 0.12", "Publication-quality figures"],
            ["HTTP Server", "FastAPI / Uvicorn", "Latest", "Distributed FL deployment"],
            ["Mobile Client", "Flutter SDK", "\u2265 3.9.2", "Android on-device training app"],
        ],
        [90, 120, 70, 195],
        s,
    ))
    story.append(sp)

    # ── 4.3 Dataset Preparation ───────────────────────────────
    story.append(Paragraph("4.3 Dataset Preparation", s["h2"]))

    story.append(Paragraph("4.3.1 Data Loading and Preprocessing", s["h3"]))
    story.append(Paragraph(
        "The MovieLens 100K dataset is loaded from a CSV file containing four columns: "
        "<i>userId</i>, <i>movieId</i>, <i>rating</i>, and <i>timestamp</i>. User and item "
        "identifiers are re-mapped to zero-indexed integers to serve as direct indices into "
        "the embedding layers. After re-mapping, the dataset comprises 943 unique users, "
        "1,682 unique items, and 100,000 interaction records. Ratings are retained on their "
        "original 1\u20135 continuous scale for the regression-based evaluation pipeline; for "
        "the binary classification variant used in certain attack evaluations, ratings are "
        "binarized with a threshold of 4.0 (ratings \u2265 4.0 \u2192 1.0; otherwise \u2192 0.0).", s["body"]))

    story.append(Paragraph("4.3.2 Train\u2013Test Split", s["h3"]))
    story.append(Paragraph(
        "The 100,000 interactions are split into 80% training (80,000 interactions) and 20% "
        "test (20,000 interactions) sets via a random permutation with a fixed seed. The split "
        "is performed at the interaction level rather than the user level, ensuring that every "
        "user has some ratings in both the training and test sets. This enables per-user "
        "recommendation metric computation on the test set.", s["body"]))

    story.append(Paragraph("4.3.3 Non-IID Data Partitioning via Dirichlet Distribution", s["h3"]))
    story.append(Paragraph(
        "To simulate realistic mobile data distributions where each device holds a distinct "
        "and non-overlapping subset of user interactions, the 80,000 training interactions are "
        "partitioned among <i>K</i> = 100 simulated clients using a Dirichlet distribution "
        "with concentration parameter \u03b1. The partitioning proceeds as follows:", s["body"]))
    story.append(Paragraph(
        "<b>Step 1 \u2013 Group by User:</b> Interactions are grouped by user ID, yielding up to "
        "943 groups.", s["bullet"]))
    story.append(Paragraph(
        "<b>Step 2 \u2013 Sample Proportions:</b> For each user, a probability vector "
        "<b>p</b> \u223c Dir(\u03b1, \u03b1, \u2026, \u03b1) with <i>K</i> = 100 components is drawn. "
        "Each component <i>p<sub>k</sub></i> represents the fraction of that user\u2019s interactions "
        "assigned to client <i>k</i>.", s["bullet"]))
    story.append(Paragraph(
        "<b>Step 3 \u2013 Assign Interactions:</b> Each interaction is independently assigned to a "
        "client according to the sampled proportions. This introduces controlled heterogeneity: "
        "a small \u03b1 concentrates most of a user\u2019s data on one or two clients, while a larger "
        "\u03b1 distributes it more evenly.", s["bullet"]))
    story.append(Paragraph(
        "The resulting partition is inherently imbalanced. With \u03b1 = 0.5 (the default), client "
        "dataset sizes range from roughly 100 to 1,500 interactions, with a mean of 800. This "
        "imbalance is representative of production mobile deployments where user activity levels "
        "vary widely.", s["body"]))
    story.append(sp)

    # Table: Alpha configurations
    story.append(Paragraph("Table 4: Dirichlet Concentration Parameter Configurations", s["caption"]))
    story.append(make_table(
        ["\u03b1 Value", "Heterogeneity Level", "Typical Client Profile", "Use Case"],
        [
            ["0.1", "Highly Non-IID",
             "Most clients receive data from 1\u20132 users only",
             "RQ3: extreme heterogeneity"],
            ["0.5", "Moderately Non-IID",
             "Clients receive data from several users with overlap",
             "Default for RQ1, RQ2"],
            ["1.0", "Mildly Non-IID",
             "Data distributed more uniformly, approaching IID",
             "RQ3: low heterogeneity"],
        ],
        [55, 100, 210, 115],
        s,
    ))
    story.append(sp)

    # ── 4.4 Federated Learning Simulation Environment ─────────
    story.append(Paragraph("4.4 Federated Learning Simulation Environment", s["h2"]))

    story.append(Paragraph("4.4.1 In-Memory Simulation Architecture", s["h3"]))
    story.append(Paragraph(
        "The federated learning experiments are conducted using an in-memory simulation that "
        "faithfully replicates the Federated Averaging (FedAvg) protocol without incurring "
        "network latency or serialization overhead. In each communication round, every client "
        "receives a deep copy of the current global model\u2019s state dictionary, performs local "
        "training on its private data partition, and returns the updated state dictionary to the "
        "server. The server then performs weighted averaging (Section 3.4 of the Methodology) to "
        "produce the next global model. This design enables the complete 30-experiment suite to "
        "execute on a single machine while remaining functionally equivalent to a distributed "
        "deployment.", s["body"]))

    story.append(Paragraph("4.4.2 Per-Round Execution Flow", s["h3"]))
    story.append(Paragraph(
        "Each federated learning round executes the following steps:", s["body"]))
    story.append(Paragraph(
        "<b>1. Model Distribution:</b> The global model\u2019s state dictionary is deep-copied to "
        "each of the 100 clients. Each client instantiates a fresh <i>MatrixFactorization</i> "
        "module and loads the copied parameters.", s["bullet"]))
    story.append(Paragraph(
        "<b>2. Local Training:</b> Each client trains on its local data partition for "
        "<i>E</i> = 3 local epochs using SGD (learning rate 0.01, weight decay 10<super>\u22125</super>, "
        "batch size 32). The loss function is Mean Squared Error (MSE) for the regression variant "
        "or Binary Cross-Entropy (BCE) for the binary variant. If differential privacy is enabled, "
        "DP-SGD gradient clipping and noise injection are applied after each backward pass.", s["bullet"]))
    story.append(Paragraph(
        "<b>3. Parameter Collection:</b> Each client\u2019s updated state dictionary and local "
        "sample count are collected.", s["bullet"]))
    story.append(Paragraph(
        "<b>4. FedAvg Aggregation:</b> The server computes the weighted average of all client "
        "parameters using sample-count proportional weighting: "
        "<i>w</i><sub>global</sub> = \u03a3<sub>k</sub> (<i>n<sub>k</sub></i> / <i>n</i><sub>total</sub>) \u00b7 <i>w<sub>k</sub></i>.", s["bullet"]))
    story.append(Paragraph(
        "<b>5. Evaluation:</b> The aggregated global model is evaluated on the held-out test set. "
        "Full evaluation (including recommendation metrics) is performed at key checkpoints "
        "(rounds 1, 5, and 10) to reduce computational overhead, while basic regression metrics "
        "(MSE, MAE) are computed every round.", s["bullet"]))
    story.append(Paragraph(
        "<b>6. Logging:</b> Round-level metrics are appended to an in-memory collector and "
        "persisted to disk as JSON and CSV at the end of the experiment.", s["bullet"]))
    story.append(sp)

    # ── 4.5 Differential Privacy Integration ──────────────────
    story.append(Paragraph("4.5 Differential Privacy Integration", s["h2"]))

    story.append(Paragraph("4.5.1 DP-SGD Implementation Details", s["h3"]))
    story.append(Paragraph(
        "Differential privacy is enforced at the gradient level during local client training. "
        "After each backward pass, two operations are applied sequentially:", s["body"]))
    story.append(Paragraph(
        "<b>Per-Parameter Gradient Clipping:</b> The L2 norm of the full gradient vector "
        "(concatenated across all model parameters) is computed. If the norm exceeds the clipping "
        "threshold <i>C</i> = 1.0, all per-parameter gradients are scaled down by the factor "
        "<i>C</i> / (||<i>g</i>||<sub>2</sub> + 10<super>\u22126</super>). This bounds the maximum "
        "contribution of any single training sample to the model update.", s["bullet"]))
    story.append(Paragraph(
        "<b>Gaussian Noise Injection:</b> After clipping, independent Gaussian noise drawn from "
        "\U0001d4a9(0, \u03c3\u00b2 \u00b7 <i>C</i>\u00b2 \u00b7 <b>I</b>) is added to each parameter\u2019s "
        "gradient. The noise multiplier \u03c3 is pre-computed to achieve the target privacy budget "
        "\u03b5 given the number of training steps, batch size, and dataset size.", s["bullet"]))
    story.append(Paragraph(
        "The clipping and noise operations are applied at every gradient step within the local "
        "training loop, ensuring that each mini-batch update satisfies the local DP guarantee. "
        "The cumulative privacy loss across all rounds is tracked by the RDP accountant.", s["body"]))

    story.append(Paragraph("4.5.2 Privacy Budget Calibration", s["h3"]))
    story.append(Paragraph(
        "The noise multiplier \u03c3 for each target \u03b5 is computed using the R\u00e9nyi Differential "
        "Privacy (RDP) accountant. The accountant evaluates the RDP guarantee at a range of "
        "R\u00e9nyi orders \u03b1 \u2208 {1.1, 1.2, \u2026, 1.9, 2, 3, \u2026, 64} and converts the tightest "
        "bound to (\u03b5, \u03b4)-DP with \u03b4 = 10<super>\u22125</super>. The key parameters for "
        "the accounting are:", s["body"]))
    story.append(Paragraph(
        "\u2022 <b>Steps per round:</b> \u2308samples_per_client / batch_size\u2309 \u2248 \u230880 / 32\u2309 = 25 "
        "(with 3 local epochs: 75 steps per round)", s["bullet"]))
    story.append(Paragraph(
        "\u2022 <b>Total steps:</b> 10 rounds \u00d7 75 steps = 750 gradient steps", s["bullet"]))
    story.append(Paragraph(
        "\u2022 <b>Per-step RDP:</b> \u03b1 / (2\u03c3\u00b2) for Gaussian mechanism at order \u03b1", s["bullet"]))
    story.append(Paragraph(
        "\u2022 <b>Composition:</b> Total RDP = 750 \u00d7 per-step RDP (linear composition under RDP)", s["bullet"]))
    story.append(Paragraph(
        "\u2022 <b>Conversion:</b> \u03b5 = total_RDP + log(1/\u03b4) / (\u03b1 \u2212 1); minimized over all \u03b1", s["bullet"]))
    story.append(sp)

    # Table: DP configurations
    story.append(Paragraph("Table 5: Differential Privacy Configurations and Achieved Guarantees", s["caption"]))
    story.append(make_table(
        ["Target \u03b5", "\u03c3 (Noise Multiplier)", "Achieved \u03b5", "Privacy Level", "Gradient Clip Norm"],
        [
            ["\u221e", "0.00", "\u221e", "No Privacy (Baseline)", "N/A"],
            ["8", "11.03", "7.91", "Relaxed", "1.0"],
            ["4", "20.40", "4.02", "Moderate", "1.0"],
            ["2", "40.70", "1.94", "Strong", "1.0"],
            ["1", "75.06", "1.03", "Very Strong", "1.0"],
        ],
        [60, 100, 65, 110, 90],
        s,
    ))
    story.append(sp)

    # ── 4.6 Privacy Attack Setup ──────────────────────────────
    story.append(Paragraph("4.6 Privacy Attack Setup", s["h2"]))

    story.append(Paragraph("4.6.1 Membership Inference Attack Configuration", s["h3"]))
    story.append(Paragraph(
        "The membership inference attack (MIA) follows the shadow-model paradigm described in "
        "Section 3.7.1 of the Methodology. The attack is configured as follows:", s["body"]))
    story.append(Paragraph(
        "<b>Shadow Models:</b> Three shadow models are trained, each on a random subset of the "
        "training data containing up to min(|<i>D</i><sub>train</sub>| / 3, 5000) \u2248 2,666 "
        "samples. Each shadow model is trained for 5 epochs with the same optimizer configuration "
        "as the target model (SGD, lr = 0.01, weight decay = 10<super>\u22125</super>, batch size 32).", s["bullet"]))
    story.append(Paragraph(
        "<b>Feature Extraction:</b> For each sample presented to a shadow model, the following "
        "features are extracted: (1) the model\u2019s prediction value, (2) the absolute prediction "
        "error, (3) the L2 norm of the user embedding, (4) the L2 norm of the item embedding, "
        "(5) the dot product of the user and item embeddings, and (6) the full user and item "
        "embedding vectors (flattened). This yields a feature vector of dimension 5 + 2\u00d764 = 133.", s["bullet"]))
    story.append(Paragraph(
        "<b>Attack Classifier:</b> A Random Forest classifier with 50 estimators (scikit-learn "
        "defaults otherwise) is trained on the labeled feature vectors from all three shadow "
        "models. The classifier learns to discriminate between member (training) and non-member "
        "(test) samples.", s["bullet"]))
    story.append(Paragraph(
        "<b>Evaluation:</b> The trained classifier is evaluated on 100 member and 100 non-member "
        "samples drawn from the target model. Performance is measured by AUC (area under the "
        "ROC curve) and classification accuracy. An AUC of 0.5 corresponds to random guessing "
        "(no privacy leakage).", s["bullet"]))

    story.append(Paragraph("4.6.2 Model Inversion Attack Configuration", s["h3"]))
    story.append(Paragraph(
        "The model inversion attack attempts to reconstruct a user\u2019s top-<i>K</i> preferred "
        "items from the trained model. For each of 50 randomly sampled target users:", s["body"]))
    story.append(Paragraph(
        "\u2022 All 1,682 items are scored using the model\u2019s prediction function.", s["bullet"]))
    story.append(Paragraph(
        "\u2022 The top-10 items by predicted score are selected as the \u201creconstructed\u201d preferences.", s["bullet"]))
    story.append(Paragraph(
        "\u2022 These are compared against the ground-truth top-10 items (determined by actual "
        "training ratings).", s["bullet"]))
    story.append(Paragraph(
        "\u2022 A user is considered \u201csuccessfully attacked\u201d if at least 20% (i.e., 2 out of 10) "
        "of the reconstructed items overlap with the true top-10.", s["bullet"]))
    story.append(Paragraph(
        "The attack success rate is reported as the fraction of the 50 target users for whom "
        "the overlap threshold is met.", s["body"]))
    story.append(sp)

    # ── 4.7 Experiment Configurations ─────────────────────────
    story.append(Paragraph("4.7 Experiment Configurations", s["h2"]))
    story.append(Paragraph(
        "The experimental design consists of four experiment groups, totaling 30 individual "
        "experiment runs. Each federated learning configuration is repeated with three random "
        "seeds (42, 123, 456) to report mean \u00b1 standard deviation. The following subsections "
        "describe each group.", s["body"]))

    story.append(Paragraph("4.7.1 Experiment 1: Centralized Baseline", s["h3"]))
    story.append(Paragraph(
        "A centralized model is trained on the full 80,000-interaction training set for 50 epochs "
        "with batch size 64, learning rate 0.01, and no differential privacy. This configuration "
        "serves as the upper bound for recommendation accuracy and provides the reference point "
        "against which federated learning degradation is measured. The centralized model uses the "
        "same <i>MatrixFactorization</i> architecture with embedding dimension 64, totaling "
        "167,936 parameters.", s["body"]))

    story.append(Paragraph("4.7.2 Experiment 2: DP Budget Sweep (RQ1)", s["h3"]))
    story.append(Paragraph(
        "Federated learning is run with 100 clients, 10 communication rounds, and \u03b1 = 0.5 "
        "(moderately non-IID) for five privacy budgets: \u03b5 \u2208 {\u221e, 8, 4, 2, 1}. Each "
        "of the five configurations is repeated with three seeds, yielding 15 experiments. The "
        "\u03b5 = \u221e configuration disables DP-SGD entirely (no clipping, no noise). This "
        "experiment group isolates the effect of differential privacy on recommendation quality "
        "while holding the data distribution constant.", s["body"]))

    story.append(Paragraph("4.7.3 Experiment 3: Privacy Attack Evaluation (RQ2)", s["h3"]))
    story.append(Paragraph(
        "For each of the five DP budgets in Experiment 2 (using seed 42), the trained model is "
        "subjected to both the membership inference attack and the model inversion attack. This "
        "yields five attack evaluation configurations. The attacks are applied to the final global "
        "model after round 10. This experiment group assesses whether increasing the DP guarantee "
        "effectively reduces the success rate of practical privacy attacks.", s["body"]))

    story.append(Paragraph("4.7.4 Experiment 4: Heterogeneity Sweep (RQ3)", s["h3"]))
    story.append(Paragraph(
        "Federated learning is run with 100 clients, 10 rounds, no differential privacy "
        "(\u03b5 = \u221e), and three Dirichlet concentration parameters: \u03b1 \u2208 {0.1, 0.5, 1.0}. "
        "Each configuration is repeated with three seeds, yielding 9 experiments (of which 3 "
        "overlap with the DP sweep at \u03b1 = 0.5, \u03b5 = \u221e). This experiment group isolates the "
        "effect of data heterogeneity on federated learning performance by removing the confound "
        "of differential privacy.", s["body"]))
    story.append(sp)

    # Summary table of all experiments
    story.append(Paragraph("Table 6: Summary of All Experiment Configurations", s["caption"]))
    story.append(make_table(
        ["Experiment", "Clients", "Rounds", "\u03b5", "\u03b1", "Seeds", "Total Runs"],
        [
            ["Centralized Baseline", "N/A", "50 epochs", "N/A", "N/A", "1", "1"],
            ["DP Budget Sweep (RQ1)", "100", "10", "{\u221e, 8, 4, 2, 1}", "0.5", "{42, 123, 456}", "15"],
            ["Attack Evaluation (RQ2)", "100", "10", "{\u221e, 8, 4, 2, 1}", "0.5", "42", "5"],
            ["Heterogeneity Sweep (RQ3)", "100", "10", "\u221e", "{0.1, 0.5, 1.0}", "{42, 123, 456}", "9"],
            ["Total", "", "", "", "", "", "30"],
        ],
        [110, 42, 48, 80, 62, 72, 50],
        s,
    ))
    story.append(sp)

    # ── 4.8 Complete Hyperparameter Summary ───────────────────
    story.append(Paragraph("4.8 Complete Hyperparameter Summary", s["h2"]))
    story.append(Paragraph(
        "Table 7 consolidates all hyperparameters used across the experimental suite. Values "
        "were selected based on standard practices in the federated learning and recommendation "
        "systems literature and kept constant across all experiments unless explicitly noted as "
        "a swept variable.", s["body"]))

    story.append(Paragraph("Table 7: Complete Hyperparameter Configuration", s["caption"]))
    story.append(make_table(
        ["Category", "Parameter", "Value", "Notes"],
        [
            ["Model", "Embedding Dimension", "64", "User and item embeddings"],
            ["Model", "Total Parameters", "167,936", "(943 + 1,682) \u00d7 64"],
            ["Model", "Initialization", "\U0001d4a9(0, 0.1)", "Gaussian noise for embeddings"],
            ["Model", "Output Activation", "Sigmoid / None", "BCE variant / MSE variant"],
            ["", "", "", ""],
            ["FL Protocol", "Number of Clients (K)", "100", "Simulated in-memory"],
            ["FL Protocol", "Communication Rounds (T)", "10", "Global aggregation rounds"],
            ["FL Protocol", "Local Epochs (E)", "3", "Per-client per-round"],
            ["FL Protocol", "Aggregation", "FedAvg", "Sample-count weighted"],
            ["FL Protocol", "Client Participation", "100%", "All clients every round"],
            ["", "", "", ""],
            ["Optimizer", "Algorithm", "SGD", "No momentum"],
            ["Optimizer", "Learning Rate", "0.01", "Fixed, no scheduling"],
            ["Optimizer", "Local Batch Size", "32", "Federated experiments"],
            ["Optimizer", "Centralized Batch Size", "64", "Baseline only"],
            ["Optimizer", "Weight Decay (L2)", "10\u207b\u2075", "Regularization"],
            ["", "", "", ""],
            ["Differential Privacy", "Gradient Clip Norm (C)", "1.0", "Per-parameter L2 clipping"],
            ["Differential Privacy", "DP Delta (\u03b4)", "10\u207b\u2075", "Standard delta"],
            ["Differential Privacy", "Privacy Budgets (\u03b5)", "{\u221e, 8, 4, 2, 1}", "Swept variable (RQ1)"],
            ["Differential Privacy", "Noise Multipliers (\u03c3)", "{0, 11.03, 20.40, 40.70, 75.06}", "Calibrated via RDP"],
            ["", "", "", ""],
            ["Data", "Dataset", "MovieLens 100K", "943 users, 1,682 items"],
            ["Data", "Train / Test Split", "80% / 20%", "80K / 20K interactions"],
            ["Data", "Dirichlet \u03b1", "{0.1, 0.5, 1.0}", "Swept variable (RQ3)"],
            ["Data", "Relevance Threshold", "\u2265 4.0", "For ranking metrics"],
            ["", "", "", ""],
            ["Evaluation", "Top-K", "10", "NDCG@10, Hit@10, Prec@10, Rec@10"],
            ["Evaluation", "Test Users Sampled", "\u2264 100", "For recommendation metrics"],
            ["Evaluation", "Random Seeds", "{42, 123, 456}", "3 runs per configuration"],
            ["", "", "", ""],
            ["Attacks (MIA)", "Shadow Models", "3", "Trained on random subsets"],
            ["Attacks (MIA)", "Shadow Subset Size", "min(|D|/3, 5000)", "\u2248 2,666 samples each"],
            ["Attacks (MIA)", "Shadow Training Epochs", "5", "Same optimizer as target"],
            ["Attacks (MIA)", "Classifier", "Random Forest (50 trees)", "Scikit-learn defaults"],
            ["Attacks (MIA)", "Eval Samples", "100 member + 100 non-member", "Balanced evaluation set"],
            ["", "", "", ""],
            ["Attacks (Inversion)", "Target Users", "50", "Randomly sampled"],
            ["Attacks (Inversion)", "Reconstructed Top-K", "10", "Compared to ground truth"],
            ["Attacks (Inversion)", "Success Threshold", "\u2265 20% overlap", "2 of 10 items match"],
        ],
        [90, 130, 125, 130],
        s,
    ))
    story.append(sp)

    # ── 4.9 Evaluation Protocol ───────────────────────────────
    story.append(Paragraph("4.9 Evaluation Protocol", s["h2"]))

    story.append(Paragraph("4.9.1 Recommendation Metric Computation", s["h3"]))
    story.append(Paragraph(
        "Recommendation metrics are computed using the full item catalog scoring approach. For "
        "each sampled test user (up to 100 users), the model scores all 1,682 items by computing "
        "the dot product of the user\u2019s embedding with every item embedding. Items are ranked by "
        "predicted score in descending order, and the top-10 items are selected. The following "
        "metrics are then computed:", s["body"]))
    story.append(Paragraph(
        "<b>NDCG@10</b> uses the original 1\u20135 ratings as graded relevance scores. "
        "DCG@10 = \u03a3<sub>i=1</sub><super>10</super> rel<sub>i</sub> / log<sub>2</sub>(i + 1), "
        "normalized by the ideal DCG (IDCG) obtained from a perfect ranking of the user\u2019s "
        "items.", s["bullet"]))
    story.append(Paragraph(
        "<b>Hit@10</b> is a binary indicator: 1 if any item in the top-10 has a ground-truth "
        "rating \u2265 4.0, and 0 otherwise. The average across users gives the hit rate.", s["bullet"]))
    story.append(Paragraph(
        "<b>Precision@10</b> is the fraction of items in the top-10 with a ground-truth "
        "rating \u2265 4.0.", s["bullet"]))
    story.append(Paragraph(
        "<b>Recall@10</b> is the fraction of all items with a ground-truth rating \u2265 4.0 "
        "that appear in the top-10.", s["bullet"]))
    story.append(Paragraph(
        "Recommendation metrics are computed at key checkpoint rounds (1, 5, and 10) rather than "
        "every round, as scoring all items for all users is computationally more expensive than "
        "the regression metrics.", s["body"]))

    story.append(Paragraph("4.9.2 Regression Metric Computation", s["h3"]))
    story.append(Paragraph(
        "MSE and MAE are computed over the full 20,000-interaction test set every round. "
        "These metrics evaluate the model\u2019s ability to predict exact rating values rather than "
        "its ranking performance, providing a complementary view of model quality.", s["body"]))

    story.append(Paragraph("4.9.3 Privacy Metric Computation", s["h3"]))
    story.append(Paragraph(
        "Three privacy metrics are collected for each attack evaluation:", s["body"]))
    story.append(Paragraph(
        "<b>MIA AUC:</b> Area under the ROC curve for the membership inference classifier. "
        "Values near 0.5 indicate that the classifier performs no better than random, meaning "
        "the model does not leak membership information.", s["bullet"]))
    story.append(Paragraph(
        "<b>MIA Accuracy:</b> Classification accuracy of the attack classifier on the balanced "
        "evaluation set (100 members, 100 non-members). Baseline accuracy is 0.5.", s["bullet"]))
    story.append(Paragraph(
        "<b>Inversion Top-K Accuracy:</b> Fraction of target users whose top-10 preferences "
        "were successfully reconstructed with \u2265 20% overlap.", s["bullet"]))
    story.append(sp)

    # ── 4.10 Results Storage and Analysis Pipeline ────────────
    story.append(Paragraph("4.10 Results Storage and Analysis Pipeline", s["h2"]))

    story.append(Paragraph("4.10.1 Result Serialization Format", s["h3"]))
    story.append(Paragraph(
        "Each experiment produces two output files:", s["body"]))
    story.append(Paragraph(
        "<b>JSON File:</b> A comprehensive record containing the experiment identifier, "
        "timestamp, full configuration dictionary, per-round metrics (train loss, test MSE, MAE, "
        "and recommendation metrics at checkpoint rounds), aggregation statistics (number of "
        "participating clients, total samples), and final metrics. Files are named following the "
        "convention: <font face='Courier' size='9'>dp_{epsilon}_alpha_{alpha}_dim_64_clients_100_seed_{seed}.json</font>.", s["bullet"]))
    story.append(Paragraph(
        "<b>CSV Summary:</b> A tabular summary with one row per round, suitable for quick "
        "inspection and import into spreadsheet tools. Columns include round number, train loss, "
        "all six evaluation metrics, and a final summary row.", s["bullet"]))
    story.append(Paragraph(
        "Attack evaluation results are consolidated into a single JSON file "
        "(<font face='Courier' size='9'>attack_evaluation_summary.json</font>) containing MIA AUC, MIA accuracy, "
        "and inversion accuracy for each \u03b5 configuration.", s["body"]))

    story.append(Paragraph("4.10.2 Analysis and Visualization", s["h3"]))
    story.append(Paragraph(
        "A dedicated analysis script (<font face='Courier' size='9'>comprehensive_analysis.py</font>) reads all "
        "result JSON files and generates publication-quality figures. The script computes mean "
        "and standard deviation across the three seeds for each configuration and produces the "
        "following visualizations:", s["body"]))
    story.append(Paragraph(
        "\u2022 <b>Convergence plots:</b> Training loss versus communication round for all \u03b5 "
        "values, showing learning dynamics under different privacy constraints.", s["bullet"]))
    story.append(Paragraph(
        "\u2022 <b>Accuracy vs. \u03b5 plots:</b> NDCG@10 and Hit@10 as a function of the privacy "
        "budget, with error bars representing \u00b11 standard deviation.", s["bullet"]))
    story.append(Paragraph(
        "\u2022 <b>Accuracy loss plot:</b> Relative accuracy degradation (%) from the no-DP "
        "baseline as \u03b5 decreases.", s["bullet"]))
    story.append(Paragraph(
        "\u2022 <b>Heterogeneity plots:</b> NDCG@10 and Hit@10 as a function of \u03b1, isolating the "
        "effect of data distribution on FL performance.", s["bullet"]))
    story.append(Paragraph(
        "\u2022 <b>Attack effectiveness plots:</b> MIA AUC and accuracy versus \u03b5, demonstrating "
        "the effectiveness of DP in mitigating privacy attacks.", s["bullet"]))
    story.append(Paragraph(
        "All figures are rendered at 1200\u00d7800 pixel resolution using Seaborn\u2019s darkgrid style, "
        "with clear legends, axis labels, and error bars. Figures are saved as PNG files in the "
        "<font face='Courier' size='9'>figures/</font> directory.", s["body"]))
    story.append(sp)

    # ── 4.11 Mobile Client Integration ────────────────────────
    story.append(Paragraph("4.11 Mobile Client Integration", s["h2"]))

    story.append(Paragraph("4.11.1 Flutter Application Architecture", s["h3"]))
    story.append(Paragraph(
        "A companion mobile application built with Flutter (Dart) demonstrates the feasibility "
        "of on-device federated learning. The application targets Android (minimum API level 21) "
        "and includes the following components:", s["body"]))
    story.append(Paragraph(
        "<b>Matrix Factorization Model (Dart):</b> A pure-Dart implementation of the same "
        "matrix factorization architecture used in the Python experiments. The model performs "
        "forward passes, computes gradients via manual backpropagation, and applies SGD updates "
        "entirely on-device without any native ML framework dependency.", s["bullet"]))
    story.append(Paragraph(
        "<b>FL Client Service:</b> Manages the federated learning lifecycle: registration with "
        "the server, downloading global model parameters, local training, and uploading updated "
        "parameters. Communication uses HTTP with JSON payloads; model parameters are serialized "
        "as base64-encoded Float32 arrays for cross-platform compatibility.", s["bullet"]))
    story.append(Paragraph(
        "<b>Resource Monitor:</b> Tracks battery level, battery drain rate, memory usage, and "
        "device information during training. These metrics quantify the on-device computational "
        "cost of federated learning.", s["bullet"]))
    story.append(Paragraph(
        "<b>User Interface:</b> A single-screen interface displaying the server URL input, "
        "connection status, training logs (last 50 messages), per-round metrics, and resource "
        "consumption. Users can initiate training and export results.", s["bullet"]))

    story.append(Paragraph("4.11.2 Server\u2013Client Communication Protocol", s["h3"]))
    story.append(Paragraph(
        "The distributed deployment uses a FastAPI server that exposes the following endpoints:", s["body"]))
    story.append(Paragraph(
        "\u2022 <font face='Courier' size='9'>POST /register</font> \u2014 Client registration with a unique client ID.", s["bullet"]))
    story.append(Paragraph(
        "\u2022 <font face='Courier' size='9'>POST /init-model</font> \u2014 Server-side model initialization with "
        "specified dimensions (num_users, num_items, embedding_dim).", s["bullet"]))
    story.append(Paragraph(
        "\u2022 <font face='Courier' size='9'>POST /global-params-json</font> \u2014 Download current global model "
        "parameters as base64-encoded tensors.", s["bullet"]))
    story.append(Paragraph(
        "\u2022 <font face='Courier' size='9'>POST /upload-params-json</font> \u2014 Upload local model updates along "
        "with the client\u2019s sample count for weighted aggregation.", s["bullet"]))
    story.append(Paragraph(
        "Model parameters are transmitted as JSON objects containing the parameter name, tensor "
        "shape, data type, and base64-encoded Float32 byte arrays. For the 167,936-parameter "
        "model, a single parameter upload is approximately 650 KB.", s["body"]))
    story.append(sp)

    # ── 4.12 Reproducibility Measures ─────────────────────────
    story.append(Paragraph("4.12 Reproducibility Measures", s["h2"]))
    story.append(Paragraph(
        "Several measures ensure full reproducibility of all reported results:", s["body"]))
    story.append(Paragraph(
        "<b>Fixed Random Seeds:</b> All stochastic operations\u2014PyTorch weight initialization, "
        "NumPy Dirichlet sampling, data shuffling, and train/test splitting\u2014use fixed seeds. "
        "Each experiment configuration is run with seeds {42, 123, 456}, and results are reported "
        "as mean \u00b1 standard deviation.", s["bullet"]))
    story.append(Paragraph(
        "<b>Deterministic Data Pipeline:</b> The train\u2013test split uses a fixed permutation, "
        "and the Dirichlet partitioning is seeded, so identical client data partitions are "
        "produced across runs with the same seed.", s["bullet"]))
    story.append(Paragraph(
        "<b>Single-Script Execution:</b> The complete experiment pipeline\u2014data loading, "
        "partitioning, training, evaluation, and analysis\u2014is encapsulated in "
        "<font face='Courier' size='9'>run_complete_experiment.py</font>, which can be executed end-to-end "
        "without manual intervention.", s["bullet"]))
    story.append(Paragraph(
        "<b>Result Persistence:</b> Every experiment writes a self-contained JSON file with the "
        "full configuration and all per-round metrics, enabling independent verification and "
        "re-analysis.", s["bullet"]))
    story.append(Paragraph(
        "<b>Version Control:</b> All code, configuration, data processing scripts, and result "
        "files are maintained in a Git repository.", s["bullet"]))
    story.append(sp)

    # ── 4.13 Summary ──────────────────────────────────────────
    story.append(Paragraph("4.13 Summary", s["h2"]))
    story.append(Paragraph(
        "The experimental setup provides a controlled, reproducible, and comprehensive framework "
        "for investigating accuracy\u2013privacy trade-offs in federated learning for mobile "
        "recommendation. The design systematically varies the privacy budget \u03b5 (RQ1), evaluates "
        "privacy attacks across all DP configurations (RQ2), and examines data heterogeneity via "
        "the Dirichlet parameter \u03b1 (RQ3). A total of 30 experiment runs\u2014spanning 1 centralized "
        "baseline, 15 DP sweep configurations, 5 attack evaluations, and 9 heterogeneity sweep "
        "configurations\u2014are executed with triple-seed averaging to ensure statistical reliability. "
        "The in-memory simulation architecture enables rapid iteration while remaining functionally "
        "equivalent to a real distributed deployment, which is demonstrated by the companion "
        "Flutter mobile client.", s["body"]))

    return story


def main():
    out_path = "/Users/jonathanjohn/StudioProjects/master_thesis/Experimental_Setup.pdf"
    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        topMargin=0.9 * inch,
        bottomMargin=0.9 * inch,
        leftMargin=0.9 * inch,
        rightMargin=0.9 * inch,
        title="Experimental Setup",
        author="(anonymous)",
    )
    styles = build_styles()
    story = build_story(styles)
    doc.build(story)
    print(f"PDF written to {out_path}")


if __name__ == "__main__":
    main()
