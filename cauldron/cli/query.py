

def confirm(question: str, default: bool = True) -> bool:
    """
    Requests confirmation of the specified question and returns that result

    :param question:
        The question to print to the console for the confirmation
    :param default:
        The default value if the user hits enter without entering a value
    """

    result = input('{question} [{yes}/{no}]:'.format(
        question=question,
        yes='(Y)' if default else 'Y',
        no='N' if default else '(N)'
    ))

    if not result:
        return default

    if result[0].lower() in ['y', 't', '1']:
        return True
    return False


