# CCBias

CCBias is (perhaps 'will be') a tool designed to help researchers understand how observation selection bias in event detection influences their data and conclusions. CCbias is designed with Astronomy in mind, but the core functionality is model agnostic, meaning it could be as easily applied to events associated with animals as events associated with Astronomy.

CCBias models the world in a two-step process: First, there is event generation. This constitutes a description of how whatever events are being investigated operate in truth. CCbias uses this to generate synthetic data (e.g. 15 supernovae occured in X time frame at Y positions on the sky with Z light curves, etc.) Second comes the Observing Profile. The Observing Profile represents the limitations imposed on observers by nature, instruments, and strategies that restrict our ability to detect events that occur. The Observing Profile takes the data generated, and prunes it down, spitting out a subset of events that were observed.

CCBias uses this model structure to recommend observing strategies (what telescope should I use? How many times per night should I change where it's pointed?) and estimate the observing bias present in real data.
