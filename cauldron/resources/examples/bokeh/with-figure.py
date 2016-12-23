import cauldron as cd
from bokeh.plotting import figure


plot = figure()
plot.line(x=[1, 2, 3], y=[3, 4, 5])
plot.scatter(x=[1, 2, 3], y=[3, 4, 5])

cd.display.bokeh(plot)
