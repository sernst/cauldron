html_escapes = [
    ("&", "&amp;"),
    ('"', "&quot;"),
    ("'", "&apos;"),
    (">", "&gt;"),
    ("<", "&lt;"),
]


def html_escape(text: str) -> str:
    """

    :param text:
    :return:
    """

    for k, v in html_escapes:
        text = text.replace(k, v)

    return text


def format_latex(source: str) -> str:
    """

    :param source:
    :return:
    """

    source = [line.strip() for line in source.strip().split('\n')]
    return ' '.join(source).replace('\\', '\\\\')
