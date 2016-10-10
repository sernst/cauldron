import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

import cauldron as cd

# Create data to plot
mu = 100
sigma = 15
x = mu + sigma * np.random.randn(10000)

cd.display.markdown(
   """
   # Plotting with PyPlot

   We created a normally-randomized data set centered at $$ @mu = {{ mu }} $$
   and with a standard deviation of $$ @sigma = {{ sigma }} $$.
   """,
   mu=mu,
   sigma=sigma
)


# the histogram of the data
n, bins, patches = plt.hist(x, 50, normed=1, facecolor='green', alpha=0.75)

# add a 'best fit' line
y = mlab.normpdf(bins, mu, sigma)
l = plt.plot(bins, y, 'r--', linewidth=1)

plt.xlabel('Smarts')
plt.ylabel('Probability')
plt.title(r'$\mathrm{Histogram\ of\ IQ:}\ \mu=100,\ \sigma=15$')
plt.axis([40, 160, 0, 0.03])
plt.grid(True)

cd.display.pyplot()
