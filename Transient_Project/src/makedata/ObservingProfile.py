"""
Class to encode the observing profile as well
as detection thresholds
"""

import numpy as np
import copy

class ObservingProfile:
    """
    """
    def __init__(self, viewingField, viewingFieldArgs,
                 extraObstruction, extraObstructionArgs,
                 holisticDetection, holisticDetectionArgs,
                 surveyNoiseFunction, surveyNoiseFunctionArgs):
        """
        Args:
            viewingField:
                Function. Returns a list of events that are 
                potentially observable because the "telescope"
                is pointed at them. This selection should
                be orthogonal to extraObservation
                    Args: 
                        Time: the time in frames since the 
                        start of the survey

                        Events: the list of events that exist
            extraObstruction:
                Function. Returns a list of events that are
                potentially observable because they are not 
                obstructed by anything. This selection
                should be orthogonal to viewingField
                    Args: 
                        Time: the time in frames since the 
                        start of the survey

                        Events: the list of events that exist

            holisticDetection:
                Function. Takes in a single event (generally dead ones,
                but not necessarily) and detirmines if they are "detected"
                If they are, returns True
                    Args:
                        Event:
                            event to be tested
            surveyNoiseFunction:
                Function that generates noise on the events
                    to simulate ambient sky noise
                    takes as args: event
                    returns noise to be added to lum

            
                        
        """
        self.view = viewingField
        self.vArgs = viewingFieldArgs
        self.obstruct = extraObstruction
        self.oArgs = extraObstructionArgs
        self.holistic = holisticDetection
        self.hArgs = holisticDetectionArgs
        self.surveyNoise = surveyNoiseFunction
        self.sArgs = surveyNoiseFunctionArgs

    def frameDetect(self, time, events):
        """Mark events that are viewed and unobstructed
        """
        frameDetected = self.obstruct(time, 
                                      self.view(time, events))
        for event in frameDetected:
            event.recordDetection(self.surveyNoise(event, 
                                                   *self.sArgs))

    def holisticDetect(self, events):
        """Mark events that are detected overall
        """
        for event in events:
            if self.holistic(event):
                event.holisticDetection = True
    