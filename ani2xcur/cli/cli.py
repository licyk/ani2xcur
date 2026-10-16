"""CLI 构建工具"""

import logging
from collections.abc import Callable
from typing import Any

import typer
from typer import _click
from typer.core import TyperCommand, TyperGroup, TyperOption

from ani2xcur.config import LOGGER_NAME


DEBUG_OPTION_HELP = "输出调试日志, 便于排查转换、安装和桌面刷新问题"


def _debug_option_callback(ctx: _click.Context, _param: _click.Parameter, value: bool) -> None:
    """启用调试日志输出。"""
    if value and not ctx.resilient_parsing:
        app_logger = logging.getLogger(LOGGER_NAME)
        app_logger.setLevel(logging.DEBUG)
        app_logger.debug("已启用 debug 日志")


def _make_debug_option() -> TyperOption:
    """创建可挂载到任意命令层级的 debug 选项。"""
    return TyperOption(
        param_decls=["--debug"],
        is_flag=True,
        is_eager=True,
        expose_value=False,
        help=DEBUG_OPTION_HELP,
        callback=_debug_option_callback,
    )


def _has_debug_option(params: list[_click.Parameter] | None) -> bool:
    """检查命令参数中是否已经存在 debug 选项。"""
    return any(isinstance(param, TyperOption) and "--debug" in param.opts for param in params or [])


def _with_debug_option(params: list[_click.Parameter] | None) -> list[_click.Parameter]:
    """为命令参数列表补齐 debug 选项。"""
    normalized_params = list(params or [])
    if _has_debug_option(normalized_params):
        return normalized_params
    return [_make_debug_option(), *normalized_params]


class DebugTyperCommand(TyperCommand):
    """默认带有 --debug 选项的 Typer 命令。"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs["params"] = _with_debug_option(kwargs.get("params"))
        super().__init__(*args, **kwargs)


class AlphabeticalMixedGroup(TyperGroup):
    """
    自定义的命令组
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs["params"] = _with_debug_option(kwargs.get("params"))
        super().__init__(*args, **kwargs)

    def list_commands(
        self,
        ctx: _click.Context,
    ) -> list[str]:  # type: ignore[name-defined]
        """将命令按键名进行字母排序

        Args:
            ctx (_click.Context): click 组件上下文
        Returns:
            list[str]: 排序后的命令名称列表
        """
        return sorted(self.commands.keys())


class DebugOptionTyper(typer.Typer):
    """默认让所有注册命令都带有 --debug 选项的 Typer 应用。"""

    def command(self, *args: Any, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """注册默认带有 debug 选项的命令。

        Args:
            *args (Any): 传递给 Typer command 注册方法的位置参数。
            **kwargs (Any): 传递给 Typer command 注册方法的关键字参数。
        Returns:
            Callable[[Callable[..., Any]], Callable[..., Any]]: 命令装饰器。
        """
        kwargs.setdefault("cls", DebugTyperCommand)
        return super().command(*args, **kwargs)


def typer_factory(
    help: str,  # pylint: disable=redefined-builtin
) -> typer.Typer:
    """生成 typer 装饰器

    Args:
        help (str): 命令的帮助信息
    Returns:
        typer.Typer: typer 装饰器
    """
    return DebugOptionTyper(
        help=help,
        add_completion=True,  # 启用自动补全功能
        no_args_is_help=True,  # 不带参数运行时显示帮助信息
        cls=AlphabeticalMixedGroup,  # 使用自定义的分组类
        rich_markup_mode=None,  # 禁用 rich 标记模式
        rich_help_panel=None,  # 禁用 rich 帮助面板
        pretty_exceptions_enable=False,  # 禁用美化异常显示
    )
