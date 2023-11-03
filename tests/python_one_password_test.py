__author__ = "Matthew Watkins"
__copyright__ = "Matthew Watkins"
__license__ = "Apache-2.0"

# Testing modules
from typer.testing import CliRunner

# Bundled modules
from python_one_password.tags import app as tags

runner = CliRunner()


# Test that we throw an error when no arguments are supplied
def test_noargs_error():
    result = runner.invoke(tags)
    assert result.exit_code == 2


# Test that main command and all sub-commands have working help
def test_cli_help():
    result = runner.invoke(tags, ["--help"])
    assert result.exit_code == 0
