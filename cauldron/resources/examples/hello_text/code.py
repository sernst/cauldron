import cauldron as cd

cd.display.markdown(
    """
    # Syntax Highlight Code Blocks

    Code can also be added to the notebook with syntax highlighting like so:
    """
)

cd.display.code_block(
    """
    import cauldron as cd
    cd.display.code_block(
        code='print("Hello World!")',
        language='py3'
    )
    """,
    language_id='py3',
)

cd.display.markdown(
    """
    Code can also be included from a file using the same display command,
    but specifying a path instead of the code as a string:
    """
)

cd.display.code_block(
    """
    import cauldron as cd
    cd.display.code_block(path='cauldron.json')
    """,
    language_id='py3',
)

cd.display.markdown(
    """
    which would produce the following result:
    """
)

cd.display.code_block(path='cauldron.json')
