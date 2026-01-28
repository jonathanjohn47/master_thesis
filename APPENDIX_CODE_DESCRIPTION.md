# Appendix: Code Description and Implementation Details

This appendix provides a comprehensive overview of the codebase structure, implementation details, and instructions for running the federated learning experiments for mobile movie recommendation systems.

## Table of Contents

1. [Code Structure](#code-structure)
2. [Folder Organization](#folder-organization)
3. [Running the Code](#running-the-code)
4. [Repository Information](#repository-information)
5. [Key Components](#key-components)
6. [Dependencies](#dependencies)

---

## Code Structure

The codebase is organized into two main components:

1. **Python Server and Client Implementation** - Core federated learning infrastructure
2. **Mobile Application (Flutter/Dart)** - Android client for real device participation

### Python Implementation

The Python codebase implements a client-server federated learning architecture using:

- **FastAPI** for RESTful server endpoints
- **PyTorch** for neural network models and training
- **NumPy/Pandas** for data processing
- **Rényi Differential Privacy (RDP)** accountant for privacy budget tracking

### Mobile Implementation

The mobile application is built using:

- **Flutter/Dart** for cross-platform mobile development
- **Pure Dart** implementation of Matrix Factorization model
- **HTTP client** for server communication
- **Resource monitoring** APIs for battery, CPU, and memory tracking

---

## Folder Organization

### Root Directory Structure

```
master_thesis/
├── server.py                          # FastAPI server for federated learning
├── client.py                          # Python federated learning client
├── run_experiment.py                  # Single experiment runner
├── run_all_experiments.py             # Master experiment orchestrator
├── centralized_baseline.py            # Centralized training baseline
├── dp_sweep_experiment.py             # Differential privacy budget sweep
├── heterogeneity_sweep_experiment.py  # Data heterogeneity sweep
├── comprehensive_analysis.py          # Results analysis and visualization
├── analyze_results.py                 # Result analysis utilities
├── analyze_combined_results.py        # Combined results analysis
├── quick_summary.py                   # Quick result summaries
├── show_summary.py                    # Display experiment summaries
├── init_server_model.py               # Server model initialization
├── start_server.py                    # Server startup helper
├── test_data_collection.py            # Data collection testing
├── requirements.txt                   # Python dependencies
├── ratings.csv                        # MovieLens dataset
│
├── scripts/                           # Utility scripts
│   ├── __init__.py
│   ├── rdp_accountant.py             # RDP privacy accountant
│   ├── metrics_collector.py          # Metrics collection utilities
│   ├── recommendation_metrics.py      # Recommendation evaluation metrics
│   └── attack_evaluation.py          # Privacy attack evaluation
│
├── federated_learning_in_mobile/      # Mobile application
│   ├── lib/                           # Dart source code
│   │   ├── main.dart                  # Main app entry point
│   │   ├── models/
│   │   │   └── matrix_factorization.dart  # Matrix factorization model
│   │   ├── services/
│   │   │   ├── api_client.dart       # HTTP client for server
│   │   │   └── fl_client.dart        # Federated learning client logic
│   │   └── utils/
│   │       ├── metrics_collector.dart    # Metrics collection
│   │       ├── model_encoder.dart       # Model parameter encoding
│   │       └── resource_monitor.dart     # Resource monitoring
│   ├── android/                       # Android-specific configuration
│   ├── ios/                           # iOS-specific configuration
│   ├── pubspec.yaml                   # Flutter dependencies
│   └── README.md                      # Mobile app documentation
│
├── results/                           # Experiment results (JSON/CSV)
├── mobile_results/                   # Mobile device experiment results
├── figures/                           # Generated plots and visualizations
│   ├── accuracy_vs_epsilon.png
│   ├── accuracy_vs_alpha.png
│   ├── convergence.png
│   ├── recommendation_metrics.png
│   └── summary_table.csv
│
└── [Documentation files]             # Various .md guide files
```

### Key Directories Explained

#### `scripts/` - Core Utilities

- **`rdp_accountant.py`**: Implements the Rényi Differential Privacy accountant for tracking privacy budget consumption. Provides methods to compute RDP parameters, convert to (ε, δ)-DP, and track cumulative privacy loss across federated rounds.

- **`metrics_collector.py`**: Handles collection and serialization of experiment metrics, including training loss, recommendation metrics, and resource usage statistics.

- **`recommendation_metrics.py`**: Implements evaluation metrics for recommendation systems, including Hit Rate@K, NDCG@K, Precision@K, Recall@K, and F1-score.

- **`attack_evaluation.py`**: Provides utilities for evaluating privacy attacks (membership inference, attribute inference, gradient inversion).

#### `federated_learning_in_mobile/` - Mobile Application

- **`lib/main.dart`**: Main Flutter application entry point, containing the UI for connecting to the server, running training rounds, and displaying metrics.

- **`lib/models/matrix_factorization.dart`**: Pure Dart implementation of the Matrix Factorization model, compatible with the Python PyTorch version.

- **`lib/services/fl_client.dart`**: Core federated learning client logic, handling model download, local training, and parameter upload.

- **`lib/services/api_client.dart`**: HTTP client wrapper for communicating with the FastAPI server.

- **`lib/utils/`**: Utility modules for model encoding/decoding, metrics collection, and resource monitoring.

#### `results/` - Experiment Outputs

Contains JSON and CSV files with experiment results, including:
- Per-round metrics (loss, accuracy, recommendation metrics)
- Final aggregated results
- Client-level statistics
- Privacy budget consumption

#### `figures/` - Visualizations

Generated plots and tables from `comprehensive_analysis.py`, including:
- Privacy-utility trade-off curves
- Convergence plots
- Heterogeneity impact analysis
- Summary statistics tables

---

## Running the Code

### Prerequisites

1. **Python Environment** (Python 3.8+)
   ```bash
   pip install -r requirements.txt
   ```

2. **Dataset**: Ensure `ratings.csv` (MovieLens 100K) is in the project root

3. **Flutter SDK** (for mobile app, optional): Flutter 3.9.2+
   ```bash
   cd federated_learning_in_mobile
   flutter pub get
   ```

### Quick Start: Running All Experiments

The simplest way to run all experiments is using the master orchestrator:

```bash
# Terminal 1: Start the federated learning server
python server.py

# Terminal 2: Run all experiments
python run_all_experiments.py
```

This will execute:
1. Centralized baseline (no server needed)
2. DP sweep experiments (ε ∈ {∞, 8, 4, 2, 1})
3. Heterogeneity sweep experiments (α ∈ {0.1, 0.5, 1.0})
4. Comprehensive analysis and visualization

**Estimated Time**: 4-8 hours (depending on hardware)

### Running Individual Experiments

#### 1. Centralized Baseline

Establishes the performance upper bound without federated learning:

```bash
python centralized_baseline.py
```

**Output**: `results/centralized_baseline.json`

#### 2. Differential Privacy Sweep

Evaluates accuracy-privacy trade-offs across different privacy budgets:

```bash
# Ensure server is running first
python server.py  # In another terminal

# Run DP sweep
python dp_sweep_experiment.py
```

**Configuration**: Tests ε ∈ {∞, 8, 4, 2, 1} with 3 random seeds each
**Output**: `results/dp_*_alpha_0.5_dim_16_clients_100_seed_*.json`

#### 3. Heterogeneity Sweep

Assesses impact of non-IID data distributions:

```bash
# Server should still be running
python heterogeneity_sweep_experiment.py
```

**Configuration**: Tests α ∈ {0.1, 0.5, 1.0} with 3 random seeds each
**Output**: `results/dp_*_alpha_*_dim_16_clients_100_seed_*.json`

#### 4. Single Experiment

Run a single federated learning experiment:

```bash
# Terminal 1: Start server
python server.py

# Terminal 2: Run experiment
python run_experiment.py
```

#### 5. Analysis and Visualization

Generate plots and summary tables:

```bash
python comprehensive_analysis.py
```

**Output**: 
- `figures/accuracy_vs_epsilon.png`
- `figures/accuracy_vs_alpha.png`
- `figures/convergence.png`
- `figures/recommendation_metrics.png`
- `figures/summary_table.csv`

### Running with Mobile Devices

#### Server Setup

1. Start the server:
   ```bash
   python server.py
   ```

2. Make server accessible:
   - **Local Network**: Use your PC's local IP (e.g., `192.168.1.100:8000`)
   - **External Access**: Use ngrok or similar tunneling service

#### Mobile App Setup

1. Navigate to mobile app directory:
   ```bash
   cd federated_learning_in_mobile
   ```

2. Install dependencies:
   ```bash
   flutter pub get
   ```

3. Run on Android device/emulator:
   ```bash
   flutter run
   ```

4. In the app:
   - Enter server URL (e.g., `http://192.168.1.100:8000`)
   - Enter unique Client ID
   - Click "Connect to Server"
   - Run training rounds

#### Hybrid Experiments

You can run experiments with both Python clients and mobile devices simultaneously:
- Multiple Python clients (for large-scale parameter sweeps)
- 2+ Android devices (for real mobile validation)
- All connect to the same server
- Server aggregates all updates together

---

## Repository Information

### Code Repository

The complete codebase is available at:

**[Repository URL to be added]**

*(Note: Please add your GitHub/GitLab repository URL here)*

### Repository Structure

The repository follows a standard Python/Flutter project structure with:
- Clear separation between server, client, and mobile components
- Modular scripts for different experiment types
- Comprehensive documentation in markdown files
- Results and figures directories for outputs

### Version Control

The codebase uses Git for version control. Key branches:
- `main`: Stable production code
- `experiments`: Experimental features and variations
- `mobile`: Mobile-specific implementations

### License

This project is part of a Master's thesis research project. All code is provided for reproducibility and academic purposes.

---

## Key Components

### Server (`server.py`)

The FastAPI server orchestrates federated learning:

**Key Features**:
- RESTful API endpoints for client registration, model download, and parameter upload
- Weighted federated averaging (FedAvg) aggregation
- Model parameter serialization in portable JSON format (base64-encoded Float32)
- Support for multiple concurrent clients (Python and mobile)
- Health check and status endpoints

**Main Endpoints**:
- `POST /register`: Client registration
- `GET /global-params-json`: Download global model parameters
- `POST /upload-params-json`: Upload local model updates
- `GET /healthz`: Health check
- `POST /mobile-results`: Receive mobile device metrics

**Model Architecture**:
- Matrix Factorization with embedding dimension 16
- User and item embedding matrices
- MSE loss for rating prediction

### Client (`client.py`)

Python federated learning client implementation:

**Key Features**:
- Local model training on client-specific data partitions
- DP-SGD support with gradient clipping and noise addition
- Non-IID data partitioning via Dirichlet distribution
- Automatic server connection and round participation
- Metrics collection and logging

**Configuration**:
- Embedding dimension: 16
- Learning rate: 0.01
- Batch size: 32
- Local epochs: 1
- Gradient clipping norm: 1.0
- DP noise multiplier: calibrated via RDP accountant

### RDP Accountant (`scripts/rdp_accountant.py`)

Privacy budget tracking using Rényi Differential Privacy:

**Key Features**:
- Computes RDP parameters for Gaussian mechanism
- Converts RDP to (ε, δ)-DP guarantees
- Tracks cumulative privacy loss across rounds
- Supports privacy amplification via subsampling
- Binary search for optimal noise multiplier calibration

**Mathematical Foundation**:
- RDP order α ∈ [1.1, 64]
- Gaussian mechanism: RDP_α = α / (2σ²)
- Composition: additive over rounds
- Conversion: ε = min_α [RDP_α + log(1/δ)/(α-1)]

### Mobile Client (`federated_learning_in_mobile/lib/`)

Flutter/Dart mobile application:

**Key Features**:
- Pure Dart Matrix Factorization model (compatible with Python version)
- HTTP-based communication with FastAPI server
- Resource monitoring (battery, CPU, memory)
- Real-time metrics display
- Results export to CSV/JSON

**Architecture**:
- `main.dart`: UI and app orchestration
- `fl_client.dart`: Federated learning client logic
- `api_client.dart`: Server communication
- `matrix_factorization.dart`: Model implementation
- `resource_monitor.dart`: Device resource tracking

---

## Dependencies

### Python Dependencies (`requirements.txt`)

```
fastapi>=0.104.0          # Web framework for server
uvicorn>=0.24.0           # ASGI server
pydantic>=2.0.0           # Data validation
torch>=2.0.0              # Deep learning framework
numpy>=1.24.0             # Numerical computing
pandas>=2.0.0             # Data manipulation
requests>=2.31.0          # HTTP client
scikit-learn>=1.3.0       # Machine learning utilities
matplotlib>=3.7.0         # Plotting
seaborn>=0.12.0           # Statistical visualization
```

### Flutter Dependencies (`federated_learning_in_mobile/pubspec.yaml`)

```yaml
dependencies:
  flutter: sdk
  http: ^1.1.0                    # HTTP client
  device_info_plus: ^10.1.0        # Device information
  battery_plus: ^6.0.2            # Battery monitoring
  path_provider: ^2.1.1            # File system access
  csv: ^5.1.1                      # CSV export
  share_plus: ^7.2.1               # File sharing
  open_filex: ^4.3.3               # File opening
```

### System Requirements

**Server**:
- Python 3.8+
- 4+ GB RAM recommended
- Network access for client connections

**Mobile App**:
- Flutter SDK 3.9.2+
- Android SDK (API level 21+)
- iOS 12+ (for iOS builds)

---

## Additional Documentation

The codebase includes extensive documentation in markdown files:

- `BEGINNER_GUIDE_TO_THESIS.md`: Getting started guide
- `EXPERIMENT_GUIDE.md`: Detailed experiment instructions
- `EXPERIMENT_RUNNER_GUIDE.md`: Complete experiment runner documentation
- `DATA_COLLECTION_GUIDE.md`: Data collection procedures
- `DATA_ANALYSIS_GUIDE.md`: Result analysis guide
- `MOBILE_APP_SETUP_STEPS.md`: Mobile app setup instructions
- `federated_learning_in_mobile/README.md`: Mobile app documentation

---

## Code Execution Flow

### Federated Learning Round

1. **Server Initialization**: Server initializes global model with random weights
2. **Client Registration**: Clients register with server and receive client IDs
3. **Model Download**: Clients download current global model parameters
4. **Local Training**: Each client trains locally on their data partition
   - Forward pass: compute predictions
   - Backward pass: compute gradients
   - DP-SGD: clip gradients and add noise (if enabled)
   - Update: apply optimizer step
5. **Parameter Upload**: Clients upload updated parameters to server
6. **Aggregation**: Server performs weighted FedAvg aggregation
7. **Broadcast**: Server broadcasts updated global model
8. **Repeat**: Steps 3-7 for multiple rounds

### Experiment Execution

1. **Data Loading**: Load and preprocess MovieLens dataset
2. **Data Partitioning**: Split data into train/test sets and client partitions
3. **Model Initialization**: Initialize server model
4. **Federated Training**: Execute multiple federated rounds
5. **Evaluation**: Evaluate model on test set after each round
6. **Metrics Collection**: Collect and log all metrics
7. **Result Serialization**: Save results to JSON/CSV files
8. **Analysis**: Generate plots and summary tables

---

## Troubleshooting

### Common Issues

1. **Server Connection Failed**:
   - Ensure server is running: `python server.py`
   - Check server URL (use IP address, not localhost for mobile)
   - Verify network connectivity

2. **Import Errors**:
   - Install dependencies: `pip install -r requirements.txt`
   - Check Python version (3.8+)

3. **Model Dimension Mismatch**:
   - Ensure embedding dimensions match between server and clients
   - Check model initialization parameters

4. **Mobile App Build Errors**:
   - Run `flutter pub get` to install dependencies
   - Check Flutter SDK version: `flutter --version`
   - Verify Android SDK is properly configured

---

## Contact and Support

For questions or issues regarding the codebase, please refer to:
- The main thesis document for theoretical background
- Individual markdown guide files for specific procedures
- Code comments and docstrings for implementation details

---

*This appendix provides a comprehensive overview of the codebase structure and execution procedures. For detailed implementation specifics, please refer to the source code comments and documentation files.*

