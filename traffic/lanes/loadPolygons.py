'''
under construction

dictOfLanes.npz format:
```
{'camid': {'<starts from 1>': {'polygon': <binary mask>, 'description': '<lane description>'}}}
```
'''
import numpy as np

masks = np.load('dictOfLanes.npz')