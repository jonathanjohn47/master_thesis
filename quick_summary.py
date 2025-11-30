"""Quick summary of all your experiment results"""
import json
import glob

print('='*70)
print('COMPLETE EXPERIMENT SUMMARY')
print('='*70)

# Python results
python_files = glob.glob("results/*.json")
print(f'\n📊 PYTHON SIMULATED CLIENTS:')
print(f'   Found {len(python_files)} experiment(s)')
for f in python_files:
    data = json.load(open(f))
    config = data['config']
    rounds = data['rounds']
    final = data['final_metrics']
    print(f'\n   File: {f.split("/")[-1]}')
    print(f'   • Clients: {config["num_clients"]}')
    print(f'   • Rounds: {len(rounds)}')
    print(f'   • Final Accuracy: {final.get("accuracy", 0):.4f}')
    print(f'   • Final Hit@10: {final.get("Hit@10", 0):.4f}')
    print(f'   • Final MSE: {final.get("mse", 0):.4f}')

# Android results
android_files = glob.glob("mobile_results/*.json")
print(f'\n📱 ANDROID DEVICES:')
print(f'   Found {len(android_files)} device result(s)')
for f in android_files:
    data = json.load(open(f))
    config = data['config']
    rounds = data['rounds']
    device_id = config.get('device_id', 'unknown')
    print(f'\n   Device: {device_id}')
    print(f'   • Client ID: {config.get("client_id", "N/A")}')
    print(f'   • Rounds: {len(rounds)}')
    if rounds:
        last_round = rounds[-1]
        test_metrics = last_round.get('test_metrics', {})
        resource_metrics = last_round.get('resource_metrics', {})
        print(f'   • Final Accuracy: {test_metrics.get("accuracy", 0):.4f}')
        print(f'   • Battery Drain: {resource_metrics.get("battery_drain", 0):.2f}%')
        print(f'   • Training Time: {resource_metrics.get("training_time_ms", 0)} ms')

print(f'\n📈 FIGURES GENERATED:')
import os
figure_files = [f for f in os.listdir('figures') if f.endswith('.png')]
print(f'   Found {len(figure_files)} figure(s) in figures/')
for fig in sorted(figure_files):
    print(f'   • {fig}')

print('\n' + '='*70)
print('NEXT STEPS:')
print('='*70)
print('1. Review all figures in the figures/ folder')
print('2. Read BEGINNER_GUIDE_TO_THESIS.md for detailed guidance')
print('3. Start writing your Results section using the templates provided')
print('4. Extract numbers from the JSON/CSV files for your tables')
print('='*70)

