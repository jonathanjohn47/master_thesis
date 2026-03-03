"""
Mobile Experiment Setup & Run Guide

This script helps you:
1. Check your Android emulator status
2. Build and run the Flutter app
3. Configure server connection
4. Run experiments on mobile

Prerequisites:
- Android emulator running
- Flutter installed
- Python server running
"""

import subprocess
import sys
import os
import time
import json
from pathlib import Path


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_section(text):
    """Print formatted section."""
    print("\n" + "-" * 70)
    print(f"  {text}")
    print("-" * 70 + "\n")


def check_flutter():
    """Check if Flutter is installed."""
    print_section("Checking Flutter Installation")

    try:
        result = subprocess.run(["flutter", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Flutter found:")
            print(result.stdout.strip())
            return True
        else:
            print("❌ Flutter not found")
            return False
    except FileNotFoundError:
        print("❌ Flutter not installed")
        return False


def check_devices():
    """Check connected devices and emulators."""
    print_section("Checking Connected Devices")

    try:
        result = subprocess.run(["flutter", "devices"], capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout.strip())
            if "emulator" in result.stdout.lower() or "device" in result.stdout.lower():
                print("\n✅ Device/Emulator found!")
                return True
            else:
                print("\n❌ No devices/emulators detected")
                print("Please start an Android emulator or connect a device")
                return False
        else:
            print("❌ Could not check devices")
            return False
    except FileNotFoundError:
        print("❌ Flutter not found")
        return False


def check_server():
    """Check if server is running."""
    print_section("Checking Server Status")

    import socket

    def is_port_open(host, port, timeout=2):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        try:
            result = sock.connect_ex((host, port))
            return result == 0
        finally:
            sock.close()

    # Check localhost
    if is_port_open("127.0.0.1", 8000):
        print("✅ Server running on localhost:8000")
        return "localhost"

    # Check local network IP
    try:
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        if is_port_open(local_ip, 8000):
            print(f"✅ Server running on {local_ip}:8000")
            return local_ip
    except:
        pass

    print("❌ Server not detected on localhost:8000")
    print("\nTo start server, run in another terminal:")
    print("  cd C:\\Users\\jonat\\OneDrive\\Documents\\GitHub\\master_thesis")
    print("  python server.py")
    return None


def get_your_ip():
    """Get your PC's local IP address."""
    print_section("Getting Your PC's IP Address")

    try:
        # Windows
        result = subprocess.run(["ipconfig"], capture_output=True, text=True)
        lines = result.stdout.split('\n')

        for i, line in enumerate(lines):
            if "IPv4 Address" in line:
                ip = line.split(":")[-1].strip()
                if ip and not ip.startswith("127."):
                    print(f"✅ Your PC's IP: {ip}")
                    return ip
    except:
        pass

    print("❌ Could not determine IP address")
    print("Try: ipconfig")
    return "192.168.1.100"  # Default suggestion


def build_flutter_app():
    """Build the Flutter app."""
    print_section("Building Flutter App")

    app_dir = Path("C:/Users/jonat/OneDrive/Documents/GitHub/master_thesis/federated_learning_in_mobile")

    if not app_dir.exists():
        print(f"❌ App directory not found: {app_dir}")
        return False

    print(f"Building from: {app_dir}")
    print("\nThis may take a few minutes...")

    try:
        result = subprocess.run(
            ["flutter", "pub", "get"],
            cwd=str(app_dir),
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            print("✅ Dependencies installed")
            return True
        else:
            print(f"❌ Build failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Build timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def run_flutter_app():
    """Run the Flutter app on emulator."""
    print_section("Running Flutter App on Emulator")

    app_dir = Path("C:/Users/jonat/OneDrive/Documents/GitHub/master_thesis/federated_learning_in_mobile")

    print("Starting app on emulator...")
    print("This will take a minute or two...")

    try:
        subprocess.Popen(
            ["flutter", "run"],
            cwd=str(app_dir),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("✅ App launched!")
        print("\nWaiting for app to load...")
        time.sleep(5)
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def get_config_instructions(server_ip):
    """Get configuration instructions for the app."""
    print_section("Configure App for Server Connection")

    print(f"""
Your Server Configuration:

📍 Server Address: http://{server_ip}:8000
📱 Client ID: android_emulator_1

Steps to Configure in App:
1. Wait for app to load on emulator
2. In the app, you'll see a "Settings" or "Configuration" section
3. Enter Server URL: http://{server_ip}:8000
4. Enter Client ID: android_emulator_1
5. Click "Connect to Server"
6. Wait for "Connected" status

Or check the app logs for the exact server URL to use.
    """)


def show_training_instructions():
    """Show training instructions."""
    print_section("Running Training Experiment")

    print("""
Once the app is connected to the server:

1. Click "Run Training Round" button in the app
2. Watch the logs for training progress
3. Results will be displayed in the app
4. Metrics will be uploaded to the server

The app shows:
- Training loss
- Recommendation metrics (NDCG@10, Hit@10)
- Battery status
- Network information
    """)


def main():
    """Main execution."""
    print_header("🚀 Mobile Experiment Setup")

    print("""
This guide will help you run the federated learning app
on your Android emulator and connect it to the server.
    """)

    # Step 1: Check Flutter
    if not check_flutter():
        print("\n⚠️  Flutter not found. Please install Flutter from https://flutter.dev")
        return False

    # Step 2: Check devices
    if not check_devices():
        print("\n⚠️  No emulator/device found. Please start Android emulator first.")
        return False

    # Step 3: Check server
    server_running = check_server()
    if not server_running:
        print("\n⚠️  Server not running. Start it with: python server.py")
        print("Continue anyway? (Y/n)")
        if input().lower() == 'n':
            return False
        server_running = "localhost"

    # Step 4: Get IP
    your_ip = get_your_ip()

    # Step 5: Build app
    print_section("Ready to Build & Run")
    print("Building Flutter app...")

    if not build_flutter_app():
        print("\n❌ Build failed")
        return False

    # Step 6: Run app
    print("\nLaunching app on emulator...")
    if not run_flutter_app():
        print("\n❌ Failed to launch app")
        return False

    # Step 7: Configuration
    get_config_instructions(your_ip if your_ip != "192.168.1.100" else server_running)

    # Step 8: Training
    show_training_instructions()

    print_header("✅ Setup Complete!")

    print("""
Next Steps:
1. Configure the app with the server URL (see above)
2. Click "Connect to Server"
3. Click "Run Training Round"
4. Monitor progress in app logs
5. Results will be uploaded to the server

Troubleshooting:
- If can't connect: Check firewall, server is running
- If app crashes: Check emulator has enough RAM/disk
- If slow: Try reducing BATCH_SIZE in model settings

Good luck! 🎉
    """)

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

