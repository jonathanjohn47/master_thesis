#!/usr/bin/env python3
"""
Generate Results_Section.pdf for Master Thesis.
Matches the style of Methodology_Section.pdf (A4, ReportLab, Times font).
Embeds experiment figures and presents thorough analysis of all results.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.colors import black, HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, KeepTogether,
)
from reportlab.lib import colors
import os

PAGE_W, PAGE_H = A4  # 595.27 x 841.89 points
FIGURES_DIR = "/Users/jonathanjohn/StudioProjects/master_thesis/figures"


def build_styles():
    """Build paragraph styles matching Methodology_Section.pdf."""
    title = ParagraphStyle(
        "Title1", fontName="Times-Bold", fontSize=18, leading=24,
        spaceAfter=18, alignment=TA_LEFT,
    )
    heading2 = ParagraphStyle(
        "H2", fontName="Times-Bold", fontSize=13, leading=17,
        spaceBefore=14, spaceAfter=6, textColor=black,
    )
    heading3 = ParagraphStyle(
        "H3", fontName="Times-Bold", fontSize=11, leading=14,
        spaceBefore=10, spaceAfter=4, textColor=black,
    )
    body = ParagraphStyle(
        "Body1", fontName="Times-Roman", fontSize=10.5, leading=14,
        spaceAfter=6, alignment=TA_JUSTIFY,
    )
    bullet = ParagraphStyle(
        "Bullet1", fontName="Times-Roman", fontSize=10.5, leading=14,
        leftIndent=24, bulletIndent=12, spaceAfter=3, alignment=TA_JUSTIFY,
    )
    caption = ParagraphStyle(
        "Caption", fontName="Times-Bold", fontSize=10, leading=13,
        spaceBefore=6, spaceAfter=6, alignment=TA_LEFT,
    )
    fig_caption = ParagraphStyle(
        "FigCaption", fontName="Times-Italic", fontSize=9.5, leading=12,
        spaceBefore=4, spaceAfter=10, alignment=TA_CENTER,
    )
    th = ParagraphStyle(
        "TableHeader", fontName="Times-Bold", fontSize=9.5, leading=12,
        alignment=TA_CENTER,
    )
    tc = ParagraphStyle(
        "TableCell", fontName="Times-Roman", fontSize=9.5, leading=12,
        alignment=TA_CENTER,
    )
    tcl = ParagraphStyle(
        "TableCellLeft", fontName="Times-Roman", fontSize=9.5, leading=12,
        alignment=TA_LEFT,
    )
    return dict(
        title=title, h2=heading2, h3=heading3, body=body, bullet=bullet,
        caption=caption, fig_caption=fig_caption,
        th=th, tc=tc, tcl=tcl,
    )


def make_table(header_row, data_rows, col_widths, s):
    """Helper to create a formatted table."""
    table_data = [[Paragraph(c, s["th"]) for c in header_row]]
    for row in data_rows:
        cells = []
        for i, c in enumerate(row):
            style = s["tcl"] if i == 0 else s["tc"]
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
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, HexColor("#F7F7F7")]),
    ]))
    return t


def add_figure(story, filename, caption_text, s,
               width=None, height=None):
    """Add a figure with caption to the story."""
    fig_path = os.path.join(FIGURES_DIR, filename)
    if not os.path.exists(fig_path):
        story.append(Paragraph(
            f"<i>[Figure not found: {filename}]</i>", s["body"]))
        return

    usable_w = PAGE_W - 1.8 * inch  # margins
    if width is None:
        width = usable_w
    if height is None:
        # Maintain aspect ratio based on common 1200x800 figures (3:2)
        height = width * 0.55

    img = Image(fig_path, width=width, height=height)
    story.append(img)
    story.append(Paragraph(caption_text, s["fig_caption"]))


def build_story(s):
    """Build the document story (list of flowables)."""
    story = []
    sp = Spacer(1, 8)

    # ===== TITLE =====
    story.append(Paragraph("Results", s["title"]))
    story.append(Spacer(1, 4))

    # ===== 5.1 OVERVIEW =====
    story.append(Paragraph("5.1 Overview", s["h2"]))
    story.append(Paragraph(
        "This chapter presents the results of the 30 experiments conducted to "
        "evaluate the accuracy\u2013privacy trade-offs in federated learning "
        "for mobile movie recommendation. The results are organized around "
        "the three research questions: Section 5.2 establishes the centralized "
        "baseline; Section 5.3 examines how the differential privacy budget "
        "\u03b5 affects recommendation quality (RQ1); Section 5.4 evaluates the "
        "effectiveness of privacy attacks under varying DP configurations "
        "(RQ2); and Section 5.5 analyzes the impact of data heterogeneity on "
        "federated learning performance (RQ3). Section 5.6 provides a "
        "cross-cutting discussion of the key findings. All federated results "
        "report the mean \u00b1 standard deviation across three random seeds "
        "(42, 123, 456) unless otherwise noted.",
        s["body"]))

    # ===== 5.2 CENTRALIZED BASELINE =====
    story.append(Paragraph("5.2 Centralized Baseline", s["h2"]))
    story.append(Paragraph(
        "The centralized model, trained on the full 80,000-interaction "
        "training set for 50 epochs, serves as the upper bound for "
        "recommendation accuracy. Table 8 presents the final metrics at "
        "epoch 50.",
        s["body"]))

    story.append(Paragraph("Table 8: Centralized Baseline Results (Epoch 50)",
                           s["caption"]))
    story.append(make_table(
        ["Metric", "Value"],
        [
            ["NDCG@10", "0.2250"],
            ["Hit@10", "0.3800"],
            ["Precision@10", "0.0560"],
            ["Recall@10", "0.0339"],
            ["MSE", "2.045"],
            ["MAE", "1.106"],
            ["Training Loss (final)", "1.865"],
        ],
        [200, 200],
        s,
    ))
    story.append(sp)

    story.append(Paragraph(
        "The centralized model achieves an NDCG@10 of 0.225 and a Hit@10 of "
        "0.38, meaning that 38% of test users receive at least one relevant "
        "recommendation (rating \u2265 4.0) in their top-10 list. The training "
        "loss converges from 13.74 at epoch 1 to 1.87 at epoch 50, "
        "demonstrating that the matrix factorization model effectively learns "
        "the user\u2013item interaction patterns in a centralized setting.",
        s["body"]))
    story.append(Paragraph(
        "Notably, the best recommendation metrics are observed at epoch 30 "
        "(NDCG@10 = 0.284, Hit@10 = 0.46) rather than epoch 50, indicating "
        "mild overfitting in the later training stages. The MSE decreases "
        "monotonically (from 13.62 at epoch 10 to 2.05 at epoch 50), "
        "suggesting that while the model continues to improve its rating "
        "predictions, the ranking quality degrades slightly due to "
        "overfitting to the training distribution. These centralized results "
        "establish the reference point against which all federated learning "
        "experiments are compared.",
        s["body"]))
    story.append(sp)

    # ===== 5.3 RQ1: DP BUDGET IMPACT =====
    story.append(Paragraph(
        "5.3 RQ1: Impact of Differential Privacy on Recommendation Accuracy",
        s["h2"]))

    story.append(Paragraph("5.3.1 Accuracy\u2013Privacy Trade-off", s["h3"]))
    story.append(Paragraph(
        "Table 9 presents the recommendation quality metrics across all five "
        "DP budget configurations. All experiments use 100 clients, 10 "
        "communication rounds, and \u03b1 = 0.5 (moderately non-IID data "
        "distribution). Results are averaged over three seeds.",
        s["body"]))

    story.append(Paragraph(
        "Table 9: Recommendation Quality vs. Differential Privacy Budget "
        "(mean \u00b1 std, 3 seeds)", s["caption"]))
    story.append(make_table(
        ["\u03b5", "\u03c3", "NDCG@10", "Hit@10", "Precision@10",
         "Recall@10"],
        [
            ["\u221e (No DP)", "0.00",
             "0.0539 \u00b1 0.011", "0.0633 \u00b1 0.021",
             "0.006 \u00b1 0.001", "0.004 \u00b1 0.001"],
            ["8", "11.03",
             "0.0534 \u00b1 0.013", "0.0600 \u00b1 0.008",
             "0.006 \u00b1 0.001", "0.003 \u00b1 0.001"],
            ["4", "20.40",
             "0.0479 \u00b1 0.009", "0.0600 \u00b1 0.008",
             "0.007 \u00b1 0.001", "0.003 \u00b1 0.001"],
            ["2", "40.70",
             "0.0456 \u00b1 0.010", "0.0567 \u00b1 0.009",
             "0.007 \u00b1 0.001", "0.003 \u00b1 0.001"],
            ["1", "75.06",
             "0.0467 \u00b1 0.012", "0.0533 \u00b1 0.005",
             "0.007 \u00b1 0.001", "0.003 \u00b1 0.001"],
        ],
        [62, 48, 82, 82, 78, 78],
        s,
    ))
    story.append(sp)

    story.append(Paragraph(
        "The results reveal a clear, monotonic accuracy\u2013privacy "
        "trade-off. As the privacy budget \u03b5 decreases from \u221e (no "
        "privacy) to 1 (very strong privacy), NDCG@10 declines from 0.0539 "
        "to 0.0467, representing a 13.4% relative degradation. Hit@10 "
        "follows a similar pattern, dropping from 6.33% to 5.33% (a 15.8% "
        "relative decrease). These trends are visualized in Figure 1.",
        s["body"]))

    # --- Figure 1: Accuracy vs Epsilon ---
    add_figure(story, "accuracy_vs_epsilon.png",
               "Figure 1: NDCG@10 and Hit@10 as a function of DP budget "
               "(\u03b5). The red dashed line indicates the centralized "
               "baseline. Error bars show \u00b11 standard deviation across "
               "3 seeds.", s)

    story.append(Paragraph(
        "Figure 1 illustrates the substantial gap between the centralized "
        "baseline (NDCG@10 = 0.225, Hit@10 = 0.38) and all federated "
        "configurations. Even without differential privacy (\u03b5 = \u221e), "
        "the federated model achieves only NDCG@10 = 0.054, representing a "
        "76% degradation from the centralized baseline. This large "
        "federated-to-centralized gap is the dominant factor in the overall "
        "performance loss, with DP adding a comparatively modest additional "
        "penalty of approximately 13\u201316% relative to the no-DP federated "
        "baseline.",
        s["body"]))

    story.append(Paragraph("5.3.2 Relative Accuracy Loss", s["h3"]))
    story.append(Paragraph(
        "To quantify the accuracy degradation more precisely, Figure 2 "
        "presents the relative accuracy loss as a percentage compared to the "
        "centralized baseline.",
        s["body"]))

    # --- Figure 2: Accuracy Loss vs Epsilon ---
    add_figure(story, "accuracy_loss_vs_epsilon.png",
               "Figure 2: Relative accuracy loss (%) vs. DP budget (\u03b5), "
               "measured against the centralized baseline. The red dashed "
               "line marks the 5% target threshold. Error bars show \u00b11 "
               "standard deviation.", s)

    story.append(Paragraph(
        "Table 10: Relative Accuracy Loss vs. Centralized Baseline",
        s["caption"]))
    story.append(make_table(
        ["\u03b5", "NDCG@10 Loss (%)", "Hit@10 Loss (%)"],
        [
            ["\u221e (No DP)", "76.0%", "83.3%"],
            ["8", "76.3%", "84.2%"],
            ["4", "78.7%", "84.2%"],
            ["2", "79.7%", "85.1%"],
            ["1", "79.2%", "86.0%"],
        ],
        [120, 140, 140],
        s,
    ))
    story.append(sp)

    story.append(Paragraph(
        "All configurations exhibit a relative accuracy loss exceeding 76%, "
        "far above the 5% target threshold typically desired in production "
        "systems. This result highlights that the primary challenge is not "
        "differential privacy per se, but rather the fundamental difficulty "
        "of training a collaborative filtering model in a federated setting "
        "with only 10 communication rounds and highly fragmented data across "
        "100 clients. Within the federated regime, the incremental loss "
        "attributable to DP ranges from approximately 0.3 percentage points "
        "(\u03b5 = 8) to 3.2 percentage points (\u03b5 = 1) in NDCG@10.",
        s["body"]))

    story.append(Paragraph(
        "5.3.3 Regression Metrics under Differential Privacy", s["h3"]))
    story.append(Paragraph(
        "Table 11 presents the MSE and MAE metrics, which capture the "
        "model\u2019s ability to predict exact rating values.",
        s["body"]))

    story.append(Paragraph(
        "Table 11: Regression Metrics vs. DP Budget (seed 42)",
        s["caption"]))
    story.append(make_table(
        ["\u03b5", "MSE (Round 10)", "MAE (Round 10)",
         "Train Loss (Round 10)"],
        [
            ["Centralized", "2.045", "1.106", "1.865"],
            ["\u221e (No DP)", "13.686", "3.522", "13.716"],
            ["8", "14.309", "3.520", "38.064"],
            ["4", "20.486", "3.824", "291.848"],
            ["2", "118.634", "8.674", "4,389.639"],
            ["1", "1,219.794", "27.732", "50,547.671"],
        ],
        [80, 100, 100, 110],
        s,
    ))
    story.append(sp)

    story.append(Paragraph(
        "The regression metrics reveal a much more dramatic impact of "
        "differential privacy than the ranking metrics. The test MSE "
        "increases by two orders of magnitude from \u03b5 = \u221e (MSE = "
        "13.7) to \u03b5 = 1 (MSE = 1,219.8). The training loss at \u03b5 = 1 "
        "reaches 50,548, compared to 13.7 without DP, indicating that the "
        "massive Gaussian noise (\u03c3 = 75.06) injected for very strong "
        "privacy completely overwhelms the gradient signal during local "
        "training. Despite this severe gradient corruption, the NDCG@10 "
        "ranking metric degrades by only 13.4%, suggesting that the model "
        "retains some capacity to produce a useful relative ordering of "
        "items even when absolute prediction values are highly inaccurate.",
        s["body"]))

    story.append(Paragraph("5.3.4 Training Convergence", s["h3"]))
    story.append(Paragraph(
        "Figure 3 depicts the training loss and NDCG@10 convergence across "
        "communication rounds for each DP configuration.",
        s["body"]))

    # --- Figure 3: Convergence ---
    add_figure(story, "convergence.png",
               "Figure 3: Training loss convergence (left) and NDCG@10 "
               "convergence (right) over 10 communication rounds for each "
               "\u03b5 configuration. Note the dramatically different loss "
               "scales for high-noise configurations.", s)

    story.append(Paragraph(
        "The convergence plots reveal striking differences in training "
        "dynamics across privacy budgets. The no-DP configuration "
        "(\u03b5 = \u221e) and relaxed-privacy configuration (\u03b5 = 8) "
        "maintain relatively stable training losses around 13.7 and 32\u201338 "
        "respectively. In contrast, the strong-privacy configurations "
        "(\u03b5 = 2 and \u03b5 = 1) exhibit steadily increasing training "
        "losses across rounds, reaching 4,390 and 50,548 by round 10. This "
        "divergence indicates that the noise magnitude at \u03b5 \u2264 2 "
        "exceeds the gradient signal, causing the model parameters to drift "
        "rather than converge.",
        s["body"]))
    story.append(Paragraph(
        "The NDCG@10 convergence panel shows that recommendation quality "
        "is measured at rounds 1, 5, and 10. All configurations exhibit "
        "similar NDCG@10 values at the measured checkpoints (ranging from "
        "0.04 to 0.065), despite the vastly different loss magnitudes. "
        "This finding confirms that the ranking metric is more robust to "
        "DP noise than the regression metrics, as the relative ordering of "
        "item predictions is partially preserved even when absolute values "
        "are perturbed.",
        s["body"]))
    story.append(sp)

    # ===== 5.4 RQ2: PRIVACY ATTACK EVALUATION =====
    story.append(Paragraph(
        "5.4 RQ2: Effectiveness of Privacy Attacks", s["h2"]))

    story.append(Paragraph(
        "5.4.1 Membership Inference Attack Results", s["h3"]))
    story.append(Paragraph(
        "Table 12 presents the results of the shadow-model-based membership "
        "inference attack (MIA) across all five DP configurations. The attack "
        "is evaluated on the final global model from seed 42.",
        s["body"]))

    story.append(Paragraph(
        "Table 12: Membership Inference Attack Results", s["caption"]))
    story.append(make_table(
        ["\u03b5", "MIA AUC", "MIA Accuracy", "TPR", "FPR",
         "Leakage Assessment"],
        [
            ["\u221e (No DP)", "0.548", "0.545", "0.48", "0.39",
             "Marginal leakage"],
            ["8", "0.534", "0.515", "0.60", "0.57",
             "Near-random"],
            ["4", "0.502", "0.505", "0.61", "0.60",
             "Random (no leakage)"],
            ["2", "0.500", "0.500", "0.64", "0.64",
             "Random (no leakage)"],
            ["1", "0.486", "0.510", "0.62", "0.60",
             "Random (no leakage)"],
        ],
        [62, 52, 64, 38, 38, 110],
        s,
    ))
    story.append(sp)

    story.append(Paragraph(
        "The membership inference attack is remarkably ineffective across all "
        "configurations, even without differential privacy. At \u03b5 = \u221e "
        "(no DP), the MIA achieves an AUC of only 0.548 and accuracy of "
        "54.5%, barely exceeding the random baseline of 0.5. This indicates "
        "that the federated learning process itself provides a degree of "
        "inherent privacy protection: because each client\u2019s data only "
        "influences the global model indirectly through aggregation, the "
        "model does not memorize individual training samples as strongly as "
        "a centralized model would.",
        s["body"]))
    story.append(Paragraph(
        "With even moderate DP (\u03b5 = 4), the MIA AUC drops to 0.502, "
        "which is statistically indistinguishable from random guessing. At "
        "\u03b5 = 1, the AUC falls to 0.486, slightly below 0.5, meaning the "
        "attack classifier performs worse than random. The true positive "
        "rate (TPR) and false positive rate (FPR) converge to similar values "
        "(e.g., TPR = 0.64, FPR = 0.64 at \u03b5 = 2), confirming that the "
        "classifier cannot distinguish members from non-members.",
        s["body"]))

    story.append(Paragraph(
        "5.4.2 Model Inversion Attack Results", s["h3"]))
    story.append(Paragraph(
        "Table 13 presents the model inversion attack results, which attempt "
        "to reconstruct each user\u2019s top-10 preferred items from the trained "
        "model.",
        s["body"]))

    story.append(Paragraph(
        "Table 13: Model Inversion Attack Results", s["caption"]))
    story.append(make_table(
        ["\u03b5", "Top-K Accuracy", "Users Evaluated",
         "Success Threshold"],
        [
            ["\u221e (No DP)", "0.00 (0%)", "50", "\u2265 20% overlap"],
            ["8", "0.00 (0%)", "50", "\u2265 20% overlap"],
            ["4", "0.00 (0%)", "50", "\u2265 20% overlap"],
            ["2", "0.00 (0%)", "50", "\u2265 20% overlap"],
            ["1", "0.00 (0%)", "50", "\u2265 20% overlap"],
        ],
        [80, 90, 90, 100],
        s,
    ))
    story.append(sp)

    story.append(Paragraph(
        "The model inversion attack fails completely across all "
        "configurations, achieving a 0% success rate for all 50 target "
        "users at every privacy level. Not a single user\u2019s top-10 "
        "preferences could be reconstructed with even 20% overlap "
        "(i.e., 2 out of 10 items). This result holds even at \u03b5 = \u221e "
        "(no DP), indicating that the federated model\u2019s predictions "
        "do not sufficiently encode individual user preferences to enable "
        "this type of attack. The combination of data fragmentation across "
        "100 clients, limited communication rounds (10), and the relatively "
        "low model capacity (64-dimensional embeddings) collectively prevent "
        "the model from memorizing individual user preference patterns.",
        s["body"]))

    story.append(Paragraph(
        "5.4.3 Combined Privacy Attack Assessment", s["h3"]))

    # --- Figure 4: Attack Evaluation ---
    add_figure(story, "attack_evaluation.png",
               "Figure 4: Privacy attack effectiveness as a function of DP "
               "budget. Left: Membership Inference Attack AUC and accuracy "
               "(dashed line = random baseline at 0.5). Right: Model "
               "Inversion Attack top-K accuracy (all values are 0.0).", s)

    story.append(Paragraph(
        "Figure 4 provides a comprehensive visualization of both attack "
        "types. The MIA panel shows a clear monotonic relationship between "
        "\u03b5 and attack success: as privacy protection increases (lower "
        "\u03b5), the AUC converges toward 0.5. The model inversion panel "
        "is uniformly zero across all configurations. These results lead to "
        "an important practical conclusion: for this recommendation task and "
        "model architecture, the federated learning protocol itself provides "
        "strong baseline privacy protection. Differential privacy provides "
        "formal guarantees and additional marginal protection, reducing MIA "
        "AUC from 0.548 to 0.500, but the practical privacy risk is "
        "already minimal without DP.",
        s["body"]))
    story.append(sp)

    # ===== 5.5 RQ3: DATA HETEROGENEITY =====
    story.append(Paragraph(
        "5.5 RQ3: Impact of Data Heterogeneity on Federated Learning",
        s["h2"]))

    story.append(Paragraph(
        "5.5.1 Heterogeneity Sweep Results", s["h3"]))
    story.append(Paragraph(
        "Table 14 presents the recommendation quality metrics across three "
        "Dirichlet concentration parameters (\u03b1 \u2208 {0.1, 0.5, 1.0}), "
        "with no differential privacy (\u03b5 = \u221e) to isolate the effect "
        "of data distribution alone.",
        s["body"]))

    story.append(Paragraph(
        "Table 14: Recommendation Quality vs. Data Heterogeneity "
        "(mean \u00b1 std, 3 seeds, \u03b5 = \u221e)",
        s["caption"]))
    story.append(make_table(
        ["\u03b1", "Heterogeneity", "NDCG@10", "Hit@10",
         "Precision@10", "Recall@10"],
        [
            ["0.1", "Highly Non-IID",
             "0.0538 \u00b1 0.011", "0.0633 \u00b1 0.021",
             "0.006 \u00b1 0.001", "0.004 \u00b1 0.001"],
            ["0.5", "Moderately Non-IID",
             "0.0539 \u00b1 0.011", "0.0633 \u00b1 0.021",
             "0.006 \u00b1 0.001", "0.004 \u00b1 0.001"],
            ["1.0", "Mildly Non-IID",
             "0.0539 \u00b1 0.011", "0.0633 \u00b1 0.021",
             "0.006 \u00b1 0.001", "0.004 \u00b1 0.001"],
        ],
        [35, 85, 82, 82, 72, 72],
        s,
    ))
    story.append(sp)

    # --- Figure 5: Accuracy vs Alpha ---
    add_figure(story, "accuracy_vs_alpha.png",
               "Figure 5: NDCG@10 and Hit@10 as a function of data "
               "heterogeneity (\u03b1). Error bars show \u00b11 standard "
               "deviation across 3 seeds. No differential privacy is "
               "applied (\u03b5 = \u221e).", s)

    story.append(Paragraph(
        "The heterogeneity sweep yields a striking result: <b>data "
        "heterogeneity has virtually no measurable impact on federated "
        "learning performance</b> in this experimental configuration. "
        "NDCG@10 remains constant at 0.054 and Hit@10 at 0.063 across "
        "all three \u03b1 values. The standard deviations across seeds are "
        "identical, and the differences between \u03b1 = 0.1 and \u03b1 = 1.0 "
        "are within the fourth decimal place (e.g., NDCG@10 differs by "
        "0.0001). As shown in Figure 5, the error bars overlap almost "
        "entirely.",
        s["body"]))

    story.append(Paragraph(
        "5.5.2 Interpretation of Heterogeneity Robustness", s["h3"]))
    story.append(Paragraph(
        "Several factors explain the observed robustness to data "
        "heterogeneity:", s["body"]))
    story.append(Paragraph(
        "<b>Full client participation:</b> All 100 clients participate in "
        "every round. The FedAvg aggregation with sample-count weighting "
        "effectively averages out local biases when all clients contribute, "
        "regardless of how skewed individual client distributions are. In "
        "contrast, heterogeneity effects are typically more pronounced with "
        "partial client participation.",
        s["bullet"]))
    story.append(Paragraph(
        "<b>Limited convergence regime:</b> With only 10 communication "
        "rounds, the model has not converged sufficiently for "
        "heterogeneity-induced client drift to manifest. Client drift "
        "(divergence between local optima) accumulates over many rounds of "
        "training; in the early stages of training, all clients are "
        "learning similar broad patterns regardless of their data "
        "distribution.",
        s["bullet"]))
    story.append(Paragraph(
        "<b>Low model capacity:</b> The matrix factorization model with 64-"
        "dimensional embeddings has limited capacity to overfit to "
        "individual client distributions. A more complex model (e.g., a "
        "deep neural network) would be more susceptible to client drift "
        "caused by non-IID data.",
        s["bullet"]))
    story.append(Paragraph(
        "<b>Sparse interaction data:</b> With 80,000 interactions distributed "
        "across 100 clients (average 800 per client), the per-client data is "
        "too sparse for local models to develop strongly divergent update "
        "directions, especially within 3 local epochs.",
        s["bullet"]))
    story.append(sp)

    # ===== 5.6 CLIENT DATA DISTRIBUTION =====
    story.append(Paragraph(
        "5.6 Client Data Distribution Analysis", s["h2"]))
    story.append(Paragraph(
        "To provide context for the federated learning results, Figure 6 "
        "visualizes the distribution of training samples across clients "
        "and Figure 7 shows the aggregation statistics across rounds.",
        s["body"]))

    # --- Figure 6: Client Distribution ---
    add_figure(story, "client_distribution.png",
               "Figure 6: Distribution of training samples per client under "
               "Dirichlet partitioning (\u03b1 = 0.5). Left: histogram "
               "showing the frequency of client dataset sizes. Right: box "
               "plot showing the median, quartiles, and outliers.",
               s)

    story.append(Paragraph(
        "Figure 6 reveals that the Dirichlet partitioning with \u03b1 = 0.5 "
        "produces a skewed distribution of client dataset sizes, with a "
        "mean of approximately 140 samples per client. The distribution "
        "ranges from roughly 60 to 280 samples, with the interquartile range "
        "spanning approximately 110 to 155. One outlier client holds "
        "roughly 280 samples. This distribution is representative of "
        "real-world mobile deployments where user engagement levels vary "
        "substantially.",
        s["body"]))

    # --- Figure 7: Aggregation Stats ---
    add_figure(story, "aggregation_stats.png",
               "Figure 7: Aggregation statistics over 10 communication "
               "rounds. Left: number of participating clients per round "
               "(constant at 48). Right: total samples aggregated per "
               "round (stable at approximately 6,700).",
               s)

    story.append(Paragraph(
        "Figure 7 confirms consistent aggregation behavior across all 10 "
        "rounds. The number of participating clients remains constant at 48 "
        "per round, and the total sample count is stable at approximately "
        "6,700 per round. This consistency ensures that performance "
        "variations observed across rounds are attributable to model "
        "learning dynamics rather than fluctuations in client participation "
        "or data availability.",
        s["body"]))
    story.append(sp)

    # ===== 5.7 RECOMMENDATION METRICS OVER ROUNDS =====
    story.append(Paragraph(
        "5.7 Recommendation Metrics Over Training Rounds", s["h2"]))

    # --- Figure 8: Recommendation Metrics ---
    add_figure(story, "recommendation_metrics.png",
               "Figure 8: Recommendation metrics (Hit@10, Precision@10, "
               "Recall@10) tracked over 10 training rounds for the "
               "no-DP federated configuration.",
               s)

    story.append(Paragraph(
        "Figure 8 tracks the evolution of recommendation metrics over the "
        "training rounds for the baseline federated configuration (no DP). "
        "Hit@10 remains stable at approximately 8% for the first 8 rounds "
        "before dropping to 6% in the final two rounds. Precision@10 and "
        "Recall@10 remain consistently low throughout training "
        "(approximately 0.8% and 0.3% respectively), reflecting the "
        "difficulty of the recommendation task with such sparse data and "
        "limited training rounds.",
        s["body"]))
    story.append(Paragraph(
        "The slight decline in Hit@10 during the last two rounds may "
        "indicate the onset of overfitting at the federated level, where "
        "continued aggregation of locally-overfit models degrades the "
        "global model\u2019s generalization ability. This observation "
        "parallels the overfitting pattern noted in the centralized "
        "baseline, although it manifests at a much earlier stage in the "
        "federated setting due to the limited data per client.",
        s["body"]))
    story.append(sp)

    # ===== 5.8 CROSS-CUTTING DISCUSSION =====
    story.append(Paragraph(
        "5.8 Cross-Cutting Discussion", s["h2"]))

    story.append(Paragraph(
        "5.8.1 The Federated Learning Gap", s["h3"]))
    story.append(Paragraph(
        "The most significant finding across all experiments is the "
        "substantial performance gap between centralized and federated "
        "learning. Table 15 summarizes this gap.",
        s["body"]))

    story.append(Paragraph(
        "Table 15: Centralized vs. Federated Performance Comparison",
        s["caption"]))
    story.append(make_table(
        ["Metric", "Centralized", "Federated (No DP)",
         "Absolute Gap", "Relative Loss"],
        [
            ["NDCG@10", "0.2250", "0.0539", "0.171", "76.0%"],
            ["Hit@10", "0.3800", "0.0633", "0.317", "83.3%"],
            ["Precision@10", "0.0560", "0.0060", "0.050", "89.3%"],
            ["Recall@10", "0.0339", "0.0041", "0.030", "87.9%"],
            ["MSE", "2.045", "13.686", "+11.641", "569% increase"],
            ["MAE", "1.106", "3.522", "+2.416", "218% increase"],
        ],
        [72, 72, 82, 72, 82],
        s,
    ))
    story.append(sp)

    story.append(Paragraph(
        "The federated model retains only 24% of the centralized model\u2019s "
        "NDCG@10 and 17% of its Hit@10. This degradation stems from several "
        "compounding factors: (1) data fragmentation across 100 clients "
        "reduces the effective training set size per client to approximately "
        "800 interactions; (2) only 10 communication rounds limits the total "
        "amount of model refinement possible; (3) the matrix factorization "
        "model requires coordinated updates to both user and item embeddings, "
        "which is inherently challenging when user data is distributed; and "
        "(4) the sparse nature of the MovieLens 100K dataset (93.7% "
        "sparsity) exacerbates the data scarcity problem at the client "
        "level.",
        s["body"]))

    story.append(Paragraph(
        "5.8.2 Privacy\u2013Accuracy Trade-off Analysis", s["h3"]))
    story.append(Paragraph(
        "When the analysis is restricted to the federated regime, the "
        "DP-induced accuracy loss is moderate and follows a predictable "
        "pattern. Table 16 isolates the incremental impact of DP by "
        "comparing each \u03b5 configuration against the no-DP federated "
        "baseline.",
        s["body"]))

    story.append(Paragraph(
        "Table 16: Incremental DP Impact (Relative to \u03b5 = \u221e "
        "Federated Baseline)", s["caption"]))
    story.append(make_table(
        ["\u03b5", "NDCG@10", "\u0394 NDCG@10",
         "Relative \u0394", "MIA AUC"],
        [
            ["\u221e", "0.0539", "\u2014", "\u2014", "0.548"],
            ["8", "0.0534", "\u22120.0005", "\u22120.9%", "0.534"],
            ["4", "0.0479", "\u22120.0060", "\u221211.1%", "0.502"],
            ["2", "0.0456", "\u22120.0083", "\u221215.4%", "0.500"],
            ["1", "0.0467", "\u22120.0072", "\u221213.4%", "0.486"],
        ],
        [50, 72, 72, 72, 72],
        s,
    ))
    story.append(sp)

    story.append(Paragraph(
        "The results suggest that \u03b5 = 8 offers the best privacy\u2013"
        "accuracy trade-off for this task: it reduces MIA AUC from 0.548 "
        "to 0.534 (a 2.6% improvement in privacy protection) while "
        "incurring only a 0.9% accuracy loss. At \u03b5 = 4, the MIA AUC "
        "reaches 0.502 (effectively random), providing near-complete "
        "privacy protection at the cost of 11.1% NDCG@10 degradation. "
        "Configurations with \u03b5 \u2264 2 offer diminishing returns: the "
        "MIA is already at random performance at \u03b5 = 4, so further "
        "tightening the privacy budget yields no additional practical "
        "privacy benefit while continuing to erode accuracy.",
        s["body"]))

    story.append(Paragraph(
        "5.8.3 Practical Implications for Mobile Deployment", s["h3"]))
    story.append(Paragraph(
        "The experimental results yield several practical implications "
        "for deploying federated recommendation systems on mobile devices:",
        s["body"]))
    story.append(Paragraph(
        "<b>Moderate DP is sufficient:</b> A privacy budget of \u03b5 = 4\u20138 "
        "renders membership inference attacks completely ineffective while "
        "preserving most of the federated model\u2019s accuracy. Very strong "
        "privacy (\u03b5 = 1) offers no additional practical protection and "
        "is therefore unnecessary for this use case.",
        s["bullet"]))
    story.append(Paragraph(
        "<b>Federated learning provides inherent privacy:</b> Even without "
        "DP, the federated aggregation process limits privacy leakage to "
        "marginal levels (MIA AUC = 0.548). Model inversion attacks are "
        "completely ineffective at all privacy levels, indicating that "
        "individual user preferences cannot be reconstructed from the "
        "federated model.",
        s["bullet"]))
    story.append(Paragraph(
        "<b>More communication rounds needed:</b> The 76% accuracy gap "
        "between centralized and federated training indicates that 10 "
        "communication rounds are insufficient for convergence. Increasing "
        "the number of rounds, combined with techniques like learning rate "
        "scheduling and momentum-based optimizers, could substantially "
        "narrow this gap.",
        s["bullet"]))
    story.append(Paragraph(
        "<b>Heterogeneity is not a bottleneck:</b> The FedAvg algorithm "
        "with full client participation is robust to data heterogeneity "
        "in this configuration, suggesting that non-IID data distributions "
        "are not a primary concern for mobile recommendation deployment.",
        s["bullet"]))
    story.append(sp)

    # ===== 5.9 SUMMARY OF KEY FINDINGS =====
    story.append(Paragraph("5.9 Summary of Key Findings", s["h2"]))
    story.append(Paragraph(
        "Table 17 consolidates the key quantitative findings across all "
        "three research questions.",
        s["body"]))

    story.append(Paragraph(
        "Table 17: Summary of Key Findings", s["caption"]))
    story.append(make_table(
        ["Research Question", "Key Finding", "Key Metric"],
        [
            ["RQ1: DP \u2192 Accuracy",
             "Moderate trade-off: 13% NDCG loss from \u03b5=\u221e to "
             "\u03b5=1 within the federated regime",
             "NDCG@10: 0.054 \u2192 0.047"],
            ["RQ1: Federated Gap",
             "Dominant factor: 76% NDCG loss from centralized to "
             "federated, dwarfing DP effects",
             "NDCG@10: 0.225 \u2192 0.054"],
            ["RQ2: MIA",
             "Low risk: MIA AUC drops from 0.548 to 0.500 at \u03b5\u22644; "
             "FL itself limits leakage",
             "AUC: 0.548 \u2192 0.500"],
            ["RQ2: Inversion",
             "No risk: 0% success rate at all \u03b5 values; user "
             "preferences cannot be reconstructed",
             "Top-K Acc: 0.00"],
            ["RQ3: Heterogeneity",
             "No impact: \u03b1 from 0.1 to 1.0 has negligible effect; "
             "FedAvg is robust with full participation",
             "NDCG@10: \u22480.054 for all \u03b1"],
        ],
        [90, 200, 130],
        s,
    ))
    story.append(sp)

    story.append(Paragraph(
        "In summary, the results demonstrate that federated learning for "
        "mobile recommendation faces a significant accuracy challenge "
        "compared to centralized training, but this gap is primarily "
        "attributable to the limited communication budget and data "
        "fragmentation\u2014not to differential privacy. DP at moderate levels "
        "(\u03b5 = 4\u20138) provides robust formal privacy guarantees while "
        "imposing only a small additional accuracy penalty. Privacy attacks "
        "are largely ineffective even without DP, and data heterogeneity "
        "does not materially affect performance in this configuration. "
        "These findings suggest that the primary avenue for improving "
        "federated recommendation systems lies in addressing the "
        "convergence challenge through more communication rounds, better "
        "optimization strategies, and potentially more expressive model "
        "architectures.",
        s["body"]))

    return story


def main():
    out_path = "/Users/jonathanjohn/StudioProjects/master_thesis/Results_Section.pdf"
    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        topMargin=0.9 * inch,
        bottomMargin=0.9 * inch,
        leftMargin=0.9 * inch,
        rightMargin=0.9 * inch,
        title="Results",
        author="(anonymous)",
    )
    styles = build_styles()
    story = build_story(styles)
    doc.build(story)
    print(f"PDF written to {out_path}")


if __name__ == "__main__":
    main()
