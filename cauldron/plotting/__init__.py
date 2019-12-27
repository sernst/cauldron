from cauldron.plotting._colors import Palettes  # noqa
from cauldron.plotting._colors import get_color  # noqa
from cauldron.plotting._colors import get_gray_color  # noqa
from cauldron.plotting._definitions import ColorPalette  # noqa
from cauldron.plotting._helpers import create_layout  # noqa
from cauldron.plotting._helpers import make_line_data  # noqa

#: This exists for backward compatibility when there was only
#: one color palette available (<= v1.0.0). For newer use-cases
#: the Palettes enumeration class should be used instead.
PLOT_COLOR_PALETTE = Palettes.categorical_10.value.colors
