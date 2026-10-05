# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 06-10-2026

### Added

- Command-line interface: `convert -v VALUE --from UNIT --to UNIT`, also available as `python -m unitconverter`
- `convert --list` to show every supported unit, and `convert --help` with examples
- Output such as `10 km = 6.2137 mi`: results on standard output, errors on standard error, and exit codes 0 (success), 1 (conversion failed) and 2 (wrong usage)
- Conversion between any two units of the same category, including temperatures
- Readable output: at least 4 decimals and 4 significant digits, with scientific notation at 1e6 and above or below 1e-4
- Number parsing with clear errors for invalid input (text, `nan`, `inf`, decimal commas, underscores)
- Clear messages for unsupported units (gallon, pint, ton, fluid ounce, cup, spoons, month, year)
- "Did you mean" suggestions for misspelled unit names
- A small public Python API (`unitconverter.api`) shared by the interfaces
- Unit catalog: length, mass, volume, time and temperature units, with symbols, plurals and British spellings as aliases
- Flexible unit lookup: case-insensitive, ignoring extra spaces
- Internal foundation: unit and quantity models, error types, and a unit registry that validates its data when it loads
- Project skeleton: `src/` package layout, `pyproject.toml`, MIT license
- Development tooling: ruff, mypy (strict) and pytest with a 100% coverage gate
- Continuous integration with GitHub Actions, on Python 3.10 to 3.13
- README with a command-line tutorial, and an architecture overview