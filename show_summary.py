"""Quick summary of experiment results"""
import json

data = json.load(open('results/dp_inf_alpha_0.5_dim_16_clients_100_seed_42.json'))
rounds = data['rounds']
final = data['final_metrics']
config = data['config']

print('='*60)
print('EXPERIMENT SUMMARY')
print('='*60)
print(f'Total Rounds: {len(rounds)}')
print(f'Total Clients: {config["num_clients"]}')
print(f'Data Heterogeneity (α): {config.get("alpha", "N/A")}')
print(f'\nFinal Metrics:')
print(f'  NDCG@10: {final.get("NDCG@10", 0):.4f}')
print(f'  Hit@10: {final.get("Hit@10", 0):.4f}')
print(f'  Precision@10: {final.get("Precision@10", 0):.4f}')
print(f'  Recall@10: {final.get("Recall@10", 0):.4f}')
print(f'  Accuracy: {final.get("accuracy", 0):.4f}')
print(f'  MSE: {final.get("mse", 0):.4f}')
print(f'  MAE: {final.get("mae", 0):.4f}')

print(f'\nTraining Loss:')
print(f'  Round 1: {rounds[0]["train_loss"]:.4f}')
print(f'  Round 10: {rounds[-1]["train_loss"]:.4f}')
print(f'  Change: {rounds[0]["train_loss"] - rounds[-1]["train_loss"]:.4f}')

print(f'\nClient Participation:')
for i, round_data in enumerate([rounds[0], rounds[4], rounds[-1]], 1):
    agg = round_data['aggregation']
    round_num = round_data['round']
    print(f'  Round {round_num}: {agg.get("num_clients", "N/A")} clients, {agg.get("total_samples", "N/A")} samples')

print('='*60)
print('\nFigures generated in: figures/')
print('  - convergence.png')
print('  - recommendation_metrics.png')
print('  - client_distribution.png')
print('  - aggregation_stats.png')

