import cauldron as cd
import pandas as pd

is_testing = cd.mode.is_test()
is_interactive = cd.mode.is_interactive()
is_single_run = cd.mode.is_single_run()


df = pd.DataFrame({
    'a': [1, 2, 3],
    'b': [True, False, True],
    'c': ['Hello', 'World', 'Foo'],
    'd': [3, None, 5]
})

df = df.fillna(4)


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

