import cauldron as cd

with open('lorem_ipsum.txt', 'r') as f:
    text = f.read()

cd.display.header('HTML Headers with different levels')

cd.display.header('First 5 Lines with head()', 2)
cd.display.head(text)

cd.display.header('Last 5 Lines with tail()', 2)
cd.display.tail(text)

cd.shared.lorem_ipsum = text
