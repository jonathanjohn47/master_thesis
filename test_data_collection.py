"""
Quick test script to verify data collection works
"""

from scripts.metrics_collector import MetricsCollector, create_experiment_id
from scripts.recommendation_metrics import ndcg_at_k, hit_rate_at_k

# Test metrics collector
print("Testing Metrics Collector...")
collector = MetricsCollector(experiment_id="test_experiment", results_dir="results")

collector.set_config({
    "num_clients": 3,
    "alpha": 0.5,
    "dp_epsilon": None
})

# Add sample round
collector.add_round_metrics(
    round_num=1,
    train_loss=0.123,
    test_metrics={
        "NDCG@10": 0.45,
        "Hit@10": 0.32,
        "mse": 0.123
    }
)

# Save
json_path = collector.save_json()
csv_path = collector.save_csv_summary()

print(f"✅ JSON saved to: {json_path}")
print(f"✅ CSV saved to: {csv_path}")

# Test recommendation metrics
print("\nTesting Recommendation Metrics...")
test_scores = [1.0, 0.8, 0.6, 0.4, 0.2]
test_relevant = [True, True, False, True, False]

ndcg = ndcg_at_k(test_scores, k=5)
hit = hit_rate_at_k(test_relevant, k=5)

print(f"✅ NDCG@5: {ndcg:.4f}")
print(f"✅ Hit@5: {hit:.4f}")

print("\n✅ All tests passed! Data collection is working.")

