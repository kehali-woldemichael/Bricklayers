class ProcessingParameters:
    def __init__(self, inputPath, slicer, machine):
        self.inputPath = inputPath
        self.slicer = slicer
        self.machine = machine



    #parser.add_argument("-extrusionMultiplier", type=float, default=1, help="Extrusion multiplier (default: 1.0)")
    #parser.add_argument("-nonPlanar", type=int, choices=[0, 1], default=0, help="Enable non-planar infill (0=off, 1=on)")
    #parser.add_argument("-wallReorder", type=int, choices=[0, 1], default=1, help="Enable wall reordering (0=off, 1=on)")
    #parser.add_argument("-amplitude", type=float, default=DEFAULT_AMPLITUDE, help=f"Amplitude of the Z modulation (default: {DEFAULT_AMPLITUDE})")
    #parser.add_argument("-frequency", type=float, default=DEFAULT_FREQUENCY, help=f"Frequency of the Z modulation (default: {DEFAULT_FREQUENCY})")