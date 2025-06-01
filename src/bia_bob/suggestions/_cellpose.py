"""
Suggestions for using Cellpose for image segmentation.

This module provides suggestions on how to utilize Cellpose 
for image segmentation tasks, with examples for versions 
less than 4.0.0 and version 4.0.0 and above.

Examples
--------

# For Cellpose versions < 4.0.0
Examples for usage can be obtained from:
https://github.com/haesleinhuepf/BioImageAnalysisNotebooks/blob/main/docs/20b_deep_learning/cellpose.ipynb

# For Cellpose versions >= 4.0.0
Refer to:
https://github.com/haesleinhuepf/BioImageAnalysisNotebooks/blob/main/docs/20b_deep_learning/cellpose-sam.ipynb
"""

import importlib

def suggest_cellpose_usage():
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
    try:
        cellpose = importlib.import_module('cellpose')
        version = tuple(map(int, cellpose.__version__.split('.')))
        if version < (4, 0, 0):
            return ("For Cellpose version < 4.0.0, please refer to the following examples: "
                    "https://github.com/haesleinhuepf/BioImageAnalysisNotebooks/blob/main/docs/20b_deep_learning/cellpose.ipynb")
        else:
            return ("For Cellpose version >= 4.0.0, please check: "
                    "https://github.com/haesleinhuepf/BioImageAnalysisNotebooks/blob/main/docs/20b_deep_learning/cellpose-sam.ipynb")
    except ModuleNotFoundError:
        return ""
