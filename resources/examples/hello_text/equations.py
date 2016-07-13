import cauldron as cd

cd.display.header('Latex Equation Support')
cd.display.latex('e = m * c^2')

cd.display.markdown(
    """
    Latex equations can also be included within markdown blocks. The equations
    can be inline, $$ 2^2 = 4 $$, by wrapping the equation in double $, or
    they can be separate lines with triple $ like:

    $$$
        test = @frac { @sqrt{ x_1^2 + x_2^2 } } { N }
    $$$

    Most of latex math mode is supported. However, the latex backslash
    character has been replaced by the ampersand, @, character because
    backslashes are escape characters in Markdown and Python strings.
    """
)


