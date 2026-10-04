# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Project skeleton: `src/` package layout, `pyproject.toml`, MIT license
- Development tooling: ruff, mypy (strict) and pytest
- Continuous integration with GitHub Actions, on Python 3.10 to 3.13
- Unit catalog: length, mass, volume, time and temperature units, with symbols, plurals and British spellings as aliases
- Flexible unit lookup: case-insensitive, ignoring extra spaces
- Internal foundation: unit and quantity models, error types, and a unit registry that validates its data when it loads
- README and architecture overview
