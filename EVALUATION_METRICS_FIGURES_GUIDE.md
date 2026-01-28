# Evaluation Metrics: Recommended Figures and Data to Include

This document provides recommendations for figures, graphs, and data tables that should be included in the "Evaluation Metrics" section to support the written content and provide visual evidence of your experimental findings.

## Essential Figures to Include

### 1. **Metric Definition Illustrations**

**Figure: NDCG@10 Calculation Example**
- **Type**: Diagram or flowchart
- **Purpose**: Illustrate how NDCG@10 is computed step-by-step
- **Content**: 
  - Show an example user with ranked recommendations
  - Visualize the DCG calculation with position-based discounting
  - Show IDCG for comparison
  - Include a numerical example with actual values
- **Placement**: Early in the Evaluation Metrics section, after introducing NDCG@10

**Figure: Top-K Recommendation Ranking Visualization**
- **Type**: Schematic diagram
- **Purpose**: Show how top-K metrics (Hit@10, Precision@10, Recall@10) are computed
- **Content**:
  - Visual representation of a ranked list with relevant/irrelevant items marked
  - Highlight which items are in top-10
  - Show how precision, recall, and hit rate are calculated from this ranking
- **Placement**: After introducing the top-K metrics subsection

### 2. **Privacy-Utility Trade-off Visualizations**

**Figure: Accuracy vs. DP Budget (ε)**
- **Type**: Line plot with error bars
- **Data Source**: `figures/accuracy_vs_epsilon.png` (already generated)
- **Content**:
  - X-axis: DP Budget (ε) values: [∞, 8, 4, 2, 1]
  - Y-axis: NDCG@10 and Hit@10 values
  - Include both federated learning results and centralized baseline (horizontal line)
  - Error bars showing standard deviation across multiple runs
  - Use different markers/colors for different metrics
- **Additional variants to consider**:
  - Separate subplots for NDCG@10 and Hit@10
  - Include Precision@10 and Recall@10 as well
- **Caption**: Should explain the trade-off trend and compare to baseline

**Figure: Relative Accuracy Loss vs. DP Budget**
- **Type**: Line plot or bar chart
- **Data Source**: `figures/accuracy_loss_vs_epsilon.png` (already generated)
- **Content**:
  - X-axis: DP Budget (ε) values
  - Y-axis: Percentage accuracy loss relative to centralized baseline
  - Show both NDCG@10 and Hit@10 loss percentages
  - Highlight the 5% loss threshold line (if that's your target)
- **Caption**: Should discuss which epsilon values meet utility targets

### 3. **Convergence Analysis**

**Figure: Training Convergence Over Rounds**
- **Type**: Multi-panel line plot
- **Data Source**: `figures/convergence.png` (already generated)
- **Content**:
  - Panel 1: Training Loss vs. Rounds
  - Panel 2: Hit@10 vs. Rounds
  - Panel 3: NDCG@10 vs. Rounds (or Test Accuracy)
  - Panel 4: MSE vs. Rounds
  - Show curves for different epsilon values (overlay or subplot)
- **Variants**:
  - Separate plots for each epsilon value for clarity
  - Combined plot with different colors/linestyles for each epsilon
- **Caption**: Should discuss convergence speed and stability under different privacy levels

**Figure: Convergence Comparison: With vs. Without DP**
- **Type**: Overlaid line plots
- **Purpose**: Direct comparison of convergence behavior
- **Content**:
  - Compare ε=∞ (no DP) with ε=1, ε=2, ε=4, ε=8
  - Focus on key metrics: Loss, Hit@10, NDCG@10
  - Show how noise affects convergence rate and final performance
- **Caption**: Analyze how differential privacy impacts training dynamics

### 4. **Data Heterogeneity Analysis**

**Figure: Accuracy vs. Data Heterogeneity (α)**
- **Type**: Line plot with error bars
- **Data Source**: `figures/accuracy_vs_alpha.png` (already generated)
- **Content**:
  - X-axis: Dirichlet parameter α values (e.g., 0.1, 0.5, 1.0)
  - Y-axis: NDCG@10 and Hit@10
  - Show how non-IID data distribution affects model performance
  - Error bars for statistical significance
- **Caption**: Discuss the impact of data heterogeneity on recommendation quality

### 5. **Comprehensive Comparison Tables**

**Table: Summary Statistics Across All Configurations**
- **Type**: Data table (CSV or LaTeX table)
- **Data Source**: `figures/summary_table.csv` (already generated)
- **Content**:
  - Rows: Different experiment configurations (epsilon, alpha combinations)
  - Columns: All evaluation metrics (NDCG@10, Hit@10, Precision@10, Recall@10, MSE, MAE, Accuracy)
  - Include mean and standard deviation for each metric
  - Highlight best/worst performing configurations
- **Additional columns to consider**:
  - Relative loss compared to baseline (%)
  - Training time or convergence round
  - Privacy budget consumed (actual epsilon if tracked)
- **Placement**: Near the end of Evaluation Metrics section or in Results section

**Table: Baseline Comparison Table**
- **Type**: Comparative table
- **Content**:
  - Centralized baseline metrics (no FL, no DP)
  - Federated learning baseline (FL with ε=∞)
  - Federated learning with DP (ε=8, 4, 2, 1)
  - Show absolute values and relative differences
  - Include percentage degradation for each privacy level
- **Purpose**: Clear comparison showing the cost of privacy

### 6. **Distribution and Variability Analysis**

**Figure: Metric Distributions Across Users**
- **Type**: Box plots or violin plots
- **Purpose**: Show distribution of metrics across users, not just averages
- **Content**:
  - Box plots showing NDCG@10 distribution per user for different epsilon values
  - Similar plots for Hit@10
  - Show median, quartiles, and outliers
- **Insight**: Reveals whether some users are disproportionately affected by privacy mechanisms

**Figure: Standard Deviation Analysis**
- **Type**: Bar chart with error bars
- **Purpose**: Show variability across experimental runs
- **Content**:
  - Mean metric values (bars) with standard deviation (error bars)
  - Compare variability across different epsilon values
  - Helps assess result reliability
- **Caption**: Discuss consistency and reproducibility of results

### 7. **Recommendation Quality Breakdown**

**Figure: Recommendation Metrics Breakdown**
- **Type**: Grouped bar chart
- **Data Source**: `figures/recommendation_metrics.png` (may need to generate)
- **Content**:
  - Groups: Different epsilon values
  - Bars: NDCG@10, Hit@10, Precision@10, Recall@10
  - Visual comparison across all recommendation metrics simultaneously
- **Purpose**: Comprehensive view of recommendation quality across privacy levels

**Figure: Precision-Recall Curves**
- **Type**: Line plot (if applicable)
- **Purpose**: Show precision-recall trade-off
- **Content**:
  - Different curves for different epsilon values
  - X-axis: Recall@10
  - Y-axis: Precision@10
  - Shows the balance between precision and recall under different privacy constraints
- **Note**: This might require computing metrics at different k values

### 8. **Ablation Study Visualizations** (If Applicable)

**Figure: Component Contribution Analysis**
- **Type**: Bar chart or waterfall chart
- **Purpose**: Show how each component (federated learning, DP, etc.) affects performance
- **Content**:
  - Baseline (centralized, no DP)
  - Effect of federated learning alone
  - Additional effect of DP at different epsilon levels
  - Shows incremental cost of each privacy mechanism

## Data Tables to Include

### Table 1: Metric Definitions and Ranges
- **Columns**: Metric Name, Definition/Formula, Range, Interpretation
- **Rows**: All metrics (NDCG@10, Hit@10, Precision@10, Recall@10, MSE, MAE, Accuracy)
- **Purpose**: Quick reference for readers

### Table 2: Evaluation Configuration
- **Columns**: Parameter, Value/Description
- **Content**: 
  - Test set size (20% of data)
  - Number of experimental runs per configuration
  - Random seeds used
  - Evaluation methodology details
- **Purpose**: Reproducibility information

### Table 3: Final Performance Summary
- **Content**: Mean and standard deviation of all metrics for key configurations
- **Highlight**: Best performing configurations
- **Include**: Statistical significance indicators if applicable

## Additional Visualizations to Consider

### 9. **Per-Round Evolution**

**Figure: Metric Evolution Throughout Training**
- **Type**: Time series line plots (already in convergence.png, but can expand)
- **Content**: Show how each metric improves over rounds for different privacy levels
- **Purpose**: Understand learning dynamics and convergence patterns

### 10. **Client Participation Analysis**

**Figure: Client Distribution and Participation**
- **Type**: Histogram or bar chart
- **Data Source**: `figures/client_distribution.png` (already generated)
- **Content**: 
  - Distribution of samples per client
  - Client participation statistics
  - Helps understand data heterogeneity
- **Caption**: Relate to non-IID challenges

### 11. **Privacy Budget Consumption**

**Figure: Privacy Budget Usage Over Rounds** (If tracked)
- **Type**: Line plot or stacked area chart
- **Purpose**: Show how privacy budget accumulates during training
- **Content**:
  - Cumulative epsilon consumption per round
  - Compare for different initial epsilon budgets
  - Show RDP accounting results
- **Note**: This might require additional tracking in your experiments

## Recommendations for Figure Placement

1. **In Evaluation Metrics Section**:
   - Metric definition illustrations (Figure 1-2)
   - Tables 1-2 (definitions and configuration)
   - Maybe one key visualization showing metric computation

2. **In Results Section** (cross-reference from Evaluation Metrics):
   - Privacy-utility trade-off plots (Figure 2)
   - Convergence plots (Figure 3)
   - Summary tables (Table 3)
   - All other performance analysis figures

## Formatting Recommendations

- **Resolution**: All figures should be high-resolution (300 DPI minimum for publication)
- **Font sizes**: Ensure text is readable when scaled down
- **Color schemes**: Use colorblind-friendly palettes (consider grayscale variants for print)
- **Axis labels**: Clear, descriptive labels with units where applicable
- **Legends**: Well-positioned, clear legends
- **Captions**: Comprehensive captions explaining what the figure shows and key insights
- **Consistency**: Use consistent color coding across all figures (same color = same epsilon value, etc.)

## Code References

Your existing analysis scripts generate several of these figures:
- `comprehensive_analysis.py`: Generates accuracy_vs_epsilon.png, accuracy_vs_alpha.png
- `analyze_results.py`: Generates convergence.png, recommendation_metrics.png
- Check `figures/` directory for already-generated visualizations

## Next Steps

1. Review existing figures in `figures/` directory
2. Generate any missing visualizations using your analysis scripts
3. Create metric definition illustrations if needed (may require manual creation)
4. Prepare summary tables from your experimental results
5. Write captions for each figure explaining the key insights
6. Cross-reference figures appropriately in the text





