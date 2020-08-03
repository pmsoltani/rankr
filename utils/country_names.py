def country_names(name: str) -> str:
    """Changes the name of some countries to pre-defined values

    Parameters:
        name (str): the name of the country to be inspected

    Returns:
        str: the new name of the country
    """

    countries = {
        "Russian Federation": "Russia",
        "USA": "United States",
        "Great Britain": "United Kingdom",
        "Vietnam": "Viet Nam",
        "Zweden": "Sweden",
        "Czech Republic": "Czechia",
    }
    try:
        return countries[name]
    except KeyError:
        return name
