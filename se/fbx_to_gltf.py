import logging
import sys
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from pathlib import Path

import bpy


def resolve_verbosity(verbosity: str):
    levels = {
        "debug": logging.DEBUG,  # 10
        "info": logging.INFO,  # 20
        "warning": logging.WARNING,  # 30
        "error": logging.ERROR,  # 40
        "critical": logging.CRITICAL,  # 50
    }
    level = levels.get(verbosity.lower(), logging.INFO)
    logging.basicConfig(format="[%(levelname)-8s] %(message)s", level=level)
    logging.debug(f"Verbosity level: {verbosity} ({level})")
    return logging.getLogger()


def resolve_input(value: str) -> Path:
    path = Path(value).resolve()

    if not path.exists():
        raise Exception(f"Input file not found: {path}")

    if not path.is_file():
        raise Exception(f"Input path is not a file: {path}")

    if path.suffix.lower() != ".fbx":
        raise Exception(f"Input file must be .fbx, got: {path.suffix}")

    logging.debug(f"Input file resolved: {path}")
    return path


def resolve_output(input: Path, output: str) -> Path:
    path = Path(output).resolve()
    default_output = input.with_suffix(".gltf")

    # If output is not specified (defaults to "."), use default name
    if output == ".":
        logging.debug(f"No output specified, using default: {default_output}")
        return default_output

    # If it's an existing directory, use default filename inside it
    if path.exists() and path.is_dir():
        output_path = path / default_output.name
        logging.debug(f"Output is directory, using: {output_path}")
        return output_path

    # If parent directory doesn't exist, error
    parent = path.parent
    if not parent.exists():
        raise Exception(f"Output directory does not exist: {parent}")

    if not parent.is_dir():
        raise Exception(f"Output parent is not a directory: {parent}")

    # Ensure .gltf extension
    if path.suffix.lower() != ".gltf":
        path = path.with_suffix(".gltf")
        logging.debug(f"Added .gltf extension: {path}")

    logging.debug(f"Output file resolved: {path}")
    return path


def main(input_file: Path, output: Path, logger: logging.Logger):
    logger.info(f"Processing: {input_file} -> {output}")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(input_file))
    # GLTF_EMBEDDED or GLB
    bpy.ops.export_scene.gltf(
        filepath=str(output),
        export_format="GLB",
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_apply=True,
    )


if __name__ == "__main__":
    epilog = """\
examples:
  python fbx_to_gltf.py -- /full/path/to/file.fbx
  blender --background --python fbx_to_gltf.py -- /full/path/to/file.fbx
  blender -b --python fbx_to_gltf.py -- model.fbx -v debug -o ./tmp/output.gltf
"""

    parser = ArgumentParser(
        description="Convert FBX to GLTF (web pipeline).",
        epilog=epilog,
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument("file", help="Path to FBX file.")
    parser.add_argument(
        "-v",
        "--verbosity",
        choices=["debug", "info", "warning", "error", "critical"],
        default="info",
        help="Verbosity level (default: info)",
    )
    parser.add_argument("-o", "--output", help="Output dir (should exist) or filename", default=".")

    # batch_parser = parser.add_subparsers(dest="batch")

    runtime_args = sys.argv[sys.argv.index("--") + 1 :]
    args = parser.parse_args(runtime_args)

    logger = resolve_verbosity(args.verbosity)
    file = resolve_input(args.file)
    output = resolve_output(file, args.output)

    # logger = logging.getLogger()
    main(file, output, logger)
