'''
under construction

dictOfLanes.npz format:
```
{'camid': {'<starts from 1>': {'polygon': <binary mask>, 'description': '<lane description>'}}}
```
'''
import numpy as np
import matplotlib.pyplot as plt

polygons = np.load('dictOfLanes.npz', allow_pickle=True)
dictOfLanes = polygons.get('arr_0')

print(dictOfLanes)