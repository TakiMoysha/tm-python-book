"""required ffmpeg"""
#!/usr/bin/env python

import csv
import logging
import os
import re
import subprocess
import sys
from argparse import ArgumentParser
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

import pytest

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt

    console = Console()
    HAS_RICH = True
except ImportError:
    from getpass import getuser  # fallback

    HAS_RICH = False
    console = None  # будем использовать print

__VERSION__ = "0.1.0-dev"

SUPPORTED_EXTENSIONS = {".mp4", ".avi", ".mkv", ".mov", ".webm"}
TECHNICAL_NAME_PATTERN = re.compile(r"^(VID|REC|CAM|202[0-9]|SCREEN|VIDEO|CLIP|DSC|MOVIE|FILE)", re.IGNORECASE)
PLAYERS = ["mpv", "ffplay"]
LOG_FILE = "tmp/rename.log"


def setup_logging(directory):
    log_path = os.path.join(directory, "rename.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),  # terminal output
        ],
        force=True,  # перезатираем предыдущую конфигурацию
    )
    logging.info("=" * 60)
    logging.info(f"queue_rename.py {__VERSION__}({getuser()})")
    logging.info(f"Target Directory {directory}")


def setup():
    _target_dir = os.getenv("TM_TARGET_DIR", None)
    setup_logging(_target_dir)
    return {"target_dir": _target_dir}


@contextmanager
def _action_logger():
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "old_path", "new_path"])
        yield writer


def write_rename_log(old_path, new_path):
    with _action_logger() as writer:
        timestamp = datetime.now().isoformat()
        writer.writerow([timestamp, old_path, new_path])
    console.print(f"[green]✓ Logged: {old_path} → {new_path}[/green]")


def test_write_rename_log():
    write_rename_log(
        os.path.relpath("test_old_path", "/var/tmp/"),
        os.path.relpath("test_new_path", "/test/full/path"),
    )


def is_player_available(player_name):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(player_name)
    if fpath:
        if is_exe(player_name):
            return player_name
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, player_name)
            if is_exe(exe_file):
                return exe_file
    return None


def get_available_player():
    for player in PLAYERS:
        if is_player_available(player):
            return player

    return None


def preview_file(filepath, player, *, player_ops=None):
    try:
        match player:
            case "ffplay":
                # ffplay: проигрывает и закрывается, -autoexit — закрыть после окончания
                subprocess.run(
                    [player, "-autoexit", filepath] + (player_ops or []),
                    check=True,
                    stderr=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                )
            case "mpv":
                subprocess.run([player, filepath] + (player_ops or []), check=True)
            case "xdg-open":
                # xdg-open открывает файл стандартной программой
                subprocess.run([player, filepath] + (player_ops or []), check=True)
            case _:
                logging.warning(f"Unknown player: {player}")
    except subprocess.CalledProcessError:
        logging.error(f"Error while playing {player}:{filepath}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")


@pytest.mark.skip(reason="idk how prevent running file, only for manual testing")
@pytest.mark.manual
def test_preview_file(testfile):
    preview_file(str(testfile), PLAYERS[0], player_ops=["--no-video"])


def scan_media_dir(target_dir):
    media_files = []
    for root, _, files in os.walk(target_dir):
        for file in files:
            name, ext = os.path.splitext(file)
            if ext.lower() in SUPPORTED_EXTENSIONS:
                filepath = os.path.join(root, file)
                # if not TECHNICAL_NAME_PATTERN.match(name):
                #     continue
                media_files.append(filepath)

    if not media_files:
        console.print("[yellow]Nothing to process[/yellow]")
        return

    console.print(f"Found {len(media_files)} media files", style="blue")


@pytest.mark.manual
def test_scan_media_dir(testfile):
    target_dir = os.path.dirname(testfile)
    scan_media_dir(target_dir)


def main(target_dir):
    media_files = scan_media_dir(target_dir)
    player = get_available_player()

    # filters ...

    for filepath in media_files:
        filename = os.path.basename(filepath)
        dirpath = os.path.dirname(filepath)

        console.print(Panel(f"[bold]File:[/bold] {filename}", style="cyan"))

        action = None
        while True:
            match action:
                case None:
                    action = Prompt.ask(
                        "[p]preview (default), [r]ename, [s]kip, [q]uit?",
                        choices=["p", "r", "s", "q"],
                        default="p",
                        show_choices=True,
                    )
                case "p":
                    preview_file(filename, player)
                    action = None
                case "r":
                    logging.info(f"rename {filename} started")
                    new_name = new_name_form_handle(filename)
                    # _file_path, _new_file_path = rename_naming_resolve()
                    rename_file(...)
                case "s":
                    logging.info(f"Skip {filename}")
                    break
                case "q":
                    logging.info(f"Stop at {filename}, exit...")
                    break
                case _:
                    console.print(f"")
                    action = None

        if action == "q":
            return

    console.print("[bold green]Success! All files was renamed.[/bold green]")
    pass


def rename_file(filepath, new_filename):
    try:
        os.rename(filepath, new_filename)
        console.print(f"[green]✓ Renamed:[/green] {filename} → {new_filename}")
        write_rename_log(filepath, new_filepath)
    except Exception as e:
        console.print(f"[red]Rename exception: {e}[/red]")
        action = "q"


def new_name_form_handle(filename):
    new_name = Prompt.ask("New filename: ")

    if not new_name.strip():
        console.print("[yellow]Empty name.[/yellow]")
        return

    #
    ext = os.path.splitext(filename)[1]
    new_filename = new_name.strip() + ext
    new_filepath = os.path.join(dirpath, new_filename)

    if os.path.exists(new_filepath):
        console.print(f"[red]Файл '{new_filename}' уже существует![/red]")
        action = Prompt.ask("Что дальше?", choices=["p", "r", "s", "q"], default="r")
        continue

    elif new_name_input:
        # Добавляем расширение старого файла
        ext = os.path.splitext(filename)[1]
        new_filename = new_name_input + ext
        new_filepath = os.path.join(dirpath, new_filename)

        if os.path.exists(new_filepath):
            print(f"Файл с именем '{new_filename}' уже существует!")
        else:
            os.rename(filepath, new_filepath)
            print(f"Переименовано в: {new_filename}\n")
            break
    else:
        print("Имя не может быть пустым.")


def runner():
    parser = ArgumentParser()

    parser.add_argument("target-dir", help="TM_TARGET_DIR equivalent, has a higher priority", default=None)

    args = parser.parse_args()
    options = setup()

    target_dir = args.target_dir or options.get("target_dir", None)

    if target_dir is None:
        raise Exception("set TM_TARGET_DIR env or use --target-dir")

    main(target_dir=target_dir)


@pytest.fixture(name="testfile")
def _testfile():
    storedir_path = Path(os.getenv("STOREDIR", ""))
    if not storedir_path.exists():
        assert False, "STOREDIR environment variable not found"

    if (file_path := storedir_path / "downloads/0-output.mp4") is None:
        assert False, "testfile not found"

    return file_path


def test_should_find_player():
    assert get_available_player(), "can't find player"
