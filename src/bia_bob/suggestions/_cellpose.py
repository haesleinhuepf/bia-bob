def suggestions():
    """
    Provides suggestions based on the installed Cellpose version.

    Returns
    -------
    str
        Suggestions or further instructions based on the version.
    
    Examples
    --------
    >>> suggest_cellpose_usage()
    'Refer to older Cellpose examples...'
    """
    import importlib.metadata

    try:
        version = int(importlib.metadata.version("cellpose")[0])
        if version < 4:
            return """
### Segmentation with Cellpose

```python
from cellpose import models

model = models.Cellpose(gpu=False, model_type='nuclei')
channels = [0,0] # This means we are processing single-channel greyscale images.
masks, flows, styles, diams = model.eval(image, diameter=None, channels=channels)
label_image = masks.astype(np.uint32)
```

Set the model_type above to the appropriate model for your task, e.g. `nuclei` for nuclei segmentation and `cyto2` for cytoplasm/cell segmentation.

"""
        else:
            return """
### Segmentation with Cellpose

```python            
from cellpose import models

model = models.CellposeModel(gpu=False)
masks, flows, styles = model.eval(image, 
                                  batch_size=32, 
                                  flow_threshold=0.4, 
                                  cellprob_threshold=0.0,
                                  normalize={"tile_norm_blocksize": 0})
label_image = masks.astype(np.uint32)
```

"""
    except ModuleNotFoundError:
        return ""
