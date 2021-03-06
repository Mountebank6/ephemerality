"""
Class to hold an individual event

"""

import numpy as np
import copy

def zeroFunction(lum=0, loc=0, lifetime=0):
    return 0.0

class TransientEvent:
    """
    """
    def __init__(self, birthLoc, lifetime, classID, 
                 noiseFunction = zeroFunction, noiseExtraArgs = [],
                 luminositySeries = None, movementFunction = None, 
                 velocityFunction = None):
        """
        Arguments:
            birthloc: length 5 list. Positions:
                0: birth time
                1: birth x-location
                2: birth y-location
                3: x-velocity
                4: y-velocity                
            lifetime: float. Number of frames
            luminositySeries: Iterable of luminosities as fractions of 
                maximum reportable luminosity. The ith entry in the
                iterable represents the luminosity on the ith frame
                of its existance
                The individual luminosities do not necessarily have to
                be floats. They could be any object as long as
                noiseFunction interacts nicely with them
            noiseFunction:
                function that adds noise to even luminosity
                Arguments (in this order):
                    lum, loc, lifetime, *noiseExtraArgs
            noiseExtraArgs:
                This is for other arguments that the noise function
                may require. 
            velocityFunction:
                
                Args: 
                    timeSinceBirth: simulation ticks since event spawn
                Returns:
                    Velocity to use for next time step format (xvel, yvel)
            movementFunction:
                OVERRIDES VELOCITY FUNCTION IF DEFINED
                Args: 
                    timeSinceBirth: simulation ticks since event spawn
                Returns:
                    position to use for next time step format (x, y)
            
        """
        self.classID = classID
        self.loc = birthLoc
        self.time = birthLoc[0]
        self.x = birthLoc[1]
        self.y = birthLoc[2]
        self.xdot = birthLoc[3]
        self.ydot = birthLoc[4]
        self.nArgs = noiseExtraArgs
        self.history = [[self.time,self.x,self.y,self.xdot,self.ydot]]
        self.detectionHistory = []
        self.lifetime = int(lifetime)
        self.noiseFunc = noiseFunction
        self.movementFunction = movementFunction
        self.velocityFunction = velocityFunction
        if luminositySeries is None:
            self.lum = 1 + self.noiseFunc(
                                1, self.loc, self.lifetime,
                                *self.nArgs         
                                         )
            self.luminositySeries = [1]
            self.history[0] += [1]
        else:
            self.luminositySeries = luminositySeries
            self.lum = (self.luminositySeries[0]  
                            + self.noiseFunc(
                                        self.luminositySeries[0], 
                                        self.loc, 
                                        self.lifetime,
                                        *self.nArgs))
            self.history[0] += [self.lum]
        self.markedForDeath = False
        self.eventID = np.random.randint(2**64, dtype = np.uint64)
        self.holisticDetection = False
        if self.loc[0] - self.history[0][0] + 1 >= self.lifetime:
            self.markedForDeath = True
        
    
    def advanceEvent(self):
        """Advance the event simulation by one tick"""
        if not self.markedForDeath:
            self.loc[0] += 1
            timeSinceBirth = self.loc[0] - self.history[0][0]
            if self.velocityFunction is not None:
                self.loc[3], self.loc[4] = self.velocityFunction(timeSinceBirth)
            self.loc[1] += self.loc[3]
            self.loc[2] += self.loc[4]
            
            if self.movementFunction is not None:
                self.loc[1], self.loc[2] = self.movementFunction(timeSinceBirth)
            [self.time,self.x,self.y,self.xdot,self.ydot] = self.loc

            self.lum = (self.luminositySeries[
                                timeSinceBirth % len(self.luminositySeries)
                                             ])
            self.lum += self.noiseFunc(
                                self.lum, 
                                self.loc, 
                                self.lifetime,
                                *self.nArgs)
            self.history.append(
                                [self.time,self.x,self.y,self.xdot,self.ydot] 
                            + [self.lum])
            
            #The +1 here accounts for timesincebirth being 1 fewer
            #than the number of frames the event has been alive
            if timeSinceBirth + 1 >= self.lifetime:
                self.markedForDeath = True
    
    def recordDetection(self, index, noise):
        """Record the time of detection, and the relevant luminosity 
        
        Args:
            index:
                The index in self.history corresponding to
                    the detection.
            noise:
                Noise to be added to luminosity. Represents noise
                    in the detector, not noise in the event's luminosity
        """
        i = index
        time = self.history[i][0]
        pos = (self.history[i][1], self.history[i][2])
        lum = self.history[i][5]
        self.detectionHistory.append([time, index, pos, lum, noise])

    def clearDetectionHistory(self):
        """Empty detectionHistory and remove holistic detection"""
        self.holisticDetection = False
        self.detectionHistory = []

