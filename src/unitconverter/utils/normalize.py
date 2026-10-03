"""Normalization of unit names, so that equivalent spellings compare equal."""


def normalize(name: str) -> str:
    """Return a canonical form of a unit name for matching.

    The result is case-insensitive and has leading, trailing and repeated
    whitespace removed. It does not remove plural endings or fix spelling:
    variants are listed explicitly as aliases in the unit data.

    Empty or whitespace-only input returns an empty string.
    """
    return " ".join(name.casefold().split())
