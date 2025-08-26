set dotenv-load


[doc("""
Examples:
    - just run test_file.py::test_func -v 
    - env TARGET_DIR=/var/media/data STOREDIR=/var/media/ just run tooling::queue_rename.py
""")]
test filename:
    uv run pytest --verbose --capture=no --log-cli-level=INFO {{filename}}

[doc("""
Examples:
    - just multi "uv run packages/case_opsqueue.py --consumer"
""")]
multi command factor='10':
    seq {{factor}} | xargs -I {} -P {{factor}} {{command}}
