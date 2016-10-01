import cauldron as cd
from cauldron import plotting

import plotly.graph_objs as go


df = cd.shared.df

cd.display.markdown(
    """
    ## Plot Data

    Now we're going to plot the loaded data to get an
    idea for what it looks like. For this notebook,
    we're going to use the Plotly plotting library.
    """
)

cd.display.plotly(
    data=go.Scatter(
        x=df['Year'],
        y=100.0 * df['Female'] / df['Total'],
        mode='lines+markers'
    ),
    layout=plotting.create_layout(
        title='Female Time Covers',
        y_label='Percentage each Year (%)',
        x_label='Year'
    )
)

cd.display.markdown(
    """
    Immediately apparent from this plot is that the
    data has high-frequency variations. We want to get
    a better sense of the trend. To do that we'll use
    a running-window smoothing operator that looks like:

    $$$
        X_i = @frac{1}{2N + 1} @sum_{@delta=-N}^N x_{@delta}
    $$$

    where $$N$$ is the window size.
    """
)
