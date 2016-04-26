import pandas as pd

from cauldron import project

df = pd.read_csv('TIME_Gender_Ratio.csv')
project.display.text(str(df.head()), preformatted=True)
project.display.table(df, scale=0.5)
