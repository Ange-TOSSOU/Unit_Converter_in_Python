# Unit Converter

[![CI](https://github.com/Ange-TOSSOU/Unit_Converter_in_Python/actions/workflows/ci.yml/badge.svg)](https://github.com/Ange-TOSSOU/Unit_Converter_in_Python/actions/workflows/ci.yml)

A Python tool that converts values between units of measurement. Use it from the command line, or import it from your own Python code.

```
$ unit-shift -v 10 --from km --to miles
10 km = 6.2137 mi
```

> **Status: work in progress.** The conversion engine and the command-line interface are done and tested. A graphical interface is planned.

## Installation

Requires Python 3.10 or later.

### Using the git repo
```
git clone https://github.com/Ange-TOSSOU/Unit_Converter_in_Python.git
cd Unit_Converter_in_Python
pip install .
```

### Using PyPi repo
```
pip install unit-shift
```

Check that it works:

```
unit-shift --help
```

## Quick start

```
unit-shift -v 10 --from km --to miles
unit-shift -v 100 --from celsius --to fahrenheit
unit-shift -v 5 --from "nautical mile" --to km
unit-shift --list
```

| Option | Meaning |
|---|---|
| `-v VALUE` | The number to convert |
| `--from UNIT` | The unit of that number |
| `--to UNIT` | The unit to convert to |
| `--list` (or `-l`) | List every supported unit, then exit |
| `--help` (or `-h`) | Show the help |

## Tutorial: using the command line

This walk-through takes about five minutes. Every example below was run, and the output shown is what you should see.

### 1. Your first conversion

Give a number with `-v`, the unit it is in with `--from`, and the unit you want with `--to`:

```
$ unit-shift -v 10 --from km --to miles
10 km = 6.2137 mi
```

The answer reads `source = result`. Both sides show the unit's standard symbol (`km`, `mi`), whatever you typed.

### 2. Name units your way

Unit names ignore case and extra spaces, and accept symbols, plurals and British spellings. These all mean the same thing:

```
$ unit-shift -v 10 --from km --to m
10 km = 10000 m

$ unit-shift -v 10 --from Kilometres --to "  METRES "
10 km = 10000 m
```

| You can write | For |
|---|---|
| `km`, `kilometer`, `kilometers`, `kilometre`, `KILOMETRES` | kilometer |
| `ft`, `foot`, `feet` | foot |
| `lb`, `lbs`, `pound`, `pounds` | pound |
| `l`, `liter`, `litres` | liter |
| `sec`, `second`, `seconds`, `s` | second |

### 3. Temperatures

Temperatures work like any other unit. The supported ones are `celsius`, `fahrenheit` and `kelvin` (symbols `C`, `F`, `K`). Type the names in plain text, without the degree sign.

```
$ unit-shift -v 100 --from celsius --to fahrenheit
100 C = 212 F

$ unit-shift -v 98.6 --from fahrenheit --to celsius
98.6 F = 37 C

$ unit-shift -v 0 --from kelvin --to celsius
0 K = -273.15 C
```

Only absolute temperatures are converted. A temperature *difference* ("a 10 degree rise") needs a different rule and is not supported.

### 4. Units with spaces

Put names that contain a space in quotes:

```
$ unit-shift -v 5 --from "nautical mile" --to km
5 nmi = 9.26 km

$ unit-shift -v 1 --from "cubic foot" --to liters
1 ft3 = 28.3168 l
```

### 5. Negative numbers

A negative number works as is:

```
$ unit-shift -v -40 --from celsius --to fahrenheit
-40 C = -40 F

$ unit-shift -v -2.5 --from m --to cm
-2.5 m = -250 cm
```

The one exception is a negative number written with an exponent such as `-1e3`. The command line would read it as an option, so join it to the option with `=`:

```
$ unit-shift -v=-1e3 --from m --to km
-1000 m = -1 km
```

Positive numbers with an exponent need nothing special: `unit-shift -v 1e3 --from m --to km`.

### 6. How results are displayed

Results show at least 4 decimal places and at least 4 significant digits, with trailing zeros removed. Very large and very small numbers switch to scientific notation:

```
$ unit-shift -v 2.5 --from kg --to lb
2.5 kg = 5.5116 lb

$ unit-shift -v 5 --from km --to mm
5 km = 5e6 mm

$ unit-shift -v 1 --from mm --to km
1 mm = 1e-6 km
```

The rule: at or above one million, or below 0.0001, you get scientific notation (`5e6` means 5 × 10⁶, `1e-6` means 1 × 10⁻⁶).

### 7. What can I convert?

List every supported unit, grouped by category:

```
$ unit-shift --list
length:
  millimeter (mm), centimeter (cm), meter (m), kilometer (km), inch (in), foot (ft),
  yard (yd), mile (mi), nautical mile
mass:
  ...
```

Units can only be converted within their own category: length to length, mass to mass, and so on.

### 8. When something goes wrong

Errors go to standard error, results to standard output. A message starts with the kind of problem:

```
$ unit-shift -v abc --from km --to miles
InvalidNumberError: 'abc' is not a valid number.

$ unit-shift -v 1 --from kilomter --to miles
UnknownUnitError: unknown unit 'kilomter'. Did you mean 'kilometer', ...?

$ unit-shift -v 1 --from gallon --to liter
UnsupportedUnitError: 'gallon' is not supported: it has no single worldwide definition.

$ unit-shift -v 1 --from kg --to meter
IncompatibleUnitsError: cannot convert from 'mass' to 'length'.
```

For a misspelled unit, the closest unit names are suggested. The suggestions are the closest matches, so they can include units unrelated to what you meant when nothing is close.

Some units are left out on purpose, because their size differs between countries or over time: gallon, pint, fluid ounce, cup, tablespoon, teaspoon, ton, month and year. The metric ton is supported (`tonne` or `metric ton`).

### 9. Using it in scripts

The exit code tells a script what happened:

| Exit code | Meaning |
|---|---|
| `0` | Success |
| `1` | The conversion failed (bad number, unknown or unsupported unit, incompatible units) |
| `2` | Wrong usage (a missing or unknown option) |

```
if unit-shift -v 10 --from km --to miles; then
    echo "converted"
else
    echo "failed"
fi
```

Check the code of the last command with `echo $?` (Linux and macOS), `$LASTEXITCODE` (PowerShell) or `echo %ERRORLEVEL%` (cmd).

### 10. Without installing the command

If the `unit-shift` command is not available, run the package as a module. It takes the same options:

```
python -m unitconverter -v 10 --from km --to miles
```

## Use it from Python

```python
from unitconverter import api

print(api.convert_and_format("10", "km", "miles"))  # 6.2137 mi

result = api.convert("10", "km", "miles")
print(result.value, result.unit.symbol)  # 6.2137119... mi
```

Errors are raised as subclasses of `api.ConverterError`. The API is small and may change before version 1.0.

## Supported units

| Category | Units |
|---|---|
| Length | millimeter, centimeter, meter, kilometer, inch, foot, yard, mile, nautical mile |
| Mass | milligram, gram, kilogram, metric ton, ounce, pound, stone |
| Volume | milliliter, cubic centimeter, liter, cubic meter, cubic inch, cubic foot |
| Time | millisecond, second, minute, hour, day, week |
| Temperature | kelvin, Celsius, Fahrenheit |

## Features

**Implemented**

- Five categories of units, defined from their official definitions (exact where a definition exists)
- Flexible unit names: case-insensitive, with symbols, plurals and British spellings
- Clear errors, with "did you mean" suggestions for misspelled units and an explicit message for unsupported ones
- Readable output: at least 4 decimals and 4 significant digits, with scientific notation for very large or small values
- A command-line interface and a small Python API, built on the same engine
- Unit data that is validated when it loads, so a mistake in the data fails immediately
- Automated tests with a 90% coverage gate, strict type checking, linting and formatting, run on every push by GitHub Actions (Python 3.10 to 3.13)

**Planned**

- A graphical interface
- A configurable number of decimals

## Design choices

- **Plain-text units only.** Type `celsius`, not the degree sign. The symbols are plain `C`, `F` and `K`.
- **No regionally ambiguous units.** Gallons, pints, fluid ounces, cups, spoons and the bare "ton" are left out on purpose, because their size differs between countries (for example US versus UK gallons).
- **No months or years**, because their length varies. The ounce is the avoirdupois ounce.
- **Absolute temperatures only.**
- **The engine knows nothing about the interfaces.** The command line is a thin layer over a public API, and the graphical interface will be another. See the [architecture overview](./docs/architecture.md).

## Development

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
├── api.py      # public API used by the interfaces
├── engine/     # models, errors, registry, resolver, converter, formatter
├── data/       # one module per category of units, plus the unsupported names
├── utils/      # small shared helpers
├── cli/        # command-line interface
└── gui/        # graphical interface (planned)
tests/          # mirrors the source layout
docs/           # architecture and project documentation
```

## How this project was built

This project was planned and built following the software development life cycle, with an AI assistant acting as project manager: it proposed options and reviewed my work, and I made every decision and wrote the code.

## Changelog

See [CHANGELOG.md](./CHANGELOG.md).

## License

Released under the [MIT License](./LICENSE).
