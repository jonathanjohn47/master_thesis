# 🔬 Experimental Gaps Analysis: What's Missing for Thesis Writing

## Executive Summary

You have a **solid foundation** with a working federated learning system, but you're missing **critical experimental components** required to answer your research questions. This document identifies what needs to be completed before you can write a comprehensive thesis.

---

## ✅ What You Have (Current Status)

### Infrastructure & Implementation
- ✅ **Federated Learning System**: Server (FastAPI), Python clients, Android mobile app
- ✅ **DP-SGD Implementation**: Gradient clipping and Gaussian noise addition in `client.py`
- ✅ **Data Pipeline**: MovieLens 100K loading, preprocessing, non-IID splitting (Dirichlet)
- ✅ **Baseline Experiment**: 100 clients, 10 rounds, α=0.5, dim=16, no DP (ε=∞)
- ✅ **Mobile Validation**: 2 Android devices participated in experiments
- ✅ **Analysis Tools**: Scripts for metrics collection, visualization, and analysis
- ✅ **Results**: Baseline results saved with convergence plots and metrics

### Metrics Collected
- ✅ Training loss per round
- ✅ Test metrics: NDCG@10, Hit@10, Precision, Recall, MSE, MAE, Accuracy
- ✅ Client participation statistics
- ✅ Mobile resource metrics (battery, CPU, memory)

---

## ❌ Critical Missing Components

### 1. **Differential Privacy Budget Sweeps (RQ1) - HIGH PRIORITY**

**Required by Expose:**
- DP budgets: ε ∈ {∞, 8, 4, 2, 1}
- Target: ≤5% accuracy loss relative to centralized baseline

**Current Status:**
- ❌ Only baseline (ε=∞) completed
- ❌ No experiments with ε ∈ {8, 4, 2, 1}
- ❌ No RDP accountant to compute actual ε values
- ❌ No centralized baseline for comparison

**What's Needed:**
1. **Implement RDP Accountant**: 
   - Install `opacus` or `tensorflow-privacy` library
   - Track privacy budget across rounds
   - Compute actual ε given σ, clip_norm, rounds, samples

2. **Create DP Sweep Script**:
   ```python
   # dp_sweep_experiment.py
   DP_EPSILONS = [float('inf'), 8, 4, 2, 1]
   for epsilon in DP_EPSILONS:
       # Calculate sigma for target epsilon
       # Run experiment with DP enabled
       # Collect accuracy metrics
   ```

3. **Run Centralized Baseline**:
   - Train model on all data (no federated learning)
   - Measure baseline NDCG@10, Hit@10
   - Use this as reference for "≤5% accuracy loss"

4. **Generate Accuracy vs ε Plots**:
   - Plot NDCG@10 vs ε
   - Plot Hit@10 vs ε
   - Identify acceptable ε thresholds

**Impact:** **CRITICAL** - This directly answers RQ1 and is a core contribution.

---

### 2. **Privacy Attack Evaluation (RQ2) - HIGH PRIORITY**

**Required by Expose:**
- Membership Inference Attacks (MIA): Target AUC < 0.7
- Model Inversion Attacks: Target top-K accuracy < 5%
- Use AIJack attack modules

**Current Status:**
- ❌ No attack evaluation code
- ❌ AIJack not installed (commented out in requirements.txt)
- ❌ No MIA implementation
- ❌ No model inversion attack implementation
- ❌ No attack metrics collected

**What's Needed:**
1. **Install AIJack**:
   ```bash
   # May require Boost C++ libraries on Windows
   pip install aijack
   ```

2. **Implement MIA Evaluation**:
   - Train shadow models
   - Build attack classifier
   - Evaluate on model updates with different ε values
   - Report AUC scores

3. **Implement Model Inversion Attack**:
   - Attempt to reconstruct training data from model updates
   - Measure top-K reconstruction accuracy
   - Evaluate across different ε values

4. **Integrate into Experiment Pipeline**:
   - Run attacks after each round or at checkpoints
   - Collect attack metrics alongside accuracy metrics
   - Generate Attack AUC vs ε plots

**Impact:** **CRITICAL** - This directly answers RQ2 and validates privacy claims.

---

### 3. **Data Heterogeneity Sweeps (RQ3) - MEDIUM PRIORITY**

**Required by Expose:**
- Heterogeneity: α ∈ {0.1, 0.5, 1.0}
- Client sparsity: local samples ∈ {5, 10, 20, 50}

**Current Status:**
- ✅ α=0.5 implemented and tested
- ❌ α ∈ {0.1, 1.0} not tested
- ❌ Client sparsity experiments not run
- ❌ No analysis of heterogeneity effects on accuracy/privacy

**What's Needed:**
1. **Run α Sweep**:
   ```python
   ALPHA_VALUES = [0.1, 0.5, 1.0]
   for alpha in ALPHA_VALUES:
       # Create non-IID split with this alpha
       # Run experiment
       # Compare accuracy and privacy leakage
   ```

2. **Implement Client Sparsity Experiments**:
   - Restrict local samples per client to {5, 10, 20, 50}
   - Run experiments with sparse data
   - Analyze impact on convergence and privacy

3. **Generate Heterogeneity Analysis**:
   - Plot accuracy vs α
   - Plot privacy leakage vs α
   - Analyze interaction with DP budgets

**Impact:** **IMPORTANT** - Answers RQ3 and shows system robustness.

---

### 4. **Model Dimension & Architecture Sweeps - MEDIUM PRIORITY**

**Required by Expose:**
- Model dimension: {8, 16, 32}
- Model type: {MF, smallNCF}

**Current Status:**
- ✅ dim=16 implemented and tested
- ❌ dim ∈ {8, 32} not tested
- ❌ NCF model not implemented (only MF)

**What's Needed:**
1. **Run Dimension Sweep**:
   - Test with embedding_dim ∈ {8, 16, 32}
   - Compare accuracy, privacy, and resource usage
   - Analyze trade-offs

2. **Implement NCF Model** (Optional but recommended):
   - Small Neural Collaborative Filtering variant
   - Compare with MF baseline
   - Evaluate on mobile devices

**Impact:** **MODERATE** - Shows model size effects, but MF alone may be sufficient.

---

### 5. **Statistical Significance (Multiple Seeds) - MEDIUM PRIORITY**

**Required by Expose:**
- 3 repeats per configuration (different seeds)

**Current Status:**
- ✅ seed=42 used
- ❌ No multiple seeds for statistical significance
- ❌ No confidence intervals or error bars in plots

**What's Needed:**
1. **Run Experiments with Multiple Seeds**:
   ```python
   SEEDS = [42, 123, 456]  # 3 seeds
   for seed in SEEDS:
       # Run experiment with this seed
       # Collect results
   ```

2. **Statistical Analysis**:
   - Compute mean and standard deviation across seeds
   - Add error bars to plots
   - Perform significance tests if needed

**Impact:** **IMPORTANT** - Ensures results are reproducible and statistically sound.

---

### 6. **Resource Profiling Analysis - LOW PRIORITY**

**Required by Expose:**
- Per-round payload (MB)
- Client CPU time
- Memory usage
- Battery cost per round
- Target thresholds: latency < 200ms, CPU < 25%, memory < 150MB, bandwidth < 2MB/round

**Current Status:**
- ✅ Mobile resource metrics collected (battery, CPU, memory)
- ❌ No systematic analysis of resource consumption
- ❌ No comparison against target thresholds
- ❌ No resource vs accuracy/privacy trade-off analysis

**What's Needed:**
1. **Systematic Resource Analysis**:
   - Aggregate resource metrics across experiments
   - Compare against target thresholds
   - Generate resource consumption plots

2. **Pareto Frontier Analysis**:
   - Plot accuracy vs privacy vs bandwidth
   - Identify optimal operating regions
   - Generate 3D or multi-objective plots

**Impact:** **MODERATE** - Important for practical deployment but not core to research questions.

---

### 7. **Centralized Baseline for Comparison - HIGH PRIORITY**

**Required by Expose:**
- Target: ≤5% accuracy loss relative to centralized baseline

**Current Status:**
- ❌ No centralized baseline computed
- ❌ Cannot measure "≤5% accuracy loss" without baseline

**What's Needed:**
1. **Train Centralized Model**:
   - Train on all training data (no federated learning)
   - Use same model architecture (MF, dim=16)
   - Evaluate on same test set
   - Record baseline NDCG@10, Hit@10

2. **Compare Federated Results**:
   - Calculate relative accuracy loss: `(baseline - federated) / baseline`
   - Identify which ε values meet ≤5% threshold
   - Generate comparison plots

**Impact:** **CRITICAL** - Required to answer RQ1 threshold question.

---

## 📊 Experimental Matrix: What Needs to Be Run

Based on your expose, here's the complete experimental grid:

| ε | α | Local Samples | Dim | Seeds | Model | Status |
|---|---|---------------|-----|-------|-------|--------|
| ∞ | 0.5 | All | 16 | 42 | MF | ✅ Done |
| 8 | 0.5 | All | 16 | 42 | MF | ❌ Missing |
| 4 | 0.5 | All | 16 | 42 | MF | ❌ Missing |
| 2 | 0.5 | All | 16 | 42 | MF | ❌ Missing |
| 1 | 0.5 | All | 16 | 42 | MF | ❌ Missing |
| ∞ | 0.1 | All | 16 | 42 | MF | ❌ Missing |
| ∞ | 1.0 | All | 16 | 42 | MF | ❌ Missing |
| ∞ | 0.5 | 5 | 16 | 42 | MF | ❌ Missing |
| ∞ | 0.5 | 10 | 16 | 42 | MF | ❌ Missing |
| ∞ | 0.5 | 20 | 16 | 42 | MF | ❌ Missing |
| ∞ | 0.5 | 50 | 16 | 42 | MF | ❌ Missing |
| ∞ | 0.5 | All | 8 | 42 | MF | ❌ Missing |
| ∞ | 0.5 | All | 32 | 42 | MF | ❌ Missing |
| ∞ | 0.5 | All | 16 | 123, 456 | MF | ❌ Missing |

**Total Experiments Needed:** ~50+ configurations (with 3 seeds each = 150+ runs)

**Minimum Viable Set (for thesis):**
- Centralized baseline (1 run)
- DP sweep: ε ∈ {∞, 8, 4, 2, 1} with α=0.5, dim=16 (5 runs × 3 seeds = 15 runs)
- Attack evaluation for each ε (5 runs)
- Heterogeneity: α ∈ {0.1, 0.5, 1.0} with ε=∞ (3 runs × 3 seeds = 9 runs)
- **Total minimum: ~30-40 experiment runs**

---

## 🎯 Priority Order for Implementation

### Phase 1: Critical for RQ1 & RQ2 (Week 1-2)
1. **Implement RDP Accountant** ⭐⭐⭐
   - Install privacy accounting library
   - Integrate into training loop
   - Verify ε computation

2. **Run Centralized Baseline** ⭐⭐⭐
   - Single experiment
   - Establish reference point
   - Document baseline metrics

3. **Implement DP Sweep** ⭐⭐⭐
   - Create sweep script
   - Run ε ∈ {∞, 8, 4, 2, 1}
   - Collect accuracy metrics
   - Generate accuracy vs ε plots

4. **Implement Attack Evaluation** ⭐⭐⭐
   - Install AIJack
   - Implement MIA
   - Implement model inversion
   - Run attacks on DP models
   - Generate attack AUC vs ε plots

### Phase 2: Important for RQ3 (Week 3)
5. **Run Heterogeneity Sweeps** ⭐⭐
   - α ∈ {0.1, 0.5, 1.0}
   - Analyze effects on accuracy/privacy

6. **Run Multiple Seeds** ⭐⭐
   - 3 seeds per critical configuration
   - Statistical analysis

### Phase 3: Nice to Have (Week 4)
7. **Client Sparsity Experiments** ⭐
   - Local samples ∈ {5, 10, 20, 50}

8. **Model Dimension Sweeps** ⭐
   - dim ∈ {8, 32}

9. **Resource Profiling Analysis** ⭐
   - Systematic resource analysis
   - Pareto frontiers

---

## 📝 Code/Implementation Gaps

### Missing Files/Modules:
1. **`rdp_accountant.py`** - RDP privacy accounting
2. **`attack_evaluation.py`** - MIA and model inversion attacks
3. **`dp_sweep_experiment.py`** - DP budget sweep script
4. **`centralized_baseline.py`** - Centralized training baseline
5. **`heterogeneity_sweep.py`** - Heterogeneity parameter sweep
6. **`statistical_analysis.py`** - Multi-seed statistical analysis

### Missing Dependencies:
- `opacus` or `tensorflow-privacy` (for RDP accounting)
- `aijack` (for attack evaluation)
- Statistical libraries for multi-seed analysis

---

## 🎓 Thesis Writing Readiness

### Can Start Writing Now:
- ✅ **Methodology Section**: System architecture, data preprocessing, FL setup
- ✅ **Baseline Results**: Current experiment results (ε=∞, α=0.5)
- ✅ **System Description**: Server, clients, mobile app implementation

### Need Before Writing:
- ❌ **RQ1 Results**: Accuracy vs ε plots, centralized baseline comparison
- ❌ **RQ2 Results**: Attack evaluation metrics, privacy leakage analysis
- ❌ **RQ3 Results**: Heterogeneity effects, sparsity analysis
- ❌ **Discussion**: Trade-off analysis, practical recommendations

### Minimum Viable Thesis:
To write a complete thesis, you need at minimum:
1. ✅ Centralized baseline (1 experiment)
2. ❌ DP sweep: ε ∈ {∞, 8, 4, 2, 1} (5 experiments × 3 seeds = 15)
3. ❌ Attack evaluation for each ε (5 experiments)
4. ✅ Current baseline (already done)

**Estimated Time:** 2-3 weeks of focused experimental work

---

## 🚀 Recommended Action Plan

### This Week:
1. **Day 1-2**: Implement RDP accountant and centralized baseline
2. **Day 3-4**: Run DP sweep (ε ∈ {∞, 8, 4, 2, 1})
3. **Day 5**: Install AIJack and implement attack evaluation framework

### Next Week:
4. **Day 1-3**: Run attack evaluations for all ε values
5. **Day 4-5**: Run heterogeneity sweeps (α ∈ {0.1, 0.5, 1.0})

### Week 3:
6. **Day 1-2**: Run multiple seeds for critical configurations
7. **Day 3-5**: Statistical analysis, generate all plots, start writing

---

## 💡 Key Takeaways

1. **You have a solid foundation** - The system works, baseline is done
2. **Critical gaps are in DP sweeps and attack evaluation** - These directly answer your RQs
3. **Focus on minimum viable set first** - Don't try to run everything at once
4. **Start with RQ1 & RQ2** - These are the core contributions
5. **Statistical significance can come later** - But include at least 3 seeds for key experiments

---

## 📞 Next Steps

1. **Review this document** with your supervisor
2. **Prioritize experiments** based on thesis timeline
3. **Start with Phase 1** (RDP accountant + DP sweep)
4. **Document everything** as you implement
5. **Generate plots incrementally** - don't wait until the end

**You're about 40% done with experiments. Focus on the critical gaps (DP sweeps + attacks) and you'll be ready to write!** 🎯

