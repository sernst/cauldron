import numpy as np
import pandas as pd
import cauldron as cd

df = pd.DataFrame(
    np.random.randn(10, 5),
    columns=['a', 'b', 'c', 'd', 'e']
)

cd.display.header('Random Data Frame:')
cd.display.markdown(
    """
    We've created a random data frame with

     * Shape: [{{ x }}, {{ y}}]
     * Column Names: {{ columns }}

    It looks like:
    """,
    x=df.shape[0],
    y=df.shape[1],
    columns=', '.join(df.columns.tolist())
)

cd.display.table(df)

print('We store the DataFrame in shared variables for use by other steps.')
cd.shared.df = df
