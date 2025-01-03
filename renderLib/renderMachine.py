from multiprocessing.connection import Connection
import matplotlib.pyplot as plot
import matplotlib.animation as animation
import numpy as np
from multiprocessing import Process, Pipe
from renderLib.renderPipeCap import renderPipeCap

DMAX=4000

def update_line(num, pipe:renderPipeCap, subplot:plot.axis)->plot.axis:
    subplot.clear()
    scan = pipe.get()
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


def renderMachine(pipeCap:renderPipeCap)->none:
    
    fig = plot.figure()
    subplot = plot.subplot(111, projection='polar')
    subplot.set_rmax(DMAX)
    subplot.grid(True)
    
    anim=animation.FuncAnimation(fig, update_line, blit=False,
    fargs=(pipeCap, subplot), interval=50, save_count=50)
    
    plot.show()
    
    


def initMachine()->tuple[Process, Connection]:
    returnPipe, machinePipe = Pipe(duplex=True)
    returnPipe=renderPipeCap(returnPipe)
    machinePipe=renderPipeCap(machinePipe)
    process= Process(target=renderMachine, args=(machinePipe,))
    process.start()


    return process, returnPipe

    