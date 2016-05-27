import cauldron as cd

# Adding text
cd.display.text('Hello World')

# Adding preformatted text
cd.display.text(
    """
    * Hello
    * World
    """,
    preformatted=True
)

# You can also use the print() function to add preformatted text
print(
    """
    Hello World
    with the print() function
    """
)
