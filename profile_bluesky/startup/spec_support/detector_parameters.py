# Converts matlab code into a python dictionary


class PythonDict:
    """
    Detector properties, as defined in matlab file
    """
    def __init__(self):
        self.masterDict = self.describe_detectors()

        self.manufacturerDict = {
            # 1: "Direct Detection CCD in slow mode",
            5: "DALSA", 
            8: "PI Princeton Instruments", 
            13: "PI Princeton Instruments", 
            # 15: "APS Detector Pool Fast CCD",
            20: "ANL-LBL FastCCD Detector", 
            25: "LAMBDA", 
            30: "EIGER", 
            35: "UFXC_128x256", 
            45: "RIGAKU500K", 
            46: "RIGAKU500K_NoGap",
        }
        for k, v in self.masterDict.items():
            v["manufacturer"] = self._getManufacturer_(k)

    def returnMasterDict(self):
        return self.masterDict

    def returnManufacturerDict(self):
        return self.manufacturerDict
    
    def _getManufacturer_(self, detNum):
        return self.manufacturerDict.get(detNum, "UNKNOWN")

    def describe_detectors(self):
        "Converts matlab code into a python dictionary"
        
        masterDict = {}
        
        with open("detectorinfo.m", "r") as f:
            for line in f:
                line = line.strip()
                if len(line) == 0 or line[0] == "%":
                    # ignore this line
                    continue
                
                if line.startswith("if") and line.find("ccdimginfo.detector") != -1:
                    # matlab: if ( ccdimginfo.detector == ...
                    detNum = line.split("==")
                    detNum = detNum[1].split(")")
                    detNum = int(detNum[0].strip())
                    masterDict[detNum] = {}
            
                elif line.startswith("ccdimginfo.") and line.find("=") >= 0:
                    # matlab: within if block, defines a parameter
                    line = line.split(";")[0].strip()   # chop off any comment
                    key, value = line.split("=")
                    key = key.split(".")[1].strip()     # trimming
                    value = value.strip()               # trimming
                    # Try to convert to float or integer, else leave as string
                    if value.find(".") >= 0:
                        dtype = float
                    else:
                        dtype = int
                    try:
                        value = dtype(value)
                    except ValueError:
                        pass
                    masterDict[detNum][key] = value
    
        return masterDict


if __name__ == "__main__":
    detectors = PythonDict()
    
    # Print the dictionary an easy-to-read format
    import json
    print(json.dumps(detectors.masterDict, indent=2))
