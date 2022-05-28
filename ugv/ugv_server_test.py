import requests
import numpy as np
from scipy.spatial import ConvexHull, convex_hull_plot_2d
# response = requests.get('http://localhost:3000/ugv/state')
# print(response.text)
# print(response.json()["state"])
# requests.post('http://localhost:3000/ugv/state', json= {"state": "DETACHED"})
# response = requests.get('http://localhost:3000/ugv/state')
# print(response.text)
response = requests.get('http://localhost:3000/ugv/mission/')
print(response.json())
drop_location_data = response.json()['airDropBoundaryPoints']
drop_location_data_array = np.empty((len(drop_location_data)+1, 2))
for i in range(len(drop_location_data)):
    drop_location_data_array[i] = np.array([drop_location_data[i]['latitude'], drop_location_data[i]['longitude']])
drop_location_data_array[len(drop_location_data)] = drop_location_data_array[0]

current_location = [38.14616667, -76.4263, 0, 0]
def point_in_bounds(bounds, current_location):
    in_bounds = True
    for i in range(bounds.shape[0]-1):
        D = (bounds[i+1][0]-bounds[i][0])*(current_location[1]-bounds[i][1]) 
        - (current_location[0]-bounds[i][0])*(bounds[i+1][1]-bounds[i][1])
        if D < 0:
            in_bounds = False
    return in_bounds

print(drop_location_data_array)
if point_in_bounds(drop_location_data_array, current_location):
    print("in bounds")
else:
    print("not in bounds")

hull = ConvexHull(drop_location_data_array)
import matplotlib.pyplot as plt
plt.plot(drop_location_data_array[:,0], drop_location_data_array[:,1], 'o')
plt.plot(current_location[0], current_location[1], 'o')
for simplex in hull.simplices:
    plt.plot(drop_location_data_array[simplex, 0], drop_location_data_array[simplex, 1], 'k-')
plt.show()
#data = json.loads(response.json())
#print(response.json()['airDropBoundaryPoints'][0])