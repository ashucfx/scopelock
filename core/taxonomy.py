"""
Formal Capability Taxonomy for ScopeLock.

Defines standard categories, normalized actions, and target API signatures
for Node.js/JavaScript and Python execution runtimes.
"""

from enum import Enum
from typing import Dict, List, Set


class CapabilityCategory(str, Enum):
    """The six primary security-sensitive capability categories."""
    FILESYSTEM = "FILESYSTEM"
    NETWORK = "NETWORK"
    PROCESS = "PROCESS"
    SECRET = "SECRET"
    DATABASE = "DATABASE"
    RUNTIME = "RUNTIME"


class CapabilityAction(str, Enum):
    """Normalized granular capability actions."""
    # Filesystem
    FS_READ = "FS_READ"
    FS_WRITE = "FS_WRITE"
    FS_DELETE = "FS_DELETE"

    # Network
    NET_HTTP_GET = "NET_HTTP_GET"
    NET_HTTP_POST = "NET_HTTP_POST"
    NET_REQUEST = "NET_REQUEST"
    NET_SOCKET = "NET_SOCKET"

    # Process
    PROC_EXEC = "PROC_EXEC"
    PROC_SPAWN = "PROC_SPAWN"

    # Secret
    SECRET_READ_ENV = "SECRET_READ_ENV"
    SECRET_READ_CRED = "SECRET_READ_CRED"

    # Database
    DB_CONNECT = "DB_CONNECT"
    DB_QUERY = "DB_QUERY"

    # Runtime
    RUNTIME_EVAL = "RUNTIME_EVAL"
    RUNTIME_DYNAMIC_IMPORT = "RUNTIME_DYNAMIC_IMPORT"


# Rule mapping API names / patterns to (Category, Action, Default Severity)
JS_SENSITIVE_APIS: Dict[str, tuple[CapabilityCategory, CapabilityAction, str]] = {
    # File System
    "readFile": (CapabilityCategory.FILESYSTEM, CapabilityAction.FS_READ, "HIGH"),
    "readFileSync": (CapabilityCategory.FILESYSTEM, CapabilityAction.FS_READ, "HIGH"),
    "writeFile": (CapabilityCategory.FILESYSTEM, CapabilityAction.FS_WRITE, "HIGH"),
    "writeFileSync": (CapabilityCategory.FILESYSTEM, CapabilityAction.FS_WRITE, "HIGH"),
    "unlink": (CapabilityCategory.FILESYSTEM, CapabilityAction.FS_DELETE, "CRITICAL"),
    "unlinkSync": (CapabilityCategory.FILESYSTEM, CapabilityAction.FS_DELETE, "CRITICAL"),
    "rmdir": (CapabilityCategory.FILESYSTEM, CapabilityAction.FS_DELETE, "CRITICAL"),
    "mkdir": (CapabilityCategory.FILESYSTEM, CapabilityAction.FS_WRITE, "MEDIUM"),

    # Network
    "fetch": (CapabilityCategory.NETWORK, CapabilityAction.NET_REQUEST, "HIGH"),
    "axios.get": (CapabilityCategory.NETWORK, CapabilityAction.NET_HTTP_GET, "HIGH"),
    "axios.post": (CapabilityCategory.NETWORK, CapabilityAction.NET_HTTP_POST, "HIGH"),
    "axios": (CapabilityCategory.NETWORK, CapabilityAction.NET_REQUEST, "HIGH"),
    "http.request": (CapabilityCategory.NETWORK, CapabilityAction.NET_REQUEST, "HIGH"),
    "https.get": (CapabilityCategory.NETWORK, CapabilityAction.NET_HTTP_GET, "HIGH"),
    "https.request": (CapabilityCategory.NETWORK, CapabilityAction.NET_REQUEST, "HIGH"),
    "WebSocket": (CapabilityCategory.NETWORK, CapabilityAction.NET_SOCKET, "CRITICAL"),

    # Process
    "child_process.exec": (CapabilityCategory.PROCESS, CapabilityAction.PROC_EXEC, "CRITICAL"),
    "child_process.execSync": (CapabilityCategory.PROCESS, CapabilityAction.PROC_EXEC, "CRITICAL"),
    "child_process.spawn": (CapabilityCategory.PROCESS, CapabilityAction.PROC_SPAWN, "CRITICAL"),
    "exec": (CapabilityCategory.PROCESS, CapabilityAction.PROC_EXEC, "CRITICAL"),
    "execSync": (CapabilityCategory.PROCESS, CapabilityAction.PROC_EXEC, "CRITICAL"),
    "spawn": (CapabilityCategory.PROCESS, CapabilityAction.PROC_SPAWN, "CRITICAL"),

    # Secrets
    "process.env": (CapabilityCategory.SECRET, CapabilityAction.SECRET_READ_ENV, "HIGH"),

    # Runtime / Dynamic Eval
    "eval": (CapabilityCategory.RUNTIME, CapabilityAction.RUNTIME_EVAL, "CRITICAL"),
    "Function": (CapabilityCategory.RUNTIME, CapabilityAction.RUNTIME_EVAL, "CRITICAL"),
}

PY_SENSITIVE_APIS: Dict[str, tuple[CapabilityCategory, CapabilityAction, str]] = {
    # File System
    "open": (CapabilityCategory.FILESYSTEM, CapabilityAction.FS_READ, "HIGH"),
    "os.remove": (CapabilityCategory.FILESYSTEM, CapabilityAction.FS_DELETE, "CRITICAL"),
    "os.unlink": (CapabilityCategory.FILESYSTEM, CapabilityAction.FS_DELETE, "CRITICAL"),
    "shutil.rmtree": (CapabilityCategory.FILESYSTEM, CapabilityAction.FS_DELETE, "CRITICAL"),

    # Network
    "requests.get": (CapabilityCategory.NETWORK, CapabilityAction.NET_HTTP_GET, "HIGH"),
    "requests.post": (CapabilityCategory.NETWORK, CapabilityAction.NET_HTTP_POST, "HIGH"),
    "urllib.request.urlopen": (CapabilityCategory.NETWORK, CapabilityAction.NET_REQUEST, "HIGH"),
    "httpx.get": (CapabilityCategory.NETWORK, CapabilityAction.NET_HTTP_GET, "HIGH"),
    "socket.socket": (CapabilityCategory.NETWORK, CapabilityAction.NET_SOCKET, "CRITICAL"),

    # Process
    "os.system": (CapabilityCategory.PROCESS, CapabilityAction.PROC_EXEC, "CRITICAL"),
    "os.popen": (CapabilityCategory.PROCESS, CapabilityAction.PROC_EXEC, "CRITICAL"),
    "subprocess.run": (CapabilityCategory.PROCESS, CapabilityAction.PROC_EXEC, "CRITICAL"),
    "subprocess.Popen": (CapabilityCategory.PROCESS, CapabilityAction.PROC_SPAWN, "CRITICAL"),
    "subprocess.call": (CapabilityCategory.PROCESS, CapabilityAction.PROC_EXEC, "CRITICAL"),

    # Secrets
    "os.environ": (CapabilityCategory.SECRET, CapabilityAction.SECRET_READ_ENV, "HIGH"),
    "os.getenv": (CapabilityCategory.SECRET, CapabilityAction.SECRET_READ_ENV, "HIGH"),

    # Runtime
    "eval": (CapabilityCategory.RUNTIME, CapabilityAction.RUNTIME_EVAL, "CRITICAL"),
    "exec": (CapabilityCategory.RUNTIME, CapabilityAction.RUNTIME_EVAL, "CRITICAL"),
    "importlib.import_module": (CapabilityCategory.RUNTIME, CapabilityAction.RUNTIME_DYNAMIC_IMPORT, "HIGH"),
}
