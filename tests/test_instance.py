#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_labtest
----------------------------------

Tests for `labtest instance` module.
"""

from click.testing import CliRunner

from labtest import cli


def test_command_line_interface():
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert 'Show this message and exit.' in help_result.output
