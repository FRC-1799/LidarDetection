from multiprocessing.connection import Connection
import matplotlib.pyplot as plot
from matplotlib.axis import Axis
import matplotlib.animation as animation
import numpy as np
from multiprocessing import Process, Pipe
from renderLib.renderPipeCap import renderPipeCap

DMAX=4000

def updateLine(num, pipe:renderPipeCap, subplot:Axis)->Axis:
    """
        updates the subplot using data gained from the pipe
        pipe should be the read end of a renderPipe cap thats partner is consistently supplied with up to date lidar maps
        subplot should be a axis value that is tied to a plot being updated by an animation(with this or a exetention of this as its active function)
        num is an placeholder argument that is automaticly suplied by animation but never used
    """

    subplot.clear()
    scan = pipe._get()
    #print(scan.mapID)
    if scan == None:
        return
    scan=scan.getPoints()
    angles=np.array([point.angle for point in scan])
    distances=np.array([point.distance for point in scan])
    #offsets = np.array([[point.angle, point.distance] for point in scan])
    #offsets=[scan[0].angle, scan[0].distance]
    #subplot.set_offsets(offsets)
    intens = np.array([1 for point in scan])
    #subplot.set_array(intens)
    print("render cycle", len(intens))
    return subplot.scatter(angles*3.14/180, distances, s=10, c=intens, cmap=plot.cm.Greys_r, lw=0),


def renderMachine(pipeCap:renderPipeCap)->None:
    """
        Initalizes a render and animation and displays it. 
        For preformance reasons this function should be set up on its own process(automaticly done in the initMachine function) so its slowness can not effect the data gatherers
        Pipe should be the read end of a renderPipe cap thats partner is consistently supplied with up to date lidar maps
    """
    fig = plot.figure()
    subplot = plot.subplot(111, projection='polar')
    subplot.set_rmax(DMAX)
    subplot.grid(True)
    
    anim=animation.FuncAnimation(fig, updateLine, blit=False,
    fargs=(pipeCap, subplot), interval=50, save_count=50)
    
    plot.show()
    
    


def initMachine()->tuple[Process, Connection]:
    """
        Creates a seperate prosses that handles all rendering and can be updated via a pipe(connection)
        returns a tuple with the first argument being the process, this can be use cancle the process but the primary use is to be saved so the renderer doesnt get collected
        the second argument is one end of a pipe that is used to update the render engine. this pipe should be passed new lidar maps periodicly so they can be rendered. 
        WARNING all code that deals with the pipe should be surrounded by a try except block as the pipe will start to throw errors whenever the user closes the render machine.
    """
    returnPipe, machinePipe = Pipe(duplex=True)
    returnPipe=renderPipeCap(returnPipe)
    machinePipe=renderPipeCap(machinePipe)
    process= Process(target=renderMachine, args=(machinePipe,))
    process.start()


    return process, returnPipe

    