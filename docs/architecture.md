# Architecture overview

This document describes how the unit converter is structured and why. Components are marked **implemented** or **planned**, so the document stays truthful as the project grows. Decision numbers (D12, D38, and so on) refer to the project's decision log.

## Design principles

1. **The engine knows nothing about the interface.** It takes plain values and strings and returns plain results or typed errors. It never prints or reads input.
2. **Units are data, not logic.** Adding a unit means adding one entry to a data module.
3. **One conversion path for everything**, including temperature, so there are no special cases to maintain.
4. **Errors are typed**, so each interface can present them in its own way.
5. **Dependencies point inward only.** Interfaces depend on the engine, never the other way round.

## Layers

```
┌────────────┐     ┌────────────┐
│ CLI layer  │     │ GUI layer  │          presentation only        (planned)
└─────┬──────┘     └─────┬──────┘
      └─────────┬────────┘
          ┌─────▼──────┐
          │ Public API │   builds the registry from the data,      (planned)
          └─────┬──────┘   exposes parse and convert
    ┌───────────┼──────────────┐
┌───▼────┐  ┌───▼─────┐  ┌─────▼─────┐
│Resolver│  │Converter│  │ Formatter │       engine                (planned)
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

The `data` package depends only on the engine's models. Nothing in the engine imports from `data`: the registry receives its categories as an argument, and the public API connects the two (D51). The `utils` package depends on nothing in the project.

## Project layout

```
src/unitconverter/
├── engine/
│   ├── models.py       # Unit, Category, Quantity
│   ├── errors.py       # exception hierarchy
│   └── registry.py     # validates and indexes unit data
├── data/               # one module per category, constants only
│   ├── length.py
│   ├── mass.py
│   ├── volume.py
│   ├── duration.py     # time units (named to avoid clashing with the stdlib "time")
│   └── temperature.py
├── utils/
│   └── normalize.py    # canonical form of a unit name
├── cli/                # planned
└── gui/                # planned
```

## Data model (implemented)

```
Unit:      id, name, symbol, factor, aliases, offset
Category:  name, base_unit_id, units
Quantity:  value, unit
```

All three are plain dataclasses (D35). `Unit` and `Category` take keyword arguments only.

Every unit is defined relative to its category's **base unit** (meter, kilogram, liter, second, kelvin):

```
base_value = value * factor + offset
value      = (base_value - offset) / factor
```

| Unit | Factor | Offset | Why |
|---|---|---|---|
| kilometer (base: meter) | 1000 | 0 | Pure scaling |
| Celsius (base: kelvin) | 1 | 273.15 | Shifted scale |
| Fahrenheit (base: kelvin) | 5/9 | 459.67 × 5/9 | Scaling and shift |

Temperature therefore needs no special code: linear units are simply the case where the offset is 0 (D13). Values are Python floats, and tests use a relative tolerance of 1e-6 (D17).

`Quantity` pairs a value with its unit, so a conversion result carries the canonical unit with it, and interfaces can show a symbol without a second lookup (D37). Equality compares value and unit, not physical size: one kilometer is not equal to 1000 meters as a `Quantity`.

## Unit data (implemented)

- One module per category, containing **constants only**: no functions and no branching (D14, D32).
- Factors come from official definitions, written as exact values or as visible expressions (for example the ounce as a pound divided by 16). Sources are cited in each module's docstring.
- Ids are lowercase, singular, `snake_case` (D49). Plurals and spelling variants are listed explicitly as aliases, never derived in code (D31).
- `data/__init__.py` gathers all categories into one tuple.
- Regionally ambiguous units (gallon, pint, fluid ounce, ton, cup, spoons) and variable-length units (month, year) are excluded on purpose (D19).

## Name normalization (implemented)

`utils/normalize.py` turns a name into a canonical form for matching: case-insensitive, with leading, trailing and repeated whitespace removed (D41, D42). Empty input gives an empty string (D40). It does not strip plurals, correct spelling or handle Unicode symbols: input is plain text.

## Registry (implemented)

The registry receives a list of categories, **validates everything in its constructor**, and builds its lookup tables once (D48). A half-built registry can never exist.

| Rule | Why |
|---|---|
| Category names are unique | One definition per category |
| Unit ids are unique across all categories | One definition per unit |
| Each category's base unit exists, with factor 1 and offset 0 | The anchor of the model |
| Every factor is positive and finite, every offset is finite | No division by zero or nonsense values |
| No name, symbol or alias is empty after normalization | An empty key can never match |
| A normalized name, symbol or alias belongs to exactly one unit, across all categories | No ambiguity at lookup time |

A name repeated inside one unit is ignored, because it is not ambiguous (D46). The name, symbol and aliases of a unit are all indexed under one rule (D43), which means symbols that differ only by case would collide, and the registry reports it at load time.

Public methods:

| Method | Returns |
|---|---|
| `find_unit(name)` | The unit matching a name, symbol or alias, or `None` |
| `category_of(unit)` | The unit's category, looked up by id. An unknown unit raises a `RegistryError` (D47) |
| `aliases()` | Every normalized lookup key, for "did you mean" suggestions |
| `categories` | All categories, in order |

The registry only looks things up. What a miss means (unknown unit, unsupported unit, suggestions) is decided by the resolver.

## Errors (implemented, with one planned addition)

```
ConverterError (base, shown to users)
├── InvalidNumberError       # the value cannot be read as a number
├── UnknownUnitError         # carries the name and suggestions
├── IncompatibleUnitsError   # carries both category names
└── UnsupportedUnitError     # planned: a known but unsupported unit, with a reason

RegistryError                # invalid unit data (a developer error)
```

- Interfaces catch `ConverterError` and show its message. They never parse message text: each error carries its data as attributes.
- `RegistryError` deliberately **does not** extend `ConverterError`: a bug in the data must not be hidden behind a friendly user-facing message (D45).
- Messages begin with the error's class name, for example "InvalidNumberError: 'abc' is not a valid number." (D33). This is a deliberate choice, made for logs and bug reports.

## Conversion flow (planned)

Conversion is a plain function that takes the registry as an argument, instead of a method on `Quantity`. A `Unit` does not know its category, only the registry does, and a function keeps the models free of hidden dependencies (D38).

```
function parse(value_text, unit_name, registry) -> Quantity
    number = parse_number(value_text)           # InvalidNumberError
    unit   = resolve(unit_name, registry)       # UnknownUnitError, UnsupportedUnitError
    return Quantity(number, unit)

function convert(quantity, target_unit, registry) -> Quantity
    if registry.category_of(quantity.unit) != registry.category_of(target_unit):
        raise IncompatibleUnitsError
    base   = quantity.value * quantity.unit.factor + quantity.unit.offset
    result = (base - target_unit.offset) / target_unit.factor
    return Quantity(result, target_unit)
```

The resolver looks a name up in the registry, and on a miss checks a known-unsupported list, then offers suggestions (unit names, without duplicates, found with the standard library's fuzzy matching, D16).

## Output formatting (planned)

A pure function with a precision parameter:

```
function format(x):
    if x == 0: return "0"
    if abs(x) >= 1e6 or abs(x) < 1e-4: return scientific notation, 4 significant figures
    return x rounded to 4 decimal places, trailing zeros removed
```

The engine returns full precision. The interface decides how to display it.

## Interfaces (planned)

- **Command line:** parse arguments, call the public API, format, print. Errors become messages with a non-zero exit code.
- **GUI:** a value field, two unit selectors, a result and an error label. The toolkit is still to be chosen. The selectors read their units from the registry, so new units appear automatically.

Both layers call only the public API.

## Testing approach

| Level | What it covers |
|---|---|
| Unit tests | Each module on its own: errors, models, normalization, registry |
| Data tests | The catalog is complete, every unit has its expected symbol and aliases, and factors match reference values written independently of the data |
| Round-trip and pair tests | Planned with the converter: every unit converts to every other unit in its category, and A to B to A returns the original value |
| Edge and error tests | Empty input, invalid numbers, unknown and unsupported units, cross-category conversions |
| Quality gates | 90% coverage, strict type checking, linting and formatting, all enforced in CI |

## Known limitations

- Only absolute temperatures are converted, not temperature differences.
- Input is plain text: symbols such as the degree sign are not accepted, and output symbols are plain (`C`, `F`, `K`, `cm3`).
- Two symbols that differ only by case cannot coexist.
- Models are plain, mutable dataclasses (D35), so nothing prevents code from changing a unit after the registry has validated it.
- Floating-point arithmetic leaves rounding noise around 1e-15, far below the display precision and the accuracy tolerance.

## Summary of key decisions

| Decision | Reference |
|---|---|
| Layered, interface-independent engine | D12 |
| One factor and offset model for all units | D13 |
| Unit data as validated Python modules | D14, D32 |
| Standard-library fuzzy matching, floats, `src/` layout | D16, D17, D18 |
| Ambiguous units excluded | D19 |
| Explicit plural aliases | D31 |
| Plain dataclasses, `Quantity`, function-based conversion | D35, D37, D38 |
| Simple normalization in `utils/` | D41, D42 |
| One lookup rule, no `system` field | D43, D44 |
| `RegistryError` outside the user-facing hierarchy | D45 |
| Unit ids, module names, registry built by the public API | D49, D50, D51 |
| CI on Python 3.10 to 3.13 | D52 |
