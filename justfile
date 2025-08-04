set dotenv-load

# ex: just run test_filen.py::test_func -v
run filename:
    uv run pytest --verbose --capture=no --log-cli-level=INFO {{filename}} $@
