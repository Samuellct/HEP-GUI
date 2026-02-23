# T00_2_docker_basics.py -- test docker-py connection

import time
import docker
import config

print("--- T00_2: docker-py basics ---\n")

# -- test 1: daemon connection --

try:
    client = docker.from_env()
    info = client.info()
    server_ver = info.get("ServerVersion", "?")
    print(f"  OK  docker.from_env() -- server v{server_ver}")
except Exception as e:
    print(f"  FAIL docker.from_env(): {e}")
    raise SystemExit(1)

# -- test 2: hello-world --

try:
    output = client.containers.run("hello-world", remove=True)
    text = output.decode() if isinstance(output, bytes) else output
    if "Hello from Docker" in text:
        print("  OK  hello-world container ran")
    else:
        print("  FAIL hello-world: unexpected output")
except Exception as e:
    print(f"  FAIL hello-world: {e}")

# -- test 3: volume mount --

try:
    volumes = {str(config.DATA_DIR): {"bind": "/data", "mode": "rw"}}
    cmd = f'{config.DOCKER_SHELL} "ls /data"'
    container = client.containers.run(
        config.DOCKER_IMAGE, cmd, volumes=volumes, detach=True,
    )
    result = container.wait()
    logs = container.logs().decode()
    container.remove()

    entries = logs.split()
    if "models" in entries and "scripts" in entries:
        print(f"  OK  volume mount -- ls /data: {' '.join(entries)}")
    else:
        print(f"  FAIL volume mount -- expected models+scripts, got: {logs.strip()}")
except Exception as e:
    print(f"  FAIL volume mount: {e}")

# -- test 4: streaming logs --

try:
    loop_cmd = 'for i in 1 2 3 4 5; do echo line_$i; sleep 0.3; done'
    cmd = f'{config.DOCKER_SHELL} "{loop_cmd}"'
    container = client.containers.run(
        config.DOCKER_IMAGE, cmd, detach=True,
    )

    t0 = time.time()
    lines = []
    for chunk in container.logs(stream=True):
        dt = time.time() - t0
        line = chunk.decode().rstrip()
        if line:
            lines.append((dt, line))

    container.wait()
    container.remove()

    span = lines[-1][0] - lines[0][0] if len(lines) > 1 else 0.0
    print(f"  OK  streaming -- {len(lines)} lines over {span:.1f}s")
    for dt, line in lines:
        print(f"       +{dt:.2f}s  {line}")
except Exception as e:
    print(f"  FAIL streaming: {e}")

print("\ndone.")
