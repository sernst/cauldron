import json
import cauldron as cd

with open('cauldron.json', 'r') as f:
    data = json.load(f)


cd.display.markdown(
    """
    {{ greeting }}

    _Markdown syntax_ is also supported. It comes with __Jinja2__ templating,
    which allows for more advanced templating than Python's built-in string
    formatting.

    {% for key, value in dictionary | dictsort %}
       * {{ key }}: {{ value }}
    {% endfor %}
    """,
    greeting='More Advanced Text',
    dictionary=data
)

