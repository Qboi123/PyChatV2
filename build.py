import os

from compiler import Compiler

if __name__ == '__main__':
    # Get main folder
    main_folder_ = os.getcwd()

    # Compiler class
    compiler = Compiler(
        exclude=[".idea", ".gitattributes", ".gitignore", "build.py", "README.md",
                 "obj", "icon.png", ".git", "compiler.py", "dll"],
        icon="icon.ico", main_folder=os.getcwd(), main_file="pychat.py",
        hidden_imports=["PIL", "sys", "os", "tkinter", "tkinter.ttk", "tkinter.colorchooser"
                        "collections", "typing", "tempfile", "io", "win32ctypes", "tkinter.filedialog"],
        log_level="INFO", app_name="PyChat", clean=True, hide_console=False)
    compiler.reindex()

    # Get argument and command
    args = compiler.get_args()
    command = compiler.get_command(args)

    # Compile workspace
    compiler.compile(command)
