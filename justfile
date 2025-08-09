set dotenv-load

# ex: just run test_filen.py::test_func -v
test filename:
    uv run pytest --verbose --capture=no --log-cli-level=INFO {{filename}} $@

# ex: just multi "uv run packages/test_opsqueue.py --consumer"
multi command factor='10':
    seq {{factor}} | xargs -I {} -P {{factor}} {{command}}
