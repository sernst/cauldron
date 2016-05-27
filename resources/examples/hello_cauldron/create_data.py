import numpy as np
import pandas as pd
import cauldron as cd

df = pd.DataFrame(
    np.random.randn(10, 5),
    columns=['a', 'b', 'c', 'd', 'e']
)

cd.display.header('Random Data Frame:')
cd.display.table(df)

cd.shared.df = df
