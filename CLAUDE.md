# CLAUDE.md

## Project Overview

Master's thesis: **"Empirical Analysis of Accuracy-Privacy Trade-offs in Federated Learning for Mobile Movie Recommendation Systems"**

This project implements a federated learning (FL) system for movie recommendations using the MovieLens 100K dataset. It includes a Python-based FL server/client system with differential privacy (DP-SGD), a Flutter mobile app for real-device participation, experiment orchestration scripts, privacy attack evaluation, and result analysis/visualization tools.

### Research Questions

- **RQ1**: How does the differential privacy budget (epsilon) impact recommendation accuracy?
- **RQ2**: How effective are privacy attacks (membership inference, model inversion) under different DP budgets?
- **RQ3**: How do data heterogeneity and client sparsity affect accuracy and privacy?

## Repository Structure

```
master_thesis/
├── server.py                  # FastAPI federated learning server (port 8000)
├── client.py                  # FL client with DP-SGD support
├── run_experiment.py          # Single experiment runner
├── run_all_experiments.py     # Master orchestrator for all experiments
├── run_complete_experiment.py # Extended experiment suite
├── dp_sweep_experiment.py     # DP epsilon sweep (RQ1)
├── heterogeneity_sweep_experiment.py  # Dirichlet alpha sweep (RQ3)
├── centralized_baseline.py    # Centralized training baseline
├── comprehensive_analysis.py  # Analysis and figure generation
├── analyze_results.py         # Result processing
├── analyze_combined_results.py # Python + Android hybrid analysis
├── quick_summary.py           # Quick statistics display
├── show_summary.py            # Experiment summary printer
├── init_server_model.py       # Server model initialization helper
├── start_server.py            # Server launcher
├── generate_*.py              # PDF/DOCX document generation scripts
├── test_model_fixes.py        # Model convergence tests
├── test_data_collection.py    # Data validation tests
├── quick_test.py              # Quick test script
├── requirements.txt           # Python dependencies
│
├── scripts/                   # Core utility modules
│   ├── __init__.py
│   ├── rdp_accountant.py      # Renyi DP accounting (epsilon/delta tracking)
│   ├── metrics_collector.py   # Training metrics aggregation
│   ├── recommendation_metrics.py  # NDCG@K, Hit@K, Precision@K, Recall@K
│   └── attack_evaluation.py   # MIA and model inversion attacks
│
├── federated_learning_in_mobile/  # Flutter/Dart mobile app
│   ├── lib/
│   │   ├── main.dart              # UI and training flow
│   │   ├── models/
│   │   │   └── matrix_factorization.dart  # Pure Dart ML model
│   │   ├── services/
│   │   │   ├── api_client.dart    # HTTP server communication
│   │   │   └── fl_client.dart     # FL client logic
│   │   └── utils/
│   │       ├── model_encoder.dart     # Parameter encoding/decoding
│   │       ├── metrics_collector.dart # Metrics collection
│   │       └── resource_monitor.dart  # Battery/CPU/memory monitoring
│   ├── android/                   # Android build config
│   ├── pubspec.yaml               # Flutter dependencies
│   └── README.md
│
├── ml-100k/                   # MovieLens 100K dataset
├── results/                   # Experiment outputs (JSON + CSV)
├── mobile_results/            # Real Android device results
├── figures/                   # Generated visualization PNGs
├── thesis_expose/             # Thesis expose documentation
└── results_old_broken/        # Archived old results
```

## Tech Stack

### Python (Server + Experiments)

| Component | Technology |
|-----------|-----------|
| ML Framework | PyTorch (>=2.0) |
| Server | FastAPI + Uvicorn |
| Data | NumPy, Pandas |
| ML Utilities | scikit-learn |
| Visualization | matplotlib, seaborn |
| HTTP Client | requests |

### Mobile App

| Component | Technology |
|-----------|-----------|
| Framework | Flutter (>=3.9.2) |
| Language | Dart |
| ML Model | Pure Dart (no external ML lib) |
| Device APIs | device_info_plus, battery_plus |

## Setup and Running

### Python Environment

```bash
pip install -r requirements.txt
```

### Running Experiments

```bash
# Start the FL server (port 8000)
python server.py

# Initialize the global model (in a second terminal)
python init_server_model.py

# Run a single experiment
python run_experiment.py

# Run all experiments (DP sweep + heterogeneity sweep + analysis)
python run_all_experiments.py

# Run only DP epsilon sweep (RQ1)
python dp_sweep_experiment.py

# Run only heterogeneity sweep (RQ3)
python heterogeneity_sweep_experiment.py

# Generate analysis figures
python comprehensive_analysis.py
```

### Mobile App

```bash
cd federated_learning_in_mobile
flutter pub get
flutter run
```

The mobile app must be configured with the server's IP address (not `localhost` for physical devices).

## Architecture

### Federated Learning Flow

1. **Server** (`server.py`): FastAPI app managing the global model state
   - Endpoints: `/register`, `/init-model`, `/global-params-json`, `/upload-params-json`
   - Parameters serialized as Base64-encoded Float32 arrays
   - Aggregation: FedAvg (weighted by client sample count)

2. **Client** (`client.py`): Simulated FL clients
   - Matrix factorization model (user/item embeddings)
   - Local training with SGD, optional DP-SGD (gradient clipping + Gaussian noise)
   - Non-IID data splitting via Dirichlet distribution

3. **Mobile Client** (`federated_learning_in_mobile/`): Real-device FL client
   - Pure Dart matrix factorization (compatible with PyTorch model)
   - Same JSON + Base64 parameter protocol as Python clients

### Model

- **Type**: Matrix Factorization for collaborative filtering
- **Dimensions**: 943 users x 1,682 items (MovieLens 100K)
- **Embedding dim**: 64 (experiments), 16 (mobile)
- **Loss**: Binary Cross-Entropy with sigmoid activation
- **Optimizer**: SGD (lr=0.01)

### Differential Privacy

- **Mechanism**: DP-SGD (per-sample gradient clipping + Gaussian noise)
- **Clipping norm**: 1.0
- **Epsilon values tested**: infinity, 8, 4, 2, 1
- **Delta**: 1e-5
- **Accounting**: Renyi Differential Privacy (`scripts/rdp_accountant.py`)

### Privacy Attacks (`scripts/attack_evaluation.py`)

- Membership Inference Attack (MIA) using shadow models + Random Forest classifier
- Model Inversion Attack (gradient-based feature reconstruction)

## Key Conventions

### Code Organization

- Root-level `.py` files are runnable scripts (experiments, server, analysis)
- Reusable modules live in `scripts/`
- Mobile app follows standard Flutter project structure under `federated_learning_in_mobile/`

### Data Flow

- Dataset: `ml-100k/u.data` (tab-separated: user_id, item_id, rating, timestamp)
- Results: `results/*.json` (full metrics) + `results/*_summary.csv` (aggregated)
- Figures: `figures/*.png`
- Mobile results: `mobile_results/`

### Experiment Naming Convention

Result files follow this pattern:
```
dp_{epsilon}_alpha_{alpha}_dim_{dim}_clients_{clients}_seed_{seed}.json
```

### Parameter Serialization

Python and Dart clients use the same protocol: model parameters are serialized as Base64-encoded Float32 arrays in JSON. This enables interoperability between PyTorch (Python) and pure Dart (mobile) implementations.

### Experiment Parameters

| Parameter | Default | Range Tested |
|-----------|---------|-------------|
| Epsilon (DP budget) | inf (no DP) | inf, 8, 4, 2, 1 |
| Alpha (Dirichlet) | 0.5 | 0.1, 0.5, 1.0 |
| Embedding dim | 64 | 16 (mobile), 64 |
| Num clients | 100 | 100 |
| Rounds | 10 | 10-50 |
| Local epochs | 1 | 1-3 |
| Batch size | 32 | 32 |
| Learning rate | 0.01 | 0.01 |
| Random seeds | [42, 123, 456] | 3 seeds per config |

## Testing

There is no formal test framework (no pytest/unittest configuration). Validation is done through:

- `test_model_fixes.py` - Tests model convergence and metric computation
- `test_data_collection.py` - Validates CSV data loading and preprocessing
- `quick_test.py` - Quick validation script
- Integration testing via experiment runners

Run tests:
```bash
python test_model_fixes.py
python test_data_collection.py
```

## CI/CD

No CI/CD pipeline is configured. Experiments and tests are run manually.

## Important Notes for AI Assistants

- The `scripts/` directory is an importable Python package (has `__init__.py`). Import with `from scripts.rdp_accountant import ...`.
- The server must be running before clients can train. Use `python server.py` in one terminal and experiment scripts in another.
- AIJack library is commented out in `requirements.txt` due to Boost C++ dependency issues. The `scripts/attack_evaluation.py` implements attacks natively without AIJack.
- The mobile app's Dart matrix factorization implementation must stay compatible with the PyTorch model's parameter format. Changes to model architecture require updates in both Python and Dart.
- Results in `results/` and `figures/` are generated artifacts. They can be regenerated by re-running experiments and analysis scripts.
- The `.gitignore` is minimal (only `__pycache__/`). Be cautious not to commit large binary files or sensitive data.
- MovieLens 100K dataset (`ml-100k/`) is committed to the repo for reproducibility.
