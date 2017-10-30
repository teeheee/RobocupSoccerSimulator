import yaml

CONFIG_FILE_PATH = "config.yml"

class configFile:
    def __init__(self):
        try:
            configFile = open(CONFIG_FILE_PATH, 'r')
            self.config = yaml.load(configFile)
            self.OUTER_FIELD_WIDTH = self.config["FieldDiemensions"]["OuterWidth"]
            self.OUTER_FIELD_LENGTH = self.config["FieldDiemensions"]["OuterLength"]
            self.INNER_FIELD_WIDTH = self.config["FieldDiemensions"]["InnerWidth"]
            self.INNER_FIELD_LENGTH = self.config["FieldDiemensions"]["InnerLength"]
            self.GOAL_WIDTH = self.config["FieldDiemensions"]["GoalWidth"]
            self.GOAL_DEPTH = self.config["FieldDiemensions"]["GoalDepth"]
            self.ROBOTS = list()
            for i in range(4):
                self.ROBOTS.append(self.config["Robot"+str(i)])
            self.RULES = self.config["Rules"]
            self.GUI = self.config["Gui"]
        except:
            self.restoreDefault()
            self.saveConfig()

    def restoreDefault(self):
        self.OUTER_FIELD_WIDTH = 182
        self.OUTER_FIELD_LENGTH = 243
        self.INNER_FIELD_WIDTH = 122
        self.INNER_FIELD_LENGTH = 183
        self.GOAL_WIDTH = 60
        self.GOAL_DEPTH = 8
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
                      "ShowTiming": True}
        self.config = dict()

    def saveConfig(self):
        self.config["FieldDiemensions"] = dict()
        self.config["FieldDiemensions"]["OuterWidth"] = self.OUTER_FIELD_WIDTH
        self.config["FieldDiemensions"]["OuterLength"] = self.OUTER_FIELD_LENGTH
        self.config["FieldDiemensions"]["InnerWidth"] = self.INNER_FIELD_WIDTH
        self.config["FieldDiemensions"]["InnerLength"] = self.INNER_FIELD_LENGTH
        self.config["FieldDiemensions"]["GoalWidth"] = self.GOAL_WIDTH
        self.config["FieldDiemensions"]["GoalDepth"] = self.GOAL_DEPTH
        for i in range(4):
            self.config["Robot" + str(i)] = self.ROBOTS[i]
        self.config["Rules"] = self.RULES
        self.config["Gui"] = self.GUI
        with open(CONFIG_FILE_PATH, 'w') as configFile:
            yaml.dump(self.config, configFile, default_flow_style=False)


gc = configFile()