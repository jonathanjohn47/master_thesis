import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            'Start FL server, initialize model, and run Flutter screenshot drive test.'
        )
    )
    parser.add_argument('--port', type=int, default=8000, help='Server port (default: 8000)')
    parser.add_argument(
        '--flutter-device',
        default=None,
        help='Optional flutter device id/name passed to "flutter drive -d"',
    )
    parser.add_argument(
        '--test-server-url',
        default=None,
        help='URL passed to Flutter test via FL_TEST_SERVER_URL',
    )
    parser.add_argument(
        '--server-start-timeout',
        type=int,
        default=45,
        help='Seconds to wait for /healthz',
    )
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parent


def wait_for_server(base_url: str, timeout_seconds: int) -> bool:
    deadline = time.time() + timeout_seconds
    health_url = f'{base_url}/healthz'
    while time.time() < deadline:
        try:
            with urlopen(health_url, timeout=3) as response:  # nosec B310
                if response.status == 200:
                    return True
        except (URLError, TimeoutError):
            pass
        time.sleep(1)
    return False


def run_command(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> int:
    process = subprocess.run(command, cwd=str(cwd), env=env, check=False)
    return process.returncode


def terminate_process(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return

    process.terminate()
    try:
        process.wait(timeout=10)
        return
    except subprocess.TimeoutExpired:
        pass

    process.kill()
    process.wait(timeout=5)


def main() -> int:
    args = parse_args()
    root = repo_root()
    mobile_dir = root / 'federated_learning_in_mobile'

    base_url = f'http://127.0.0.1:{args.port}'
    test_server_url = args.test_server_url or f'http://10.0.2.2:{args.port}'

    server_env = os.environ.copy()
    server_env['FL_SERVER_PORT'] = str(args.port)
    # Avoid OpenMP duplicate runtime abort seen on some macOS Python setups.
    server_env.setdefault('KMP_DUPLICATE_LIB_OK', 'TRUE')

    print(f'[1/4] Starting server on port {args.port}...')
    server_process = subprocess.Popen(
        [sys.executable, '-u', 'server.py'],
        cwd=str(root),
        env=server_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    try:
        if not wait_for_server(base_url, args.server_start_timeout):
            print('Server did not become healthy in time.')
            if server_process.stdout is not None:
                try:
                    output = server_process.stdout.read().decode('utf-8', errors='replace')
                    if output.strip():
                        print('--- server output ---')
                        print(output)
                except Exception:
                    pass
            return 1

        print('[2/4] Initializing server model via init_server_model.py...')
        init_env = os.environ.copy()
        init_env['FL_SERVER_URL'] = base_url
        init_exit = run_command(
            [sys.executable, 'init_server_model.py'],
            cwd=root,
            env=init_env,
        )
        if init_exit != 0:
            print('Model initialization failed.')
            return init_exit

        print('[3/4] Running flutter drive screenshot test...')
        flutter_command = [
            'flutter',
            'drive',
            '--driver=test_driver/screenshot_test_driver.dart',
            '--target=integration_test/screenshot_test.dart',
            f'--dart-define=FL_TEST_SERVER_URL={test_server_url}',
        ]
        if args.flutter_device:
            flutter_command.extend(['-d', args.flutter_device])

        drive_exit = run_command(flutter_command, cwd=mobile_dir)

        print('[4/4] Cleaning up server process...')
        return drive_exit
    finally:
        terminate_process(server_process)


if __name__ == '__main__':
    raise SystemExit(main())

