"""Build the Blender extension with source and license notices, without caches."""

import argparse
from pathlib import Path
import zipfile


def build(output: Path) -> Path:
    root = Path(__file__).resolve().parent
    package = root / "blender_ko_3d"
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(package.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts and path.suffix in {".py", ".toml"}:
                archive.write(path, path.relative_to(root).as_posix())
        for name in ("LICENSE", "THIRD_PARTY_NOTICES.md", "README.md"):
            archive.write(root / name, "blender_ko_3d/" + name)
    return output


def main():
    parser = argparse.ArgumentParser(description="Build Blender KO 3D extension")
    parser.add_argument("-o", "--output", type=Path, default=Path(__file__).resolve().parent / "blender-ko-3d.zip")
    print(build(parser.parse_args().output))


if __name__ == "__main__":
    main()
