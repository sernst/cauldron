import matplotlib.pyplot as plt
import cauldron as cd

df = cd.shared.df

for column_name in df.columns:
    plt.plot(df[column_name])

plt.title('Random Plot')
plt.xlabel('Indexes')
plt.ylabel('Values')

cd.display.pyplot()
