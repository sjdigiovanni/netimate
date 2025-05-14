import pytest

from netimate import errors


@pytest.mark.parametrize(
    "exc_cls, expected",
    [
        (errors.NetimateError, "An unknown Netimate error occurred."),
        (errors.ConfigError, "Configuration error"),
        (errors.PluginError, "Plugin system error"),
        (errors.ConnectionProtocolError, "Connection to device failed"),
        (errors.AuthError, "Authentication failed"),
        (errors.ConnectionTimeoutError, "Connection timed out"),
        (errors.CommandError, "Failed to execute command on device"),
        (errors.RunnerError, "Runner failed to complete task"),
        (errors.CliUsageError, "Invalid CLI usage"),
        (errors.ShellRuntimeError, "Shell command failed"),
        (errors.ApplicationError, "Application-level failure"),
    ],
)
def test_default_message(exc_cls, expected):
    err = exc_cls()
    assert str(err) == expected
