import yaml

CONFIG_FILE_PATH = "config.yml"

class configFile:
    def __init__(self):
        try:
            configFile = open(CONFIG_FILE_PATH, 'r')
            self.config = yaml.load(configFile)
            self.FIELD = self.config["Field"]
            self.ROBOTS = list()
            for i in range(4):
                self.ROBOTS.append(self.config["Robot"+str(i)])
            self.RULES = self.config["Rules"]
            self.GUI = self.config["Gui"]
        except:
            print("ERROR: conifg file was corrupted")
            self.restoreDefault()
            self.saveConfig()

    def restoreDefault(self):
        self.ROBOTS = list()
        for i in range(4):
            self.ROBOTS.append({"Active": True,
                                "Stable": True,
                                "MainPath": "RobotPrograms/simple_python/main.py"})
        self.RULES = {"LagOfProgress": 2000,
                      "LagOfProgressActive": True,
                      "DoubleDefense": True,
                      "Pushing": True,
                      "OutOfBounce": True,
                      "Timeout": 0,
                      "DefektTime": 60000,
                      "TestMode": 0}
        self.GUI = {"Debugger": False,
                      "Commandline": False,
                      "Fast": True,
                      "SamplingRate": 20,
                      "ShowTiming": False}
        self.FIELD = {"TouchlineActive": True,
                      "TouchlineLength": 183,
                      "TouchlineWidth": 122,
                      "GoalDepth": 8,
                      "GoalWidth": 60,
                      "BorderLength": 243,
                      "BorderWidth": 183}
        self.config = dict()

    def saveConfig(self):
        self.config["Field"] = self.FIELD
        for i in range(4):
            self.config["Robot" + str(i)] = self.ROBOTS[i]
        self.config["Rules"] = self.RULES
        self.config["Gui"] = self.GUI
        with open(CONFIG_FILE_PATH, 'w') as configFile:
            yaml.dump(self.config, configFile, default_flow_style=False)


gc = configFile()