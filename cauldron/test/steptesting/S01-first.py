import cauldron as cd
import pandas as pd

df = pd.DataFrame({
    'a': [1, 2, 3],
    'b': [True, False, True],
    'c': ['Hello', 'World', 'Foo']
})


def to_strings(values):
    return ['{}'.format(value) for value in values]


def create_unified_column(data_frame: pd.DataFrame) -> pd.Series:
    unified = [
        '-'.join(to_strings(row.to_dict().values()))
        for _, row in data_frame.iterrows()
    ]

    return pd.Series(unified)

df['d'] = create_unified_column(df)

cd.shared.df = df
