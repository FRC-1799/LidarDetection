#!/usr/bin/env python3
'''Animates distances and measurement quality with hitboxes and quadrant tracking.'''

from lidarLib.lidarMeasurment import lidarMeasurement
from lidarLib.Lidar import Lidar
import matplotlib.pyplot as plot
import numpy as np
import time
from lidarLib.translation import translation
from renderLib.renderMachine import initMachine
from sklearn.cluster import DBSCAN  # For clustering points into hitboxes
import matplotlib.patches as patches

PORT_NAME = '/dev/LidarFL'
DMAX = 1600
IMIN = 20
IMAX = 20

def cluster_points(points, eps=50, min_samples=5):
    """Cluster points into hitboxes using DBSCAN."""
    if len(points) == 0:
        return {}

    # Extract coordinates from points
    coordinates = np.array([(p.x, p.y) for p in points])

    # Perform DBSCAN clustering
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(coordinates)

    # Group points by cluster labels
    clusters = {}
    for label, point in zip(clustering.labels_, points):
        if label == -1:  # Noise points
            continue
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(point)

    return clusters

def determine_quadrants(points):
    """Determine which quadrants contain points."""
    quadrants = {"Q1": False, "Q2": False, "Q3": False, "Q4": False}
    
    for p in points:
        if p.x >= 0 and p.y >= 0:
            quadrants["Q1"] = True
        elif p.x < 0 and p.y >= 0:
            quadrants["Q2"] = True
        elif p.x < 0 and p.y < 0:
            quadrants["Q3"] = True
        elif p.x >= 0 and p.y < 0:
            quadrants["Q4"] = True
    
    return quadrants

def draw_hitboxes(ax, clusters):
    """Draw rectangular hitboxes around clusters."""
    for cluster in clusters.values():
        # Extract cluster bounds
        x_coords = [p.x for p in cluster]
        y_coords = [p.y for p in cluster]
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)

        # Add a rectangle to the plot
        rect = patches.Rectangle((min_x, min_y), max_x - min_x, max_y - min_y,
                                 linewidth=1, edgecolor='r', facecolor='none')
        ax.add_patch(rect)

def run():
    lidar = Lidar(debugMode=True, deadband=None)
    lidar.connect(port=PORT_NAME, baudrate=256000, timeout=3)
    lidar.setMotorPwm(1000)

    lidar.getScanModes()
    print(lidar.getSampleRate())
    print(lidar.getScanModeTypical())

    lidar.startScan()
    time.sleep(2)

    # axis = subplot.scatter([0, 1], [100, 2000], s=1, c=[IMIN, IMAX],
    #                        cmap=plot.cm.Greys_r, lw=0)
    
    #lidar.setCurrentLocalTranslation(translation(0,0, 180))
    time.sleep(1)
    #lidar.currentMap.printMap()
    #print(lidar.currentMap.points)
    #lidar.currentMap.thisFuncDoesNothing()
    renderer, pipe = initMachine()

    try:
        fig, ax = plot.subplots()
        while True:
            # Get the latest map data
            current_map = lidar.lastMap
            points = current_map.points

            # Cluster points into hitboxes
            clusters = cluster_points(points)
            quadrants = determine_quadrants(points)

            # Print quadrant occupancy
            print("Quadrant Status:", quadrants)

            # Clear the plot and redraw
            ax.clear()
            ax.scatter([p.x for p in points], [p.y for p in points], s=1, c='blue')
            draw_hitboxes(ax, clusters)

            plot.pause(0.1)  # Update plot

            pipe.send(current_map)  # Send map data to renderer
            time.sleep(0.1)

    except Exception as e:
        print(e)

    lidar.stop()
    lidar.disconnect()

    print("The run is done")

if __name__ == '__main__':
    run()