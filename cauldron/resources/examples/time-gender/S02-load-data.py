import cauldron as cd
import pandas as pd

cd.display.markdown(
    """
    ## Load CSV Data

    In this step we load the time gender CSV data
    and display it using the table display function
    as follows:

    ```
    cd.display.table(df)
    ```

    We're passing in the Pandas DataFrame that was
    returned from the *read_csv* function.
    """
)

df = pd.read_csv('TIME_Gender_Ratio.csv')

cd.display.table(df, scale=0.5)

cd.shared.df = df
