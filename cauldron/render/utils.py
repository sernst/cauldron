html_escapes = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
}


def html_escape(text: str) -> str:
    """

    :param text:
    :return:
    """

    for k, v in html_escapes.items():
        text = text.replace(k, v)

    return text
