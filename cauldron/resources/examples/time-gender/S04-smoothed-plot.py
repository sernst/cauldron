import cauldron as cd
from cauldron import plotting

import plotly.graph_objs as go

df = cd.shared.df

cd.display.markdown(
    """
    ## Plot Smoothed Data

    Applying the smoothing function for a few different
    window sizes of 1, 2 and 4 we get plots that look
    like
    """
)

percentages = 100.0 * df['Female'] / df['Total']


def smooth_data(data, window_size):
    n = window_size
    out = []

    for i in range(n, len(data) - n):
        normalizer = 1 / (2 * n + 1)
        out.append(normalizer * sum(percentages[i - n:i + n]))

    for i in range(window_size):
        out.insert(0, out[0])
        out.append(out[-1])

    return out


cd.display.plotly(
    data=[
        go.Scatter(
            x=df['Year'],
            y=percentages,
            mode='lines+markers',
            name='raw'
        ),
        go.Scatter(
            x=df['Year'],
            y=smooth_data(percentages, 1),
            mode='lines+markers',
            name='Smoothed 1'
        ),
        go.Scatter(
            x=df['Year'],
            y=smooth_data(percentages, 2),
            mode='lines+markers',
            name='Smoothed 2'
        ),
        go.Scatter(
            x=df['Year'],
            y=smooth_data(percentages, 4),
            mode='lines+markers',
            name='Smoothed 4'
        )
    ],
    layout=plotting.create_layout(
        title='Female Time Covers',
        y_label='Percentage each Year (%)',
        x_label='Year'
    )
)

cd.shared.put(
  smooth_data=smooth_data
)
