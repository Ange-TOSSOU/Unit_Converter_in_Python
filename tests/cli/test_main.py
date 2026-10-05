"""Tests for the command-line interface."""

import runpy
import subprocess
import sys

import pytest

from unitconverter.cli.main import build_parser, main


def run(capsys: pytest.CaptureFixture[str], argv: list[str]) -> tuple[int, str, str]:
    """Run the CLI, returning its exit code, standard output and standard error."""
    code = main(argv)
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def run_expecting_exit(
    capsys: pytest.CaptureFixture[str], argv: list[str]
) -> tuple[int, str, str]:
    """Run the CLI when argparse is expected to exit (usage errors, help)."""
    with pytest.raises(SystemExit) as info:
        main(argv)
    captured = capsys.readouterr()
    assert isinstance(info.value.code, int)
    return info.value.code, captured.out, captured.err


# --- Successful conversions ---


@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        (["-v", "10", "--from", "km", "--to", "miles"], "10 km = 6.2137 mi"),
        (["-v", "100", "--from", "celsius", "--to", "fahrenheit"], "100 C = 212 F"),
        (["-v", "-40", "--from", "celsius", "--to", "fahrenheit"], "-40 C = -40 F"),
        (["-v", "-2.5", "--from", "m", "--to", "cm"], "-2.5 m = -250 cm"),
        (["-v", "0", "--from", "kelvin", "--to", "celsius"], "0 K = -273.15 C"),
        (["-v", "5", "--from", "km", "--to", "mm"], "5 km = 5e6 mm"),
        (["-v", "1e3", "--from", "m", "--to", "km"], "1000 m = 1 km"),
        (["-v", "1", "--from", "KILOMETRES", "--to", "  Metres "], "1 km = 1000 m"),
        (["-v", "5", "--from", "nautical mile", "--to", "km"], "5 nmi = 9.26 km"),
        (["-v", "2", "--from", "lb", "--to", "oz"], "2 lb = 32 oz"),
    ],
)
def test_conversion_prints_source_and_result(
    capsys: pytest.CaptureFixture[str], argv: list[str], expected: str
) -> None:
    code, out, err = run(capsys, argv)
    assert code == 0
    assert out == expected + "\n"
    assert err == ""


def test_a_unit_symbol_is_shown_canonically(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # "Kilometres" typed by the user is shown as the symbol "km".
    _, out, _ = run(capsys, ["-v", "3", "--from", "Kilometres", "--to", "Meters"])
    assert out == "3 km = 3000 m\n"


def test_main_reads_sys_argv_when_given_no_arguments(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        sys, "argv", ["unitconverter", "-v", "10", "--from", "km", "--to", "miles"]
    )
    assert main() == 0
    assert capsys.readouterr().out == "10 km = 6.2137 mi\n"


# --- Conversion errors ---


@pytest.mark.parametrize(
    ("argv", "expected_in_message"),
    [
        (["-v", "abc", "--from", "km", "--to", "miles"], "InvalidNumberError"),
        (["-v", "1,5", "--from", "km", "--to", "miles"], "InvalidNumberError"),
        (["-v", "nan", "--from", "km", "--to", "miles"], "InvalidNumberError"),
        (["-v", "1", "--from", "kilomter", "--to", "miles"], "UnknownUnitError"),
        (["-v", "1", "--from", "km", "--to", "mils"], "UnknownUnitError"),
        (["-v", "1", "--from", "gallon", "--to", "liter"], "UnsupportedUnitError"),
        (["-v", "1", "--from", "liter", "--to", "pints"], "UnsupportedUnitError"),
        (["-v", "1", "--from", "kg", "--to", "meter"], "IncompatibleUnitsError"),
        (
            ["-v", "1", "--from", "celsius", "--to", "kilogram"],
            "IncompatibleUnitsError",
        ),
    ],
)
def test_conversion_errors_go_to_stderr_with_exit_code_1(
    capsys: pytest.CaptureFixture[str],
    argv: list[str],
    expected_in_message: str,
) -> None:
    code, out, err = run(capsys, argv)
    assert code == 1
    assert out == ""
    assert expected_in_message in err
    assert err.endswith("\n")
    assert "Traceback" not in err


def test_unknown_unit_error_shows_suggestions(
    capsys: pytest.CaptureFixture[str],
) -> None:
    _, _, err = run(capsys, ["-v", "1", "--from", "kilomter", "--to", "miles"])
    assert "'kilomter'" in err
    assert "kilometer" in err


def test_unsupported_unit_error_names_the_unit(
    capsys: pytest.CaptureFixture[str],
) -> None:
    _, _, err = run(capsys, ["-v", "1", "--from", "Gallons", "--to", "liter"])
    assert "'Gallons'" in err


def test_the_number_error_comes_before_the_unit_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    _, _, err = run(capsys, ["-v", "abc", "--from", "blorp", "--to", "blorp"])
    assert "InvalidNumberError" in err
    assert "UnknownUnitError" not in err


# --- Usage errors ---


@pytest.mark.parametrize(
    "argv",
    [
        [],
        ["-v", "10"],
        ["-v", "10", "--from", "km"],
        ["-v", "10", "--from", "km", "--to", "miles", "extra"],
        ["--bogus"],
        ["-v", "10", "--from", "km", "--to", "miles", "--bogus"],
    ],
)
def test_wrong_usage_exits_with_code_2(
    capsys: pytest.CaptureFixture[str], argv: list[str]
) -> None:
    code, out, err = run_expecting_exit(capsys, argv)
    assert code == 2
    assert out == ""
    assert "usage:" in err


def test_missing_arguments_are_explained(
    capsys: pytest.CaptureFixture[str],
) -> None:
    _, _, err = run_expecting_exit(capsys, ["-v", "10", "--from", "km"])
    assert "value, from_unit and to_unit" in err


def test_a_negative_number_with_an_exponent_needs_an_equality_sign(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # argparse reads "-1e3".
    code, out, _ = run_expecting_exit(
        capsys, ["-v", "-1e3", "--from", "m", "--to", "km"]
    )
    assert code == 2
    code, out, _ = run(capsys, ["-v=-1e3", "--from", "m", "--to", "km"])
    assert (code, out) == (0, "-1000 m = -1 km\n")


# --- Help and unit list ---


@pytest.mark.parametrize("option", ["-h", "--help"])
def test_help_explains_the_command(
    capsys: pytest.CaptureFixture[str], option: str
) -> None:
    code, out, err = run_expecting_exit(capsys, [option])
    assert code == 0
    assert err == ""
    assert "usage: unit-shift" in out
    assert "-v 10 km miles" in out
    assert "--list" in out


@pytest.mark.parametrize("option", ["-l", "--list"])
def test_list_shows_every_category_and_unit(
    capsys: pytest.CaptureFixture[str], option: str
) -> None:
    code, out, err = run(capsys, [option])
    assert code == 0
    assert err == ""
    for category in ("Length:", "Mass:", "Volume:", "Time:", "Temperature:"):
        assert category in out
    for unit in ("kilometer", "nautical mile", "metric ton", "fahrenheit"):
        assert unit in out


def test_list_lines_are_not_too_long(capsys: pytest.CaptureFixture[str]) -> None:
    _, out, _ = run(capsys, ["--list"])
    assert all(len(line) <= 78 for line in out.splitlines())


def test_list_never_splits_a_unit_name_across_lines(
    capsys: pytest.CaptureFixture[str],
) -> None:
    _, out, _ = run(capsys, ["--list"])
    for name in ("nautical mile", "metric ton", "cubic centimeter"):
        assert name in out


def test_list_cannot_be_combined_with_a_conversion(
    capsys: pytest.CaptureFixture[str],
) -> None:
    code, out, err = run_expecting_exit(
        capsys, ["--list", "-v=10", "--from=km", "--to=miles"]
    )
    assert code == 2
    assert out == ""
    assert "-l or --list option must be used alone." in err


# --- The parser and the entry points ---


def test_the_program_name_is_unitconverter() -> None:
    assert build_parser().prog == "unit-shift"


def test_python_dash_m_runs_the_cli(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        sys, "argv", ["unitconverter", "-v=10", "--from=km", "--to=miles"]
    )
    with pytest.raises(SystemExit) as info:
        runpy.run_module("unitconverter", run_name="__main__")
    assert info.value.code == 0
    assert capsys.readouterr().out == "10 km = 6.2137 mi\n"


def test_python_dash_m_exits_with_code_1_on_a_conversion_error(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        sys, "argv", ["unitconverter", "-v=abc", "--from=km", "--to=miles"]
    )
    with pytest.raises(SystemExit) as info:
        runpy.run_module("unitconverter", run_name="__main__")
    assert info.value.code == 1
    assert "InvalidNumberError" in capsys.readouterr().err


def test_the_command_works_in_a_real_subprocess() -> None:
    done = subprocess.run(
        [sys.executable, "-m", "unitconverter", "-v=10", "--from=km", "--to=miles"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode == 0
    assert done.stdout == "10 km = 6.2137 mi\n"
    assert done.stderr == ""


def test_a_failing_command_in_a_real_subprocess_exits_with_code_1() -> None:
    done = subprocess.run(
        [sys.executable, "-m", "unitconverter", "-v=1", "--from=kg", "--to=meter"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode == 1
    assert done.stdout == ""
    assert "IncompatibleUnitsError" in done.stderr
