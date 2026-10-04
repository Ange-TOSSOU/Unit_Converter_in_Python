# Unit Converter

![CI](https://github.com/<your-username>/<your-repo>/actions/workflows/ci.yml/badge.svg)

A Python tool that converts values between units of measurement, from the command line or a graphical interface.

> **Status: work in progress.** The conversion engine's foundation and the unit catalog are done and tested. The conversion function, the command-line interface and the graphical interface are next. Usage instructions will be added when the first interface is available.

## Supported units

| Category | Units |
|---|---|
| Length | millimeter, centimeter, meter, kilometer, inch, foot, yard, mile, nautical mile |
| Mass | milligram, gram, kilogram, metric ton, ounce, pound, stone |
| Volume | milliliter, cubic centimeter, liter, cubic meter, cubic inch, cubic foot |
| Time | millisecond, second, minute, hour, day, week |
| Temperature | kelvin, Celsius, Fahrenheit |

Unit names are matched flexibly: case-insensitive, with symbols (`km`), plurals (`feet`) and British spellings (`metres`, `litres`) accepted.

## Features

**Implemented**

- Five categories of units, defined from their official definitions (exact where a definition exists)
- Flexible unit lookup by name, symbol or alias, ignoring case and extra spaces
- Unit data that is validated when it loads, so a mistake in the data fails immediately
- Automated tests with a 90% coverage gate, strict type checking, linting and formatting, run on every push by GitHub Actions (Python 3.10 to 3.13)

**Planned**

- Conversion between any two units of the same category
- Readable output: 4 decimal places, with scientific notation for very large or small values
- Friendly errors, including "did you mean...?" suggestions and clear messages for unsupported units
- A command-line interface and a graphical interface, both built on the same engine

## Design choices

- **Plain-text units only.** Type `celsius`, not the degree sign. The symbols are plain `C`, `F` and `K`.
- **No regionally ambiguous units.** Gallons, pints, fluid ounces, cups, spoons and the bare "ton" are left out on purpose, because their size differs between countries (for example US versus UK gallons). The metric ton is supported as `tonne` or `metric ton`.
- **No months or years**, because their length varies. The ounce is the avoirdupois ounce.
- **Absolute temperatures only.** A temperature difference (for example "a 10 degree rise") needs a different rule and is not supported.
- **The engine knows nothing about the interfaces.** The command line and the GUI will be thin layers over the same engine. See the [architecture overview](docs/architecture.md).

## Development

Requires Python 3.10 or later.

```
python -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

The four checks that CI runs:

```
ruff check .
ruff format --check .
mypy
pytest
```

`ruff format .` and `ruff check --fix .` fix most formatting and lint issues automatically.

## Project layout

```
src/unitconverter/
├── engine/     # models, errors and the unit registry (no user interface code)
├── data/       # one module per category of units
├── utils/      # small shared helpers
├── cli/        # command-line interface (planned)
└── gui/        # graphical interface (planned)
tests/          # mirrors the source layout
docs/           # architecture and project documentation
```

## How this project was built

This project was planned and built following the software development life cycle, with Claude Code as my AI assistant acting as project manager: it proposed options and reviewed my work, and I made every decision and wrote the code.

## License

Released under the [MIT License](LICENSE).
