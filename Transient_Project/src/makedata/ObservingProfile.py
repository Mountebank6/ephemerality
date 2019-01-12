"""
Class to encode the observing profile as well
as detection thresholds
"""

import numpy as np
import copy

class ObservingProfile:
    """
    """
    def __init__(self, 
                 viewingField, viewingFieldArgs, vFieldCharPath,
                 vFieldCharBias,

                 extraObstruction, extraObstructionArgs, obstructCharPath,
                 obstructCharBias,

                 holisticDetection, holisticDetectionArgs, hDetectCharPath,
                 hDetectCharBias,

                 surveyNoiseFunction, surveyNoiseFunctionArgs, sNoiseCharPath,
                 sNoiseCharBias,

                 measurementFunction):
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

                        FrameEvents: the current FrameEvents

                        survey: the relevant survey object itself
            extraObstruction:
                Function. Returns a list of events that are
                potentially observable because they are not 
                obstructed by anything. This selection
                should be orthogonal to viewingField
                    Args: 
                        Time: the time in frames since the 
                        start of the survey

                        Events: the list of events that exist

                        survey: the relevant survey object itself

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
                    takes as 
                    args: 
                        event
                            the event to have noise generated on
                        survey: the relevant survey object itself
                    returns noise to be added to lum
            vFieldCharPath,eObstructCharPath,hDetectCharPath,sNoiseCharPath:
                Characteristic values for search strategy optimization
                Ranges of legal values for the associated extraArgs.
                each is a list of 3-tuples with lengths equal to
                the lengths of their corresponding extraArgs.
                The tuples tell the range of values over
                which to optimize and the datatype. Of the form:
                (low, high, "float") or (low, high, "int").
                The ranges are inclusive on low, and exclusive on high.
                If the type given is "int", the optimizer will only
                search within integers between low and high.
            vFieldCharBias,eObstructCharBias,hDetectCharBias,sNoiseCharBias:
                Characteristic values for Bias Detection.
                These are the ranges that the Bias extractor will search
                over.
                Ranges of legal values for the associated extraArgs.
                each is a list of 3-tuples with lengths equal to
                the lengths of their corresponding extraArgs.
                The tuples tell the range of values over
                which to optimize and the datatype. Of the form:
                (low, high, "float") or (low, high, "int").
                The ranges are inclusive on low, and exclusive on high.
                If the type given is "int", the optimizer will only
                search within integers between low and high.
            measurementFunction:
                Function. Produces information true and observed event
                    properties.

                The purpose of this function is to compare the
                    observed/true properties of ONE observable at
                    a time. This is because this function does 
                    not return in data where it is possible to
                    associate what data points correspond to
                    the *same* event. e.g. if you have 10 events
                    with a lifetime and a magnitude, you cannot tell
                    what magnitude belonged to the same event as a given
                    luminosity. 
                Args:
                    events:
                        List of all events created
                    survey: 
                        the relevant survey object itself
                Returns:
                    2-tuple of lists of 2-tuples.
                
                The top-level 2-tuple is of the form (true, observed).
                    true is a list of 2-tuples representing data about
                        the true event distribution.
                    observed is a list of 2-tuples representing data
                        about the observed event distribution

                Each 2-tuple inside the lists 'true' and 'observed' is
                    of the form (list, string). The list is data of the
                    events and the string is the name of the parameter
                    measured in the data (e.g. "lifetime)
                
                Example: If there were 3 events generated in total,
                    but only 1 was detected, and we were interested in
                    event lifetime, measurementFunction would return
                    something like;
                        ([([45,23,8],"lifetime")],[([23],"lifetime")])
                    Where the event with lifetime 23 was the only event 
                    to be detected

                        
        """
        self.view = viewingField
        self.vArgs = viewingFieldArgs
        self.vCharPath = vFieldCharPath
        self.vCharBias = vFieldCharBias
        
        self.obstruct = extraObstruction
        self.oArgs = extraObstructionArgs
        self.oCharPath = obstructCharPath
        self.oCharBias = obstructCharBias

        self.holistic = holisticDetection
        self.hArgs = holisticDetectionArgs
        self.hCharPath = hDetectCharPath
        self.hCharBias = hDetectCharBias

        self.surveyNoise = surveyNoiseFunction
        self.sArgs = surveyNoiseFunctionArgs
        self.sCharPath = sNoiseCharPath
        self.sCharBias = sNoiseCharBias
        
        self.measureFunc = measurementFunction

    def frameDetect(self, time, frameEvents, survey):
        """Mark events that are viewed and unobstructed
        """
        #Get the events that are "in frame" as it were
            #at the given absoluteTime
        eventsInView = self.view(time, frameEvents, survey, *self.vArgs)

        #Apply Obstruction to the "in frame" events 
            #at the given absoluteTime
        #The result is all events that have data logged
        frameDetected = self.obstruct(time, eventsInView, 
                                      survey, *self.oArgs)

        
        for pair in frameDetected:
            #pair = (event, index)
            #index is the corresponding index for event.history
            noise = self.surveyNoise(pair[0], survey, *self.sArgs)
            pair[0].recordDetection(pair[1], noise)


        
    def holisticDetect(self, events, survey):
        """Mark events that are detected overall
        """
        for event in events:
            if self.holistic(event, survey, *self.hArgs):
                event.holisticDetection = True
            else:
                event.holisticDetection = False
    