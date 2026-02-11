"""Generate Methodology section PDF for the thesis document using reportlab."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib import colors

output_path = "Methodology_Section.pdf"
doc = SimpleDocTemplate(
    output_path,
    pagesize=A4,
    leftMargin=2.5*cm, rightMargin=2.5*cm,
    topMargin=2.5*cm, bottomMargin=2.5*cm
)

styles = getSampleStyleSheet()

# Custom styles
styles.add(ParagraphStyle(
    'ChapterTitle', parent=styles['Title'],
    fontName='Times-Bold', fontSize=18, spaceAfter=12, alignment=TA_CENTER
))
styles.add(ParagraphStyle(
    'SectionTitle', parent=styles['Heading2'],
    fontName='Times-Bold', fontSize=13, spaceBefore=16, spaceAfter=6
))
styles.add(ParagraphStyle(
    'SubsectionTitle', parent=styles['Heading3'],
    fontName='Times-Bold', fontSize=11.5, spaceBefore=12, spaceAfter=4
))
styles.add(ParagraphStyle(
    'BodyText2', parent=styles['BodyText'],
    fontName='Times-Roman', fontSize=11, leading=15,
    alignment=TA_JUSTIFY, spaceAfter=8
))
styles.add(ParagraphStyle(
    'IndentedText', parent=styles['BodyText'],
    fontName='Times-Roman', fontSize=11, leading=15,
    alignment=TA_JUSTIFY, leftIndent=20, spaceAfter=8
))
styles.add(ParagraphStyle(
    'EquationText', parent=styles['BodyText'],
    fontName='Times-Italic', fontSize=11, leading=15,
    alignment=TA_CENTER, spaceAfter=8, spaceBefore=4
))
styles.add(ParagraphStyle(
    'TableCaption', parent=styles['BodyText'],
    fontName='Times-Italic', fontSize=10, leading=13,
    alignment=TA_CENTER, spaceAfter=4, spaceBefore=6
))

story = []

# ============================================================
# Title
# ============================================================
story.append(Paragraph("Methodology", styles['ChapterTitle']))
story.append(Spacer(1, 8))

# ============================================================
# 3.1 Research Design
# ============================================================
story.append(Paragraph("3.1 Research Design", styles['SectionTitle']))
story.append(Paragraph(
    "This study employs an empirical, quantitative research design to investigate the accuracy-privacy "
    "trade-offs in federated learning for mobile movie recommendation systems. The research is structured "
    "around three research questions that examine (RQ1) the impact of differential privacy budgets on "
    "recommendation accuracy, (RQ2) the effectiveness of privacy attacks under varying DP configurations, "
    "and (RQ3) the influence of data heterogeneity on federated learning performance.",
    styles['BodyText2']
))
story.append(Paragraph(
    "The experimental framework follows a controlled variable approach: for RQ1, the privacy budget "
    "(\u03b5) is varied while holding data distribution constant; for RQ2, privacy attacks are evaluated "
    "across all DP configurations; and for RQ3, the Dirichlet concentration parameter (\u03b1) is varied "
    "while disabling differential privacy. Each configuration is repeated with three random seeds "
    "(42, 123, 456) to ensure statistical reliability and to report mean \u00b1 standard deviation of results.",
    styles['BodyText2']
))

# ============================================================
# 3.2 Dataset
# ============================================================
story.append(Paragraph("3.2 Dataset", styles['SectionTitle']))
story.append(Paragraph(
    "We use the MovieLens 100K dataset (Harper & Konstan, 2015), a widely adopted benchmark for "
    "recommendation system research. The dataset contains 100,000 ratings from 943 users across "
    "1,682 movies, with ratings on a 1\u20135 integer scale. The dataset exhibits 93.7% sparsity, which "
    "is representative of real-world recommendation scenarios. Ratings are used in their original "
    "continuous form (1\u20135 scale) rather than binarized, enabling regression-based evaluation that "
    "better captures the nuances of user preference prediction.",
    styles['BodyText2']
))
story.append(Paragraph(
    "The dataset is split into 80% training (80,000 interactions) and 20% test (20,000 interactions) "
    "sets using a random permutation with a fixed seed for reproducibility. For the federated learning "
    "experiments, the training data is further partitioned among 100 simulated clients using a "
    "Dirichlet distribution to create non-IID (non-independent and identically distributed) data splits, "
    "which models the natural heterogeneity of user preferences across mobile devices.",
    styles['BodyText2']
))

# ============================================================
# 3.3 Model Architecture
# ============================================================
story.append(Paragraph("3.3 Model Architecture", styles['SectionTitle']))
story.append(Paragraph(
    "The recommendation model is based on Matrix Factorization (MF), a proven approach for "
    "collaborative filtering that decomposes the user-item interaction matrix into low-dimensional "
    "latent factor representations. The model consists of two embedding layers:",
    styles['BodyText2']
))
story.append(Paragraph(
    "\u2022 <b>User Embedding</b>: Maps each of the 943 users to a 64-dimensional latent vector.<br/>"
    "\u2022 <b>Item Embedding</b>: Maps each of the 1,682 items to a 64-dimensional latent vector.",
    styles['IndentedText']
))
story.append(Paragraph(
    "The predicted rating for a user-item pair (u, i) is computed as the dot product of the corresponding "
    "user and item embedding vectors:",
    styles['BodyText2']
))
story.append(Paragraph(
    "\u0177(u, i) = e<sub>u</sub><sup>T</sup> \u00b7 e<sub>i</sub>",
    styles['EquationText']
))
story.append(Paragraph(
    "Embeddings are initialized with Gaussian noise (std = 0.1) to ensure adequate gradient flow during "
    "early training. The embedding dimension of 64 was selected to provide sufficient representational "
    "capacity while remaining deployable on mobile devices. The total model size is "
    "(943 + 1,682) \u00d7 64 = 167,936 parameters, which is suitable for on-device training on "
    "resource-constrained mobile platforms.",
    styles['BodyText2']
))

# ============================================================
# 3.4 Federated Learning Protocol
# ============================================================
story.append(Paragraph("3.4 Federated Learning Protocol", styles['SectionTitle']))
story.append(Paragraph(
    "The federated learning protocol follows the Federated Averaging (FedAvg) algorithm "
    "(McMahan et al., 2017). The protocol operates over T = 10 communication rounds between "
    "a central server and K = 100 simulated clients. Each round proceeds as follows:",
    styles['BodyText2']
))
story.append(Paragraph(
    "<b>Step 1 \u2013 Global Distribution:</b> The server broadcasts the current global model parameters "
    "to all participating clients.",
    styles['IndentedText']
))
story.append(Paragraph(
    "<b>Step 2 \u2013 Local Training:</b> Each client trains the received model on their local data for "
    "E = 3 local epochs using Stochastic Gradient Descent (SGD) with a learning rate of 0.01, "
    "batch size of 32, and L2 regularization (weight decay = 10<sup>\u20135</sup>). "
    "The loss function is Mean Squared Error (MSE) for regression-based rating prediction.",
    styles['IndentedText']
))
story.append(Paragraph(
    "<b>Step 3 \u2013 Parameter Upload:</b> Each client sends its updated model parameters back "
    "to the server.",
    styles['IndentedText']
))
story.append(Paragraph(
    "<b>Step 4 \u2013 Aggregation:</b> The server performs weighted averaging of client parameters, "
    "where weights are proportional to each client\u2019s local dataset size:",
    styles['IndentedText']
))
story.append(Paragraph(
    "w<sub>global</sub> = \u03a3<sub>k=1</sub><sup>K</sup> (n<sub>k</sub> / n<sub>total</sub>) \u00b7 w<sub>k</sub>",
    styles['EquationText']
))
story.append(Paragraph(
    "where n<sub>k</sub> is the number of training samples on client k and n<sub>total</sub> is the "
    "total number of samples across all clients.",
    styles['BodyText2']
))

# ============================================================
# 3.5 Non-IID Data Partitioning
# ============================================================
story.append(Paragraph("3.5 Non-IID Data Partitioning", styles['SectionTitle']))
story.append(Paragraph(
    "To simulate realistic mobile data distributions, we partition the training data among clients "
    "using a Dirichlet distribution with concentration parameter \u03b1. For each user in the dataset, "
    "a probability vector is sampled from Dir(\u03b1, \u2026, \u03b1) with K = 100 components, determining "
    "the proportion of that user\u2019s interactions assigned to each client. The parameter \u03b1 controls "
    "the degree of heterogeneity:",
    styles['BodyText2']
))
story.append(Paragraph(
    "\u2022 <b>\u03b1 = 0.1 (Highly Non-IID)</b>: Most of a user\u2019s data is concentrated on a single "
    "client, creating highly skewed distributions.<br/>"
    "\u2022 <b>\u03b1 = 0.5 (Moderately Non-IID)</b>: An intermediate distribution representing realistic "
    "mobile scenarios where users have some overlap but distinct preferences.<br/>"
    "\u2022 <b>\u03b1 = 1.0 (Mildly Non-IID)</b>: Data is more evenly distributed across clients, approaching "
    "but not reaching the IID case.",
    styles['IndentedText']
))
story.append(Paragraph(
    "This approach is standard in federated learning literature (Hsu et al., 2019) and captures "
    "the natural heterogeneity that arises when different mobile users have different movie-watching "
    "patterns and rating behaviors.",
    styles['BodyText2']
))

# ============================================================
# 3.6 Differential Privacy
# ============================================================
story.append(Paragraph("3.6 Differential Privacy Mechanism", styles['SectionTitle']))
story.append(Paragraph(
    "We implement Differentially Private Stochastic Gradient Descent (DP-SGD) (Abadi et al., 2016) "
    "to provide formal privacy guarantees during local training. The mechanism consists of two steps "
    "applied to each gradient computation during training:",
    styles['BodyText2']
))
story.append(Paragraph(
    "<b>Gradient Clipping:</b> Per-sample gradients are clipped to a maximum L2 norm of C = 1.0. "
    "This bounds the sensitivity of each individual training sample:",
    styles['IndentedText']
))
story.append(Paragraph(
    "g\u0302 = g \u00b7 min(1, C / \u2016g\u2016<sub>2</sub>)",
    styles['EquationText']
))
story.append(Paragraph(
    "<b>Gaussian Noise Addition:</b> After clipping, calibrated Gaussian noise is added to the gradients:",
    styles['IndentedText']
))
story.append(Paragraph(
    "g\u0303 = g\u0302 + \ud835\udca9(0, \u03c3\u00b2 \u00b7 C\u00b2 \u00b7 I)",
    styles['EquationText']
))
story.append(Paragraph(
    "where \u03c3 is the noise multiplier that determines the privacy-utility trade-off. "
    "The noise multiplier is calibrated using the R\u00e9nyi Differential Privacy (RDP) accountant "
    "(Mironov, 2017) to achieve a target (\u03b5, \u03b4)-DP guarantee with \u03b4 = 10<sup>\u20135</sup>. "
    "The RDP composition theorem tracks the cumulative privacy loss across multiple rounds of training. "
    "We evaluate five privacy budgets:",
    styles['BodyText2']
))

# DP Table
story.append(Paragraph("Table 1: DP Budget Configurations", styles['TableCaption']))
dp_data = [
    ['Target \u03b5', '\u03c3 (Noise Multiplier)', 'Achieved \u03b5', 'Privacy Level'],
    ['\u221e', '0.00', '\u221e', 'No Privacy'],
    ['8', '11.03', '7.91', 'Relaxed'],
    ['4', '20.40', '4.02', 'Moderate'],
    ['2', '40.70', '1.94', 'Strong'],
    ['1', '75.06', '1.03', 'Very Strong'],
]
dp_table = Table(dp_data, colWidths=[3*cm, 4*cm, 3*cm, 3.5*cm])
dp_table.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
    ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.9, 0.9, 0.9)),
    ('TOPPADDING', (0, 0), (-1, -1), 3),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
]))
story.append(dp_table)
story.append(Spacer(1, 12))

# ============================================================
# 3.7 Privacy Attack Evaluation
# ============================================================
story.append(Paragraph("3.7 Privacy Attack Evaluation", styles['SectionTitle']))

story.append(Paragraph("3.7.1 Membership Inference Attack (MIA)", styles['SubsectionTitle']))
story.append(Paragraph(
    "We implement a shadow-model based Membership Inference Attack (Shokri et al., 2017) to evaluate "
    "whether an adversary can determine if a specific data sample was used in the training set. "
    "The attack proceeds in three phases:",
    styles['BodyText2']
))
story.append(Paragraph(
    "<b>Phase 1 \u2013 Shadow Model Training:</b> Three shadow models are trained on random subsets of "
    "the training data (up to 5,000 samples each) for 5 epochs to approximate the target model\u2019s "
    "behavior.",
    styles['IndentedText']
))
story.append(Paragraph(
    "<b>Phase 2 \u2013 Attack Classifier Training:</b> For each shadow model, feature vectors are extracted "
    "for both member (training) and non-member (test) samples. Features include the model\u2019s prediction "
    "value, prediction error, embedding L2 norms, dot product of embeddings, and the raw embedding "
    "vectors (user and item). A Random Forest classifier with 50 estimators is trained on these features "
    "to distinguish members from non-members.",
    styles['IndentedText']
))
story.append(Paragraph(
    "<b>Phase 3 \u2013 Evaluation:</b> The trained attack classifier is applied to the target model using "
    "100 member and 100 non-member samples. We report the Area Under the ROC Curve (AUC) and accuracy. "
    "An AUC of 0.5 indicates random guessing (no privacy leakage), while an AUC approaching 1.0 "
    "indicates severe privacy leakage.",
    styles['IndentedText']
))

story.append(Paragraph("3.7.2 Model Inversion Attack", styles['SubsectionTitle']))
story.append(Paragraph(
    "We implement a model inversion attack that attempts to reconstruct a user\u2019s top-K preferred items "
    "from the trained model. For each target user, the attack scores all items in the catalog using the "
    "model\u2019s prediction function and selects the top-10 items with the highest predicted scores. "
    "These reconstructed preferences are compared against the ground truth top-10 items (determined "
    "by actual training ratings). Success is measured as the fraction of users for whom at least 20% "
    "of the reconstructed top-10 items overlap with the true top-10 items. The attack is evaluated on "
    "50 randomly sampled users per configuration.",
    styles['BodyText2']
))

# ============================================================
# 3.8 Evaluation Metrics
# ============================================================
story.append(Paragraph("3.8 Evaluation Metrics", styles['SectionTitle']))

story.append(Paragraph("3.8.1 Recommendation Quality Metrics", styles['SubsectionTitle']))
story.append(Paragraph(
    "We evaluate recommendation quality using four standard information retrieval metrics computed "
    "at rank K = 10, following established practice in recommendation system evaluation:",
    styles['BodyText2']
))
story.append(Paragraph(
    "<b>NDCG@10</b> (Normalized Discounted Cumulative Gain): Measures the quality of the ranking by "
    "assigning higher importance to relevant items appearing at higher positions. Relevance scores "
    "are the original 1\u20135 ratings. NDCG@10 ranges from 0 to 1, with 1 indicating a perfect ranking.",
    styles['IndentedText']
))
story.append(Paragraph(
    "DCG@K = \u03a3<sub>i=1</sub><sup>K</sup> rel<sub>i</sub> / log<sub>2</sub>(i + 1)&nbsp;&nbsp;&nbsp;&nbsp;"
    "NDCG@K = DCG@K / IDCG@K",
    styles['EquationText']
))
story.append(Paragraph(
    "<b>Hit@10</b> (Hit Rate): A binary indicator of whether any relevant item (rating \u2265 4.0) appears in "
    "the top-10 recommendations. Averaged across users, it represents the probability that at least "
    "one good recommendation is made.",
    styles['IndentedText']
))
story.append(Paragraph(
    "<b>Precision@10</b>: The fraction of items in the top-10 recommendations that are relevant "
    "(rating \u2265 4.0).",
    styles['IndentedText']
))
story.append(Paragraph(
    "<b>Recall@10</b>: The fraction of all relevant items for a user that appear in the top-10 "
    "recommendations.",
    styles['IndentedText']
))
story.append(Paragraph(
    "For efficiency, recommendation metrics are computed on a sample of up to 100 test users. "
    "For each sampled user, all 1,682 items are scored by the model, ranked by predicted score, "
    "and the top-10 items are selected for metric computation.",
    styles['BodyText2']
))

story.append(Paragraph("3.8.2 Regression Metrics", styles['SubsectionTitle']))
story.append(Paragraph(
    "<b>MSE</b> (Mean Squared Error): Average squared difference between predicted and actual ratings. "
    "<b>MAE</b> (Mean Absolute Error): Average absolute difference between predicted and actual ratings. "
    "These metrics are computed over the full test set (20,000 interactions) and provide a "
    "complementary view of prediction quality beyond ranking performance.",
    styles['BodyText2']
))

story.append(Paragraph("3.8.3 Privacy Metrics", styles['SubsectionTitle']))
story.append(Paragraph(
    "\u2022 <b>MIA AUC</b>: Area under the ROC curve for the membership inference attack classifier. "
    "Values near 0.5 indicate effective privacy protection; values approaching 1.0 indicate privacy "
    "leakage.<br/>"
    "\u2022 <b>MIA Accuracy</b>: Classification accuracy of the attack classifier in distinguishing training "
    "members from non-members.<br/>"
    "\u2022 <b>Inversion Top-K Accuracy</b>: Fraction of users whose top-10 preferences can be reconstructed "
    "with at least 20% overlap.",
    styles['IndentedText']
))

# ============================================================
# 3.9 Experimental Configurations
# ============================================================
story.append(Paragraph("3.9 Experimental Configurations", styles['SectionTitle']))
story.append(Paragraph(
    "The complete experimental design consists of the following configurations:",
    styles['BodyText2']
))

story.append(Paragraph("Experiment 1: Centralized Baseline", styles['SubsectionTitle']))
story.append(Paragraph(
    "A centralized model trained on the full training set for 50 epochs with batch size 64, "
    "learning rate 0.01, and no differential privacy. This serves as the upper bound for "
    "recommendation accuracy and the reference point for measuring federated learning degradation.",
    styles['BodyText2']
))

story.append(Paragraph("Experiment 2: DP Budget Sweep (RQ1)", styles['SubsectionTitle']))
story.append(Paragraph(
    "Federated learning with 100 clients, 10 rounds, \u03b1 = 0.5, and \u03b5 \u2208 {\u221e, 8, 4, 2, 1}. "
    "Each configuration is repeated with 3 seeds, yielding 15 experiments. This evaluates the "
    "accuracy-privacy trade-off by measuring how recommendation quality degrades as the DP guarantee "
    "is strengthened.",
    styles['BodyText2']
))

story.append(Paragraph("Experiment 3: Privacy Attack Evaluation (RQ2)", styles['SubsectionTitle']))
story.append(Paragraph(
    "Membership inference and model inversion attacks are evaluated on the trained models from each "
    "DP budget in Experiment 2 (using seed 42). This assesses whether DP effectively prevents "
    "practical privacy attacks against the recommendation model.",
    styles['BodyText2']
))

story.append(Paragraph("Experiment 4: Heterogeneity Sweep (RQ3)", styles['SubsectionTitle']))
story.append(Paragraph(
    "Federated learning with 100 clients, 10 rounds, no DP (\u03b5 = \u221e), and "
    "\u03b1 \u2208 {0.1, 0.5, 1.0}. Each configuration is repeated with 3 seeds, yielding 9 experiments "
    "(3 overlap with the DP sweep at \u03b1 = 0.5, \u03b5 = \u221e). This isolates the effect of data "
    "distribution on federated learning performance.",
    styles['BodyText2']
))

# ============================================================
# 3.10 Summary of Hyperparameters
# ============================================================
story.append(Paragraph("3.10 Summary of Hyperparameters", styles['SectionTitle']))
story.append(Paragraph("Table 2: Experiment Hyperparameters", styles['TableCaption']))

hp_data = [
    ['Parameter', 'Value'],
    ['Embedding Dimension', '64'],
    ['Number of Clients (K)', '100'],
    ['Communication Rounds (T)', '10'],
    ['Local Epochs (E)', '3'],
    ['Learning Rate', '0.01'],
    ['Batch Size (local)', '32'],
    ['Batch Size (centralized)', '64'],
    ['Weight Decay (L2)', '10\u207b\u2075'],
    ['Gradient Clip Norm (C)', '1.0'],
    ['DP Delta (\u03b4)', '10\u207b\u2075'],
    ['Train / Test Split', '80% / 20%'],
    ['Evaluation Top-K', '10'],
    ['Random Seeds', '{42, 123, 456}'],
    ['Total Experiments', '24'],
]
hp_table = Table(hp_data, colWidths=[6*cm, 5*cm])
hp_table.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
    ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
    ('ALIGN', (1, 0), (1, -1), 'CENTER'),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.9, 0.9, 0.9)),
    ('TOPPADDING', (0, 0), (-1, -1), 3),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
]))
story.append(hp_table)
story.append(Spacer(1, 12))

# ============================================================
# 3.11 Implementation Details
# ============================================================
story.append(Paragraph("3.11 Implementation Details", styles['SectionTitle']))
story.append(Paragraph(
    "All experiments are implemented in Python using PyTorch for model training and inference. "
    "The federated learning simulation is performed in-memory to avoid HTTP communication overhead, "
    "enabling the complete experiment suite (24 experiments) to run in approximately 60 minutes on a "
    "standard CPU. The RDP accountant implements the R\u00e9nyi Differential Privacy composition theorem "
    "for accurate privacy budget tracking. The recommendation metrics follow the standard evaluation "
    "protocol for top-K recommendation, where all items are scored for each user and ranked by "
    "predicted score.",
    styles['BodyText2']
))
story.append(Paragraph(
    "The in-memory simulation faithfully replicates the federated learning protocol: each round, "
    "every client receives a fresh copy of the global model, performs local training with optional "
    "DP-SGD, and returns the updated parameters for weighted FedAvg aggregation. The simulation "
    "is functionally equivalent to a distributed deployment but eliminates network latency and "
    "serialization overhead. A companion server-client implementation using FastAPI is also provided "
    "for real distributed deployment and mobile client integration.",
    styles['BodyText2']
))

# ============================================================
# 3.12 Reproducibility
# ============================================================
story.append(Paragraph("3.12 Reproducibility", styles['SectionTitle']))
story.append(Paragraph(
    "To ensure full reproducibility, all experiments use fixed random seeds for PyTorch and NumPy. "
    "The complete experiment pipeline, including data loading, partitioning, training, evaluation, "
    "and analysis, is encapsulated in a single script (<i>run_complete_experiment.py</i>) that can be "
    "executed end-to-end. Analysis and figure generation are handled by a separate script "
    "(<i>comprehensive_analysis.py</i>) that reads the saved JSON result files. All code, data, and results "
    "are version-controlled in a Git repository.",
    styles['BodyText2']
))

# Build
doc.build(story)
print(f"PDF saved to: {output_path}")
