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
dictOfLanes = polygons.get('arr_0').item()

print(dictOfLanes)
x=134
y=155

# Example: test centroid for car lane
camid = 'H210F'
testForLane = [dictOfLanes[camid][i]['polygon'][y,x] for i in dictOfLanes[camid]]
print(testForLane, np.argmax(testForLane)+1)