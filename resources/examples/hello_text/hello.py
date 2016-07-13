import cauldron as cd

cd.display.text('You can add text')

cd.display.text(
    """
    You can also
    add text that
    preserves formatting
    by setting the

        "preformatted"

    argument to true
    """,
    preformatted=True
)

print(
    """
    The print() function works just like it normally does, and adds
    preformatted text. However, you can add more than just text:
    """,
    21 * 2,
    cd
)

