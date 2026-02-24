import docker
from PySide6.QtCore import QThread, Signal


def get_docker_client():
    try:
        client = docker.from_env()
        client.ping()
        return client
    except docker.errors.DockerException:
        return None


def check_docker():
    try:
        client = docker.from_env()
        client.ping()
        version = client.version().get("Version", "?")
        return True, version
    except docker.errors.DockerException as e:
        return False, str(e)


def check_image(client, tag):
    try:
        client.images.get(tag)
        return True
    except docker.errors.ImageNotFound:
        return False


class DockerWorker(QThread):
    log_line = Signal(str)
    finished = Signal(int)
    error = Signal(str)

    def __init__(self, client, image, cmd, volumes=None, environment=None):
        super().__init__()
        self.client = client
        self.image = image
        self.cmd = cmd
        self.volumes = volumes
        self.environment = environment
        self.container = None

    def run(self):
        try:
            self.container = self.client.containers.run(
                self.image, self.cmd,
                volumes=self.volumes,
                environment=self.environment,
                detach=True,
            )
            for chunk in self.container.logs(stream=True):
                line = chunk.decode().rstrip()
                if line:
                    self.log_line.emit(line)
            result = self.container.wait()
            self.container.remove()
            self.container = None
            self.finished.emit(result["StatusCode"])
        except docker.errors.DockerException as e:
            self.error.emit(str(e))

    def stop_container(self):
        if self.container:
            try:
                self.container.kill()
            except docker.errors.DockerException:
                pass


class PullWorker(QThread):
    progress = Signal(str)
    finished = Signal(bool)

    def __init__(self, client, tag):
        super().__init__()
        self.client = client
        self.tag = tag

    def run(self):
        try:
            if ":" in self.tag:
                repo, tag = self.tag.rsplit(":", 1)
            else:
                repo, tag = self.tag, "latest"
            for chunk in self.client.api.pull(repo, tag=tag, stream=True, decode=True):
                status = chunk.get("status", "")
                prog = chunk.get("progress", "")
                if prog:
                    self.progress.emit(f"{status} {prog}")
                elif status:
                    self.progress.emit(status)
            self.finished.emit(True)
        except docker.errors.DockerException as e:
            self.progress.emit(f"ERROR: {e}")
            self.finished.emit(False)


def diagnose_docker_error(error_msg):
    """Add user-friendly context to Docker error messages."""
    low = error_msg.lower()
    if "no space left" in low:
        return f"{error_msg}\n  -> Disk full. Run 'docker system prune' to free space."
    if "timeout" in low or "timed out" in low:
        return f"{error_msg}\n  -> Docker daemon may be overloaded or unresponsive."
    if "connection refused" in low or "not running" in low:
        return f"{error_msg}\n  -> Is Docker Desktop running?"
    if "permission denied" in low:
        return f"{error_msg}\n  -> Check Docker permissions."
    return error_msg
