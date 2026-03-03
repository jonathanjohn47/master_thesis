"""
Quick Demo Script for Live Presentation

This script provides an interactive menu for demonstrating your thesis work.
Run this during presentations for a professional, guided demo.

Usage: python presentation_demo.py
"""

import os
import sys
import subprocess
import time
from pathlib import Path


def print_banner(text):
    """Print a formatted banner."""
    width = 70
    print("\n" + "=" * width)
    print(text.center(width))
    print("=" * width + "\n")


def print_section(text):
    """Print a section header."""
    print("\n" + "-" * 70)
    print(f"  {text}")
    print("-" * 70 + "\n")


def run_verification():
    """Run the verification script."""
    print_section("DEMO 1: Verifying Stored Results")
    print("This verifies that all 24 experiment configurations match")
    print("our published results exactly.\n")

    input("Press ENTER to run verification... ")

    subprocess.run([sys.executable, "verify_results.py"])

    input("\nPress ENTER to continue... ")


def run_single_experiment():
    """Run a single experiment."""
    print_section("DEMO 2: Running Live Experiment")
    print("This runs a complete federated learning experiment from scratch.")
    print("Configuration: 100 clients, 10 rounds, no DP, α=0.5")
    print("Expected duration: ~35 seconds\n")

    input("Press ENTER to start experiment... ")

    start = time.time()
    subprocess.run([sys.executable, "run_single_experiment.py"])
    elapsed = time.time() - start

    print(f"\n✅ Experiment completed in {elapsed:.1f} seconds")
    input("\nPress ENTER to continue... ")


def show_figures():
    """Open the figures directory."""
    print_section("DEMO 3: Visualization Gallery")
    print("Opening figures directory with all publication-ready visualizations:")
    print("  • accuracy_vs_epsilon.png - Privacy-accuracy tradeoff")
    print("  • accuracy_loss_vs_epsilon.png - Quantified accuracy loss")
    print("  • attack_evaluation.png - Privacy attack results")
    print("  • accuracy_vs_alpha.png - Data heterogeneity impact")
    print("  • convergence.png - Training dynamics")
    print("  • And more...\n")

    input("Press ENTER to open figures folder... ")

    figures_path = Path("figures")
    if figures_path.exists():
        if sys.platform == "win32":
            os.startfile(figures_path)
        elif sys.platform == "darwin":
            subprocess.run(["open", str(figures_path)])
        else:
            subprocess.run(["xdg-open", str(figures_path)])
        print("✅ Figures folder opened")
    else:
        print("⚠️  Figures folder not found")

    input("\nPress ENTER to continue... ")


def show_results_summary():
    """Display key results summary."""
    print_section("DEMO 4: Results Summary")

    print("KEY FINDINGS\n")

    print("📊 RQ1: Privacy-Accuracy Tradeoff")
    print("-" * 50)
    print("DP Budget (ε)  | NDCG@10       | Accuracy Loss")
    print("-" * 50)
    print("∞ (No DP)      | 0.0539±0.0108 | Baseline")
    print("8              | 0.0534±0.0131 | ~1%")
    print("4              | 0.0479±0.0091 | ~11%")
    print("2              | 0.0456±0.0095 | ~15%")
    print("1              | 0.0467±0.0121 | ~13%")

    print("\n🔒 RQ2: Privacy Attack Effectiveness")
    print("-" * 50)
    print("DP Budget (ε)  | MIA AUC | Status")
    print("-" * 50)
    print("∞ (No DP)      | 0.5481  | Vulnerable")
    print("8              | 0.5335  | Reduced")
    print("4              | 0.5025  | Protected")
    print("2              | 0.5004  | Protected")
    print("1              | 0.4858  | Protected")
    print("\nModel Inversion: 0.000 (completely ineffective)")

    print("\n📈 RQ3: Data Heterogeneity")
    print("-" * 50)
    print("Alpha | NDCG@10       | Status")
    print("-" * 50)
    print("0.1   | 0.0538±0.0108 | Robust")
    print("0.5   | 0.0539±0.0108 | Robust")
    print("1.0   | 0.0539±0.0108 | Robust")

    print("\n🎯 Major Finding: Federated-Centralized Gap")
    print("-" * 50)
    print("Centralized:  NDCG@10 = 0.2250")
    print("Federated:    NDCG@10 = 0.0539")
    print("Gap:          76% accuracy reduction")
    print("\nCauses: Data fragmentation, limited communication,")
    print("        sparse collaborative filtering data")

    input("\nPress ENTER to continue... ")


def show_code_structure():
    """Show the code structure."""
    print_section("DEMO 5: Code Structure")

    print("MAIN EXPERIMENT FILES:")
    print("-" * 50)

    files = [
        ("run_complete_experiment.py", "Main experiment runner (24 configs)"),
        ("run_single_experiment.py", "Single experiment demo"),
        ("verify_results.py", "Results verification"),
        ("centralized_baseline.py", "Centralized baseline training"),
    ]

    for filename, description in files:
        path = Path(filename)
        if path.exists():
            size = path.stat().st_size
            print(f"✅ {filename:<30} - {description}")
            print(f"   {size:>7,} bytes")
        else:
            print(f"⚠️  {filename:<30} - Not found")

    print("\nKEY MODULES:")
    print("-" * 50)

    modules = [
        ("scripts/recommendation_metrics.py", "NDCG, Hit@K evaluation"),
        ("scripts/rdp_accountant.py", "Privacy budget calculation"),
        ("scripts/attack_evaluation.py", "MIA and inversion attacks"),
    ]

    for filename, description in modules:
        path = Path(filename)
        if path.exists():
            print(f"✅ {filename:<35} - {description}")
        else:
            print(f"⚠️  {filename:<35} - Not found")

    print("\nRESULTS:")
    print("-" * 50)
    results_path = Path("results")
    if results_path.exists():
        json_files = list(results_path.glob("*.json"))
        csv_files = list(results_path.glob("*.csv"))
        print(f"✅ {len(json_files)} JSON result files")
        print(f"✅ {len(csv_files)} CSV summary files")

    print("\nFIGURES:")
    print("-" * 50)
    figures_path = Path("figures")
    if figures_path.exists():
        png_files = list(figures_path.glob("*.png"))
        csv_files = list(figures_path.glob("*.csv"))
        print(f"✅ {len(png_files)} PNG visualizations")
        print(f"✅ {len(csv_files)} CSV tables")

    input("\nPress ENTER to continue... ")


def full_demo():
    """Run the complete demo sequence."""
    print_banner("FULL DEMO SEQUENCE")
    print("This will run all demos in sequence:")
    print("  1. Verify stored results")
    print("  2. Run live experiment")
    print("  3. Show visualizations")
    print("  4. Display results summary")
    print("  5. Show code structure")

    input("\nPress ENTER to start, or Ctrl+C to cancel... ")

    run_verification()
    run_single_experiment()
    show_figures()
    show_results_summary()
    show_code_structure()

    print_banner("DEMO COMPLETE")
    print("All demonstrations completed successfully! ✅")


def quick_demo():
    """Run a quick 2-minute demo."""
    print_banner("QUICK DEMO (2 Minutes)")
    print("This runs a minimal demo showing reproducibility.\n")

    input("Press ENTER to start... ")

    # Quick verification
    print_section("Quick Verification")
    subprocess.run([sys.executable, "verify_results.py"])

    # Show one figure
    print_section("Sample Visualization")
    fig_path = Path("figures/accuracy_vs_epsilon.png")
    if fig_path.exists():
        if sys.platform == "win32":
            os.startfile(fig_path)
        print("✅ Opened accuracy vs epsilon figure")

    print_banner("QUICK DEMO COMPLETE")


def main():
    """Main menu."""
    while True:
        print_banner("THESIS PRESENTATION DEMO")
        print("Privacy-Preserving Federated Learning for Mobile Recommendations\n")

        print("Choose a demonstration:\n")
        print("  [1] Verify Stored Results (~30 seconds)")
        print("  [2] Run Live Experiment (~35 seconds)")
        print("  [3] Show Visualizations (instant)")
        print("  [4] Display Results Summary (instant)")
        print("  [5] Show Code Structure (instant)")
        print()
        print("  [F] Full Demo Sequence (~5 minutes)")
        print("  [Q] Quick Demo (~2 minutes)")
        print()
        print("  [X] Exit")
        print()

        choice = input("Enter your choice: ").strip().upper()

        try:
            if choice == "1":
                run_verification()
            elif choice == "2":
                run_single_experiment()
            elif choice == "3":
                show_figures()
            elif choice == "4":
                show_results_summary()
            elif choice == "5":
                show_code_structure()
            elif choice == "F":
                full_demo()
            elif choice == "Q":
                quick_demo()
            elif choice == "X":
                print("\n👋 Thank you for viewing the demo!")
                break
            else:
                print("\n⚠️  Invalid choice. Please try again.")
                input("Press ENTER to continue... ")
        except KeyboardInterrupt:
            print("\n\n⚠️  Demo interrupted. Returning to menu...")
            input("Press ENTER to continue... ")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            input("Press ENTER to continue... ")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo terminated. Goodbye!")

