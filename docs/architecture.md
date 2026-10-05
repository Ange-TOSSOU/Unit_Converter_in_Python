# Architecture overview

This document describes how the unit converter is structured and why. Components are marked **implemented** or **planned**, so the document stays truthful as the project grows.

## Design principles

1. **The engine knows nothing about the interface.** It takes plain values and strings and returns plain results or typed errors. It never prints or reads input.
2. **Units are data, not logic.** Adding a unit means adding one entry to a data module.
3. **One conversion path for everything**, including temperature, so there are no special cases to maintain.
4. **Errors are typed**, so each interface can present them in its own way.
5. **Dependencies point inward only.** Interfaces depend on the public API, the API on the engine, never the other way round.

## Layers

```
┌─────────────┐     ┌────────────┐
│  CLI layer  │     │  GUI layer │          presentation only
|(implemented)|     |  (planned) |
└─────┬───────┘     └─────┬──────┘
      └─────────┬────────┘
          ┌─────▼──────┐
          │ Public API │   builds the registry from the data,      (implemented)
          └─────┬──────┘   exposes parse and convert
    ┌───────────┼──────────────┐
┌───▼────┐  ┌───▼─────┐  ┌─────▼─────┐
│Resolver│  │Converter│  │ Formatter │       engine                (implemented)
└───┬────┘  └───┬─────┘  └───────────┘
    └────┬──────┘
    ┌────▼─────┐   ┌────────┐   ┌────────┐
    │ Registry │   │ Models │   │ Errors │  engine                (implemented)
    └────┬─────┘   └────────┘   └────────┘
         │ uses
    ┌────▼─────┐          ┌────────────┐
    │  utils   │          │    data    │    unit definitions      (implemented)
    └──────────┘          └────────────┘
```

The `data` package depends only on the engine's models. Nothing in the engine imports from `data`: the registry receives its categories as an argument, and the public API connects the two. The `utils` package depends on nothing in the project. The CLI imports only the public API.

## Project layout

```
src/unitconverter/
├── api.py              # public API: the only module interfaces import
├── __main__.py         # python -m unitconverter
├── engine/
│   ├── models.py       # Unit, Category, Quantity
│   ├── errors.py       # exception hierarchy
│   ├── registry.py     # validates and indexes unit data
│   ├── resolver.py     # name -> unit, or a helpful error
│   ├── numbers.py      # parse_number
│   ├── converter.py    # parse and convert
│   └── formatter.py    # number and quantity display
├── data/               # one module per category, constants only
│   ├── length.py
│   ├── mass.py
│   ├── volume.py
│   ├── duration.py     # time units (named to avoid clashing with the stdlib "time")
│   ├── temperature.py
│   └── unsupported.py  # names recognized but deliberately not supported
├── utils/
│   └── normalize.py    # canonical form of a unit name
├── cli/
│   └── main.py         # argparse command line (implemented)
└── gui/                # planned
```

## Data model (implemented)

```
Unit:      id, name, symbol, factor, aliases, offset
Category:  name, base_unit_id, units
Quantity:  value, unit
```

All three are plain dataclasses. `Unit` and `Category` take keyword arguments only.

Every unit is defined relative to its category's **base unit** (meter, kilogram, liter, second, kelvin):

```
base_value = (value + offset) * factor
value      = base_value / factor - offset
```

| Unit | Factor | Offset | Why |
|---|---|---|---|
| kilometer (base: meter) | 1000 | 0 | Pure scaling |
| Celsius (base: kelvin) | 1 | 273.15 | Shifted scale |
| Fahrenheit (base: kelvin) | 5/9 | 459.67 | Scaling and shift |

Temperature therefore needs no special code: linear units are simply the case where the offset is 0. Values are Python floats, and tests use a relative tolerance of 1e-6 or tighter.

`Quantity` pairs a value with its unit, so a conversion result carries the canonical unit with it, and interfaces can show a symbol without a second lookup. Equality compares value and unit, not physical size: one kilometer is not equal to 1000 meters as a `Quantity`.

## Unit data (implemented)

- One module per category, containing **constants only**: no functions and no branching.
- Factors come from official definitions, written as exact values or as visible expressions (for example the ounce as a pound divided by 16). Sources are cited in each module's docstring.
- Ids are lowercase, singular, `snake_case`. Plurals and spelling variants are listed explicitly as aliases, never derived in code.
- `data/__init__.py` gathers all categories into one tuple, and exposes the unsupported names.
- Regionally ambiguous units (gallon, pint, fluid ounce, ton, cup, spoons) and variable-length units (month, year) are excluded on purpose. Their names, with plurals and abbreviations, are listed in `unsupported.py`.

## Name normalization (implemented)

`utils/normalize.py` turns a name into a canonical form for matching: case-insensitive, with leading, trailing and repeated whitespace removed. Empty input gives an empty string. It does not strip plurals, correct spelling or handle Unicode symbols: input is plain text.

## Registry (implemented)

The registry receives a list of categories and an optional collection of unsupported names, **validates everything in its constructor**, and builds its lookup tables once. A half-built registry can never exist.

| Rule | Why |
|---|---|
| Category names are unique | One definition per category |
| Unit ids are unique across all categories | One definition per unit |
| Each category's base unit exists, with factor 1 and offset 0 | The anchor of the model |
| Every factor is positive and finite, every offset is finite | No division by zero or nonsense values |
| No name, symbol or alias is empty after normalization | An empty key can never match |
| A normalized name, symbol or alias belongs to exactly one unit, across all categories | No ambiguity at lookup time |
| No unsupported name is empty | An empty key can never match |
| No unsupported name is also a supported name, symbol or alias | A name cannot be both supported and unsupported |

A name repeated inside one unit, or inside the unsupported list, is ignored, because it is not ambiguous. The name, symbol and aliases of a unit are all indexed under one rule, which means symbols that differ only by case would collide, and the registry reports it at load time.

Public methods:

| Method | Returns |
|---|---|
| `find_unit(name)` | The unit matching a name, symbol or alias, or `None` |
| `is_unsupported(name)` | Whether a name is recognized but deliberately not supported |
| `category_of(unit)` | The unit's category, looked up by id. An unknown unit raises a `RegistryError` |
| `aliases()` | Every normalized lookup key (never an unsupported name) |
| `categories` | All categories, in order |

The registry only looks things up. What a miss means is decided by the resolver.

## Resolver (implemented)

`resolve(name, registry)` returns a unit, or raises an error:

1. If the registry finds the name, return the unit.
2. If the name is unsupported, raise `UnsupportedUnitError`.
3. Otherwise raise `UnknownUnitError` with the three closest unit names.

Suggestions are unit names, not spellings: every lookup key is ranked by similarity with the standard library's `difflib`, mapped back to its unit, and deduplicated, so a unit with several spellings is suggested once. There is no similarity cutoff, so three suggestions are always offered, even for unrelated input.

## Numbers and conversion (implemented)

`parse_number` accepts ints, floats and text in Python's float syntax with surrounding spaces ignored. It rejects `nan`, `inf`, values too large for a float, decimal commas, underscores, non-ASCII digits, booleans and other types.

Conversion is a plain function that takes the registry as an argument, instead of a method on `Quantity`. A `Unit` does not know its category, only the registry does, and a function keeps the models free of hidden dependencies.

```
function parse(value, unit_name, registry) -> Quantity
    number = parse_number(value)                # InvalidNumberError
    unit   = resolve(unit_name, registry)       # UnknownUnitError, UnsupportedUnitError
    return Quantity(number, unit)

function convert(quantity, target_unit, registry) -> Quantity
    if categories differ: raise IncompatibleUnitsError
    if same unit: return the value unchanged
    base = (quantity.value + quantity.unit.offset) * quantity.unit.factor
    resukt = base_value / target_unit.factor - target_unit.offset
    return Quantity(result, target_unit)
```

The number is always checked before the unit, and the source unit before the target unit. Converting a unit to itself skips the arithmetic, so the value comes back exactly.

## Output formatting (implemented)

`format_number` is a pure function:

| Value | Display |
|---|---|
| Zero | `0` |
| At or above 1e6, or below 1e-4 | Scientific notation with 4 significant digits, no padding: `1.235e9`, `1.234e-5` |
| Everything else | Fixed notation with at least 4 decimals and at least 4 significant digits, trailing zeros removed |
| `inf`, `nan` | Shown as such |

The notation is decided from the rounded value, so `999999.99996` shows as `1e6`, not `1000000`. `format_quantity` adds the unit symbol: `6.2137 mi`. The engine returns full precision, and the interface decides how to display it.

## Errors (implemented)

```
ConverterError (base, shown to users)
├── InvalidNumberError       # the value cannot be read as a number
├── UnknownUnitError         # carries the name and suggestions
├── UnsupportedUnitError     # carries the name
└── IncompatibleUnitsError   # carries both category names

RegistryError                # invalid unit data (a developer error)
```

- Interfaces catch `ConverterError` and show its message. They never parse message text: each error carries its data as attributes.
- `RegistryError` deliberately **does not** extend `ConverterError`: a bug in the data must not be hidden behind a friendly user-facing message.
- Messages begin with the error's class name, for example "InvalidNumberError: 'abc' is not a valid number.". This is a deliberate choice, made for logs and bug reports.

## Public API (implemented)

`api.py` is the only module the interfaces import. It builds the real registry once from the data and exposes:

| Function | Purpose |
|---|---|
| `parse_quantity(value, unit_name)` | Read a typed value and unit into a `Quantity` |
| `convert_quantity(quantity, to_unit)` | Convert a quantity to a named unit |
| `convert(value, from_unit, to_unit)` | Both steps in one call |
| `convert_and_format(value, from_unit, to_unit)` | The result as display text |
| `format_quantity(quantity)` | A quantity as text with its symbol |
| `list_units()` | Unit names by category, for selectors and listings |
| `get_registry()` | The shared registry |

`ConverterError` and `Quantity` are re-exported, so interfaces never import from the engine.

## Command-line interface (implemented)

```
unit-shift -v VALUE --from UNIT --to UNIT
unit-shift --list
unit-shift --help
```

Built with `argparse`, as a thin layer over the API:

- Output is `source = result` with canonical symbols, for example `10 km = 6.2137 mi`.
- Results go to standard output and errors to standard error, with the engine's message and no traceback.
- Exit codes: `0` success, `1` the conversion failed, `2` wrong usage (argparse's standard code).
- The command is installed as `unit-shift` through the package's entry point, and the package also runs with `python -m unit-shift`.
- Interactive mode, `--version` and a precision option are deferred.

## Graphical interface (planned)

A value field, two unit selectors, a result and an error label. The toolkit is still to be chosen. The selectors read their units from `list_units()`, so new units appear automatically. The GUI calls only the public API.

## Testing approach

| Level | What it covers |
|---|---|
| Unit tests | Each module on its own: errors, models, normalization, numbers, registry, resolver, converter, formatter |
| Data tests | The catalog is complete, every unit has its expected symbol and aliases, and factors match reference values written independently of the data |
| Conversion tests | Every ordered pair of units in each category against independently typed reference factors, and round trips for all pairs |
| Interface tests | The API and the CLI, including exit codes, output streams and a real subprocess run |
| Quality gates | 100% coverage, strict type checking, linting and formatting, all enforced in CI on Python 3.10 to 3.13 |

## Known limitations

- Only absolute temperatures are converted, not temperature differences.
- Input is plain text: symbols such as the degree sign are not accepted, and output symbols are plain (`C`, `F`, `K`, `cm3`).
- Two symbols that differ only by case cannot coexist.
- A negative number with an exponent must be written `-v=-1e3`, because argparse reads `-v -1e3` as an option.
- A result too large for a float becomes `inf` and is shown as such.
- Suggestions always list three unit names, even when nothing is close.
- Models are plain, mutable dataclasses, so nothing prevents code from changing a unit after the registry has validated it.
- Floating-point arithmetic leaves rounding noise around 1e-15, far below the display precision and the accuracy tolerance.
- The command name `convert` can clash with other programs of the same name, such as `convert.exe` on Windows and ImageMagick's `convert`.
