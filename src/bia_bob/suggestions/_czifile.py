def suggestions():
    return """
    ### Working with CZI files using czifile
    
     * Loading files ending with `.czi` works like this:
    ```
    import czifile
    from pathlib import Path
    image = czifile.imread(Path(filename))
    ```
    """