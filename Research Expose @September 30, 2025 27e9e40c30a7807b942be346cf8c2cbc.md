# Research Expose @September 30, 2025

Title: Empirical Analysis of Accuracy–Privacy Trade-offs in Federated Learning for Mobile Movie Recommendation Systems

Author: Jonathan John — [M.Sc](http://m.sc/). Artificial Intelligence (120 ECTS)

Supervisor: Nghia Duong‑Trung

Date: September 30, 2025 

## Working title

Empirical Analysis of Accuracy–Privacy Trade-offs in Federated Learning for Mobile Movie Recommendation Systems

## Objective

Quantify the trade-offs between recommendation accuracy and privacy protection in mobile federated learning (FL) for movie recommendation. Produce actionable boundaries (privacy budgets, aggregation policies) where model utility remains acceptable for deployment on mobile devices.

## Research questions

1. RQ1 — How does model accuracy (NDCG, Hit Rate) degrade across DP budgets (ε ∈ {∞, 8, 4, 2, 1}) and what thresholds are acceptable (target: ≤5% accuracy loss relative to centralized baseline)?
2. RQ2 — How effective are membership inference and model‑inversion attacks against model updates under those DP budgets (targets: MIA AUC < 0.7, inversion top‑K accuracy < 5%)?
3. RQ3 — How do degrees of data heterogeneity (Dirichlet α ∈ {0.1, 0.5, 1.0}) and client sparsity (local samples ∈ {5,10,20,50}) affect both accuracy and privacy leakage?

## Current status

- Server: FastAPI + AIJack bridge running in Colab; endpoints:
    - `/healthz`, `/init-model`, `/register`
    - `/global-params` (torch blob), `/global-params-json` (portable JSON)
    - `/upload-params`, `/upload-params-json`, `/aggregate`, `/reset`
- Wire format: portable JSON param entries (name, shape, dtype, base64 float32); FP16 packing for transmission implemented.
- Client prototypes:
    - Python simulator (AIJack + PyTorch) for many simulated clients, per‑client DataLoader reuse and weighted FedAvg aggregation implemented.
    - Minimal Flutter app (pure Dart MF) that can fetch JSON params, run local SGD on small models, and upload JSON params.
- Tunneling: Colab → ngrok automated (authenticated) for direct mobile/Postman access to server.
- Verified basic FL loop end‑to‑end: register → pull global → local train → upload → server aggregate (logs show rounds advance and aggregated state returned).

## Methodology

- Data: MovieLens 100K (CSV uploaded to Colab). Preprocessing: map IDs → integer indices; binarize rating (rating ≥ 4 → positive).
- Client partitioning:
    - Non‑IID splits via Dirichlet(α) for α ∈ {0.1, 0.5, 1.0}.
    - Sparse regimes: restrict local samples per client ∈ {5,10,20,50}.
- Models:
    - Primary: Matrix Factorization (MF) and small Neural Collaborative Filtering (NCF) variants.
    - Mobile demo: small MF in Dart; server/experiments: PyTorch models.
- Training:
    - Local SGD; FedAvg weighted by sample counts.
    - DP: DP‑SGD (clipping + Gaussian noise) implemented in simulated clients; RDP accountant to compute ε.
- Privacy evaluation:
    - Membership inference (shadow models + attack classifier) — report AUC.
    - Model inversion — report top‑K reconstruction accuracy.
    - Use AIJack attack modules for standardized evaluation.
- Resource profiling:
    - Per‑round payload (MB), client CPU time, memory, and simulated battery cost per round.
    - Target mobile thresholds: latency < 200 ms per small operation, CPU < 25%, memory < 150MB, bandwidth < 2MB/round (for demo sizes).

## Experimental plan

- DP budgets ε ∈ {∞, 8, 4, 2, 1}
- Heterogeneity α ∈ {0.1, 0.5, 1.0}
- Local samples ∈ {5, 10, 20, 50}
- Model dimension ∈ {8, 16, 32} and model type ∈ {MF, smallNCF}
- Seeds: 3 repeats per cell → compute accuracy, attack metrics, resource metrics
- Outputs: accuracy vs ε plots, attack AUC vs ε plots, Pareto frontiers (accuracy vs privacy vs bandwidth).

## Metrics and thresholds

- Accuracy: NDCG@10, Hit@10, Precision, Recall. Acceptable loss threshold: ≤5% relative to centralized baseline.
- Privacy: MIA AUC (target < 0.7), inversion top‑K accuracy (target < 5%).
- Resources: bandwidth (MB/round), CPU secs per local epoch, peak memory (MB).
- Usability: define operational region where accuracy and resource budgets meet thresholds while privacy targets hold.

## Deliverables

1. Reproducible Colab notebooks (server + simulation + attack evaluation).
2. Server module (FastAPI) with documented endpoints and wire format.
3. Python simulation harness to run full experiment grid and produce figures.
4. Flutter demo app (lib/main.dart) demonstrating mobile interaction for small models.
5. Empirical results: accuracy/privacy curves, Pareto frontiers, and a concise recommendation policy for deployment.
6. Thesis write‑up describing experiments, analysis, and conclusions.

## Limitations

- Full MovieLens‑scale embeddings cannot be downloaded/updated as a whole on mobile devices — experiments will use small model sizes or partial update protocols for mobile trials.
- Flutter/Dart MF is a demo; parity with PyTorch requires PyTorch Mobile (native) for production‑grade experiments.
- Production secure aggregation (Paillier / MPC) is out of scope for full implementation; we will simulate its privacy effects and, where feasible, prototype a simplified secure aggregation flow.

## Reproducibility & artifacts

Provided artifacts (ready):

- Colab notebooks to write server, start uvicorn, create ngrok tunnel, run simulation.
- `aijack_movielens_bridge_opt.py` server file with portable JSON endpoints.
- Flutter `lib/main.dart` for demo client.
- cURL examples and small README.

## Immediate next steps (research work)

- Implement DP‑SGD with RDP accountant in the simulation pipeline and run ε sweeps for MF and small NCF across the heterogeneity grid.
- Integrate AIJack MIA/inversion attack runs per checkpoint and collect attack metrics.
- Produce consolidated figures (accuracy vs ε, attack AUC vs ε, Pareto frontiers) and begin drafting results sections.

## Expected contributions

- Empirical privacy–utility curves for FL recommender systems with reproducible artifacts and a practical mobile prototype demonstrating feasible operating regions and limitations.
- Practical recommendations for small‑model mobile FL deployments (partial updates, compression, DP parameter ranges).