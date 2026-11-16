import importlib
import pkgutil

import typer

app = typer.Typer(help="EduRAG CLI", no_args_is_help=True)


@app.callback()
def _root():
    """EduRAG CLI"""
    pass


def _discover_commands():
    """扫描 commands 目录，加载含 register(app) 的模块。"""
    import commands as commands_pkg

    for info in pkgutil.iter_modules(commands_pkg.__path__):
        if info.name.startswith("_"):
            continue

        try:
            module = importlib.import_module(f"commands.{info.name}")
        except ImportError as e:
            print(f"[cli] 跳过 commands.{info.name}: {e}")
            continue

        register = getattr(module, "register", None)
        if callable(register):
            register(app)
        else:
            print(f"[cli] 跳过 commands.{info.name}: 缺少 register(app)")


_discover_commands()


if __name__ == "__main__":
    app()