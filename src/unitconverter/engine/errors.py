class ConverterError(Exception):
    """Base class for every error raised by the conversion engine.

    Interfaces (CLI, GUI) can catch this one type to handle all converter
    errors in a single place, then show ``message`` to the user.
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class InvalidNumberError(ConverterError):
    """Raised when the value to convert cannot be read as a finite number.

    The offending input is kept in ``value`` so interfaces never need to
    parse the message text.
    """

    def __init__(self, value: object = None) -> None:
        self.value = value

        message = "InvalidNumberError"

        # If possible, specify which data is in fault.
        if value is not None:
            message += f": '{value}' is not a valid number"

        super().__init__(message + ".")


class UnknownUnitError(ConverterError):
    """Raised when a unit name matches no unit known to the registry.

    ``name`` is the text the user typed. ``suggestions`` holds the closest
    known names (possibly none), so interfaces can present them their own way.
    """

    def __init__(
        self, name: None | str = None, suggestions: None | list[str] = None
    ) -> None:
        self.name = name
        # Make suggestions immutable.
        if suggestions:
            self.suggestions = tuple(suggestions)
        else:
            self.suggestions = ()

        message = "UnknownUnitError"

        # If possible, specify which unit is not recognized and give suggestions.
        if name is not None:
            message += f": unknown unit '{name}'."

            # Add suggestions if provided.
            if suggestions is not None:
                options = ", ".join(
                    f"'{suggestion}'" for suggestion in self.suggestions
                )
                message += f" Did you mean {options}?"
        else:
            message += "."

        super().__init__(message)


class IncompatibleUnitsError(ConverterError):
    """Raised when two units belong to different categories.

    Both category names are kept so interfaces never need to parse the
    message text.
    """

    def __init__(
        self, from_category: None | str = None, to_category: None | str = None
    ) -> None:
        self.from_category = from_category
        self.to_category = to_category

        message = "IncompatibleUnitsError"

        # If possible, specify which type of conversion is in fault.
        if (from_category is not None) and (to_category is not None):
            message += f": cannot convert from '{from_category}' to '{to_category}'"

        super().__init__(message + ".")


class RegistryError(Exception):
    """Raised when unit data is invalid (a developer error, not a user error)."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        self.message = f"RegistryError: {detail}"
        super().__init__(self.message)
