"""Shell 命令执行器

不同平台下 subprocess 的执行结果不一致, 以下为不同平台的测试结果:
```
        测试平台: linux
        用例 1: {'cmd': ['/usr/bin/git', '--version'], 'shell': False} -> 成功
        用例 2: {'cmd': ['/usr/bin/git', '--version'], 'shell': True} -> 失败
        用例 3: {'cmd': '"/usr/bin/git" --version', 'shell': False} -> 失败
        用例 4: {'cmd': '"/usr/bin/git" --version', 'shell': True} -> 成功
        用例 5: {'cmd': ['/usr/bin/git', '--version'], 'shell': False} -> 成功
        用例 6: {'cmd': ['/usr/bin/git', '--version'], 'shell': True} -> 失败
        用例 7: {'cmd': '"/usr/bin/git" --version', 'shell': False} -> 失败
        用例 8: {'cmd': '"/usr/bin/git" --version', 'shell': True} -> 成功

        测试平台: win32
        用例 1: {'cmd': ['C:\\Program Files\\Git\\mingw64\\bin\\git.EXE', '--version'], 'shell': False} -> 成功
        用例 2: {'cmd': ['C:\\Program Files\\Git\\mingw64\\bin\\git.EXE', '--version'], 'shell': True} -> 成功
        用例 3: {'cmd': '"C:\\Program Files\\Git\\mingw64\\bin\\git.EXE" --version', 'shell': False} -> 成功
        用例 4: {'cmd': '"C:\\Program Files\\Git\\mingw64\\bin\\git.EXE" --version', 'shell': True} -> 成功
        用例 5: {'cmd': ['C:/Program Files/Git/mingw64/bin/git.EXE', '--version'], 'shell': False} -> 成功
        用例 6: {'cmd': ['C:/Program Files/Git/mingw64/bin/git.EXE', '--version'], 'shell': True} -> 成功
        用例 7: {'cmd': '"C:/Program Files/Git/mingw64/bin/git.EXE" --version', 'shell': False} -> 成功
        用例 8: {'cmd': '"C:/Program Files/Git/mingw64/bin/git.EXE" --version', 'shell': True} -> 成功

        测试平台: darwin
        用例 1: {'cmd': ['/opt/homebrew/bin/git', '--version'], 'shell': False} -> 成功
        用例 2: {'cmd': ['/opt/homebrew/bin/git', '--version'], 'shell': True} -> 失败
        用例 3: {'cmd': '"/opt/homebrew/bin/git" --version', 'shell': False} -> 失败
        用例 4: {'cmd': '"/opt/homebrew/bin/git" --version', 'shell': True} -> 成功
        用例 5: {'cmd': ['/opt/homebrew/bin/git', '--version'], 'shell': False} -> 成功
        用例 6: {'cmd': ['/opt/homebrew/bin/git', '--version'], 'shell': True} -> 失败
        用例 7: {'cmd': '"/opt/homebrew/bin/git" --version', 'shell': False} -> 失败
        用例 8: {'cmd': '"/opt/homebrew/bin/git" --version', 'shell': True} -> 成功
```

- 对于 Linux 平台, 当使用 Shell=True 时, 应使用字符串命令; Shell=False 时, 使用列表命令
- 对于 Windows 平台, 当使用 Shell=True / Shell=False 时, 使用字符串命令和列表命令都可行
- 对于 MacOS 平台, 当使用 Shell=True 时, 应使用字符串命令; Shell=False 时, 使用列表命令 (行为和 Linux 中的一致)
"""

import os
import sys
import shlex
import subprocess
from pathlib import Path
from typing import Any

from ani2xcur.logger import get_logger
from ani2xcur.config import (
    LOGGER_COLOR,
    LOGGER_LEVEL,
    LOGGER_NAME,
)


logger = get_logger(
    name=LOGGER_NAME,
    level=LOGGER_LEVEL,
    color=LOGGER_COLOR,
)

DEBUG_ENV_KEYS = (
    "DISPLAY",
    "WAYLAND_DISPLAY",
    "XDG_SESSION_TYPE",
    "XCURSOR_THEME",
    "XCURSOR_SIZE",
)
"""命令调试日志中允许展示的环境变量键。"""


def preprocess_command(
    command: list[str] | str,
    shell: bool,
) -> list[str] | str:
    """针对不同平台对命令进行预处理

    Args:
        command (list[str] | str): 原始命令
        shell (bool): 是否调用 Shell
    Returns:
        (list[str] | str): 处理后的命令
    """
    if sys.platform == "win32":
        # Windows 平台
        # 字符串命令和列表命令都可行
        return command
    else:
        # Linux / macOS 平台
        if shell:
            # 使用字符串命令
            if isinstance(command, list):
                return shlex.join(command)
            return command
        # 使用列表命令
        if isinstance(command, str):
            return shlex.split(command)
        return command


def _debug_env_summary(
    env: dict[str, str],
) -> dict[str, str]:
    """提取命令调试日志中允许展示的环境变量。

    Args:
        env (dict[str, str]): 进程环境变量。
    Returns:
        dict[str, str]: 允许写入日志的环境变量摘要。
    """
    return {key: env[key] for key in DEBUG_ENV_KEYS if key in env}


def _debug_text_summary(
    text: str | None,
    limit: int = 500,
) -> str | None:
    """生成命令输出的短摘要。

    Args:
        text (str | None): 命令输出内容。
        limit (int): 最大保留长度。
    Returns:
        str | None: 输出摘要。
    """
    if text is None:
        return None

    text = text.strip()
    if len(text) <= limit:
        return text
    return f"{text[:limit]}...<已截断 {len(text) - limit} 个字符>"


def run_cmd(
    command: str | list[str],
    custom_env: dict[str, str] | None = None,
    live: bool | None = True,
    shell: bool | None = None,
    cwd: Path | None = None,
    check: bool | None = True,
) -> str | None:
    """执行 Shell 命令

    Args:
        command (str | list[str]): 要执行的命令
        custom_env (dict[str, str] | None): 自定义环境变量
        live (bool | None): 是否实时输出命令执行日志
        shell (bool | None): 是否使用内置 Shell 执行命令
        cwd (Path | None): 执行进程时的起始路径
        check (bool | None): 是否检查进程退出状态
    Returns:
        str | None: 命令输出内容, 当 live=True 或执行失败时可能返回 None
    Raises:
        RuntimeError: 命令执行失败且 check=True 时
    """

    if shell is None:
        shell = sys.platform != "win32"

    if custom_env is None:
        custom_env = os.environ.copy()

    command_to_exec = preprocess_command(command=command, shell=shell)

    kwargs: dict[str, Any] = {
        "args": command_to_exec,
        "shell": shell,
        "env": custom_env,
        "cwd": cwd,
        "encoding": "utf-8",
        "errors": "ignore",
    }

    if not live:
        kwargs["stdout"] = kwargs["stderr"] = subprocess.PIPE

    logger.debug(
        "执行命令: command=%s, cwd=%s, shell=%s, live=%s, check=%s, env=%s",
        command_to_exec,
        cwd,
        shell,
        live,
        check,
        _debug_env_summary(custom_env),
    )

    result: subprocess.CompletedProcess[str] = subprocess.run(**kwargs)  # pylint: disable=subprocess-run-check
    logger.debug(
        "命令执行完成: returncode=%s, stdout=%r, stderr=%r",
        result.returncode,
        _debug_text_summary(result.stdout),
        _debug_text_summary(result.stderr),
    )

    if check and result.returncode != 0:
        errors = [
            "执行命令时发生错误",
            f"命令: {command_to_exec}",
            f"错误代码: {result.returncode}",
        ]
        if result.stdout:
            errors.append(f"标准输出: {result.stdout}")
        if result.stderr:
            errors.append(f"错误输出: {result.stderr}")

        raise RuntimeError("\n".join(errors))

    return result.stdout
