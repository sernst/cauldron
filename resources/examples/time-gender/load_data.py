import pandas as pd
import plotly.graph_objs as go

from cauldron import plotting
from cauldron import project

df = pd.read_csv('TIME_Gender_Ratio.csv')
# project.display.text(str(df.head()), preformatted=True)

project.display.table(df, scale=0.5)

data = go.Scatter(
    x=df['Year'],
    y=100.0 * df['Female'] / df['Total'],
    mode='lines+markers'
)

project.display.plotly(
    data=data,
    layout=plotting.create_layout(
        title='Female Time Covers',
        y_label='Percentage each Year (%)',
        x_label='Year'
    )
)

project.shared.df = df
