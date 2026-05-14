#!/usr/bin/env python3
"""
code_bundler.py
---------------
Recorre un directorio de proyecto y genera un único archivo .txt
con todos los archivos de código, titulados y separados, listo para
pasarle a un agente de IA.

Uso:
    python code_bundler.py                        # usa el directorio actual
    python code_bundler.py /ruta/a/tu/proyecto
    python code_bundler.py /ruta/proyecto -o salida.txt
    python code_bundler.py /ruta/proyecto --include .py .js .ts
    python code_bundler.py /ruta/proyecto --exclude node_modules .git dist
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# ─── Extensiones de código incluidas por defecto ───────────────────────────────
DEFAULT_EXTENSIONS = {
    # Web
    ".html", ".htm", ".css", ".scss", ".sass", ".less",
    ".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte",
    # Backend
    ".py", ".rb", ".php", ".java", ".go", ".rs", ".cs",
    ".cpp", ".c", ".h", ".hpp", ".swift", ".kt", ".scala",
    # Config / datos estructurados
    ".json", ".yaml", ".yml", ".toml", ".ini", ".env.example",
    # Scripts
    ".sh", ".bash", ".zsh", ".ps1", ".bat",
    # Docs de código
    ".md", ".mdx", ".rst",
    # Base de datos
    ".sql",
    # Otros
    ".graphql", ".proto", ".dockerfile",
}

# ─── Carpetas ignoradas por defecto ────────────────────────────────────────────
DEFAULT_EXCLUDE_DIRS = {
    "node_modules", ".git", ".svn", "__pycache__", ".mypy_cache",
    ".pytest_cache", "venv", ".venv", "env", ".env",
    "dist", "build", "out", ".next", ".nuxt", ".output",
    "coverage", ".coverage", ".tox", "eggs", ".eggs",
    "target",  # Rust / Java
    ".idea", ".vscode", ".vs",
    "vendor",  # Go / PHP
}

# ─── Archivos ignorados por defecto ────────────────────────────────────────────
DEFAULT_EXCLUDE_FILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "Cargo.lock", "Gemfile.lock", "composer.lock",
    ".DS_Store", "Thumbs.db",
}

SEPARATOR = "=" * 72
FILE_HEADER = "─" * 72


def should_include(path: Path, include_exts: set, exclude_dirs: set,
                   exclude_files: set) -> bool:
    """Devuelve True si el archivo debe incluirse en el bundle."""
    # Ignorar archivos ocultos (empiezan con .)
    if path.name.startswith("."):
        return False
    # Ignorar archivos en la lista de excluidos
    if path.name in exclude_files:
        return False
    # Solo incluir extensiones permitidas
    if path.suffix.lower() not in include_exts:
        return False
    # Ignorar carpetas excluidas en cualquier nivel
    for part in path.parts:
        if part in exclude_dirs:
            return False
    return True


def read_file_safe(filepath: Path) -> str:
    """Lee un archivo de forma segura, intentando varios encodings."""
    for encoding in ("utf-8", "latin-1", "cp1252"):
        try:
            return filepath.read_text(encoding=encoding)
        except (UnicodeDecodeError, PermissionError):
            continue
    return "[⚠ No se pudo leer el archivo — posible contenido binario]"


def bundle(root: Path, output: Path, include_exts: set,
           exclude_dirs: set, exclude_files: set) -> int:
    """Genera el archivo bundle. Devuelve la cantidad de archivos incluidos."""

    all_files = sorted(
        [p for p in root.rglob("*")
         if p.is_file() and should_include(p.relative_to(root),
                                           include_exts, exclude_dirs,
                                           exclude_files)],
        key=lambda p: (p.parent, p.name)
    )

    if not all_files:
        print("⚠  No se encontraron archivos con las extensiones indicadas.")
        return 0

    with output.open("w", encoding="utf-8") as out:
        # ── Encabezado del bundle ──────────────────────────────────────────
        out.write(f"{SEPARATOR}\n")
        out.write(f"  CODE BUNDLE\n")
        out.write(f"  Proyecto  : {root.resolve()}\n")
        out.write(f"  Generado  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        out.write(f"  Archivos  : {len(all_files)}\n")
        out.write(f"{SEPARATOR}\n\n")

        # ── Índice de archivos ─────────────────────────────────────────────
        out.write("ÍNDICE DE ARCHIVOS\n")
        out.write(f"{FILE_HEADER}\n")
        for i, filepath in enumerate(all_files, 1):
            rel = filepath.relative_to(root)
            out.write(f"  {i:>3}. {rel}\n")
        out.write(f"{FILE_HEADER}\n\n\n")

        # ── Contenido de cada archivo ──────────────────────────────────────
        for i, filepath in enumerate(all_files, 1):
            rel = filepath.relative_to(root)
            size_kb = filepath.stat().st_size / 1024
            content = read_file_safe(filepath)

            out.write(f"{SEPARATOR}\n")
            out.write(f"  ARCHIVO {i}/{len(all_files)}\n")
            out.write(f"  Ruta   : {rel}\n")
            out.write(f"  Tamaño : {size_kb:.1f} KB\n")
            out.write(f"{SEPARATOR}\n\n")
            out.write(content)

            # Asegurar salto de línea al final
            if content and not content.endswith("\n"):
                out.write("\n")
            out.write("\n\n")

    return len(all_files)


def main():
    parser = argparse.ArgumentParser(
        description="Concatena todos los archivos de código en un único .txt"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directorio raíz del proyecto (por defecto: directorio actual)"
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Nombre del archivo de salida (por defecto: <nombre_proyecto>_bundle.txt)"
    )
    parser.add_argument(
        "--include",
        nargs="+",
        metavar="EXT",
        help="Extensiones a incluir, ej: --include .py .js  (reemplaza las por defecto)"
    )
    parser.add_argument(
        "--add",
        nargs="+",
        metavar="EXT",
        help="Extensiones extra a agregar a las por defecto, ej: --add .tf .hcl"
    )
    parser.add_argument(
        "--exclude",
        nargs="+",
        metavar="DIR",
        help="Carpetas adicionales a ignorar, ej: --exclude migrations fixtures"
    )
    parser.add_argument(
        "--no-md",
        action="store_true",
        help="Excluir archivos Markdown (.md, .mdx)"
    )

    args = parser.parse_args()

    root = Path(args.directory).resolve()
    if not root.is_dir():
        print(f"❌ No se encontró el directorio: {root}")
        sys.exit(1)

    # Armar set de extensiones
    if args.include:
        include_exts = {e if e.startswith(".") else f".{e}" for e in args.include}
    else:
        include_exts = set(DEFAULT_EXTENSIONS)
        if args.add:
            include_exts |= {e if e.startswith(".") else f".{e}" for e in args.add}

    if args.no_md:
        include_exts -= {".md", ".mdx", ".rst"}

    # Armar set de carpetas excluidas
    exclude_dirs = set(DEFAULT_EXCLUDE_DIRS)
    if args.exclude:
        exclude_dirs |= set(args.exclude)

    # Archivo de salida
    output_name = args.output or f"{root.name}_bundle.txt"
    output = Path(output_name).resolve()

    print(f"\n📁 Proyecto  : {root}")
    print(f"📄 Salida    : {output}")
    print(f"🔍 Extensiones: {', '.join(sorted(include_exts))}\n")

    count = bundle(root, output, include_exts, exclude_dirs, DEFAULT_EXCLUDE_FILES)

    if count:
        size_mb = output.stat().st_size / (1024 * 1024)
        print(f"✅ Bundle generado con {count} archivos → {output.name} ({size_mb:.2f} MB)")
    else:
        print("❌ No se generó ningún archivo.")


if __name__ == "__main__":
    main()
