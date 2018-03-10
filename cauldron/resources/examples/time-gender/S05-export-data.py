import cauldron as cd

df = cd.shared.df

percentages = df['Female'] / df['Total']
smoothed = cd.shared.smooth_data(percentages, 4)

normalized = [s - min(smoothed) for s in smoothed]
normalized = [n / max(normalized) for n in normalized]

cd.display.json(percentages=normalized)

cd.display.markdown(
    """
    ## HTML &amp; JavaScript
    
    Cauldron is capable of working directly with HTML and JavaScript.
    This is useful if you want to create custom displays. In this example
    we'll create a custom graphic for the data above using D3 directly
    from JavaScript.
    
    First we need to save some data from Python into our notebook page so
    that JavaScript has access to it. To do that we use the JSON display
    function:
    
    ``
    cd.display.json(data=my_data)
    ``
    
    where we set a key and a value. In this case we map the key "data" to the
    the variable "my_data". It is important to understand that this data 
    is going to be serialized in JavaScript, which requires mapping only
    data types that JSON serialization supports.
    """
)