"""
The AOV builder for Maya that would be responsible for creating and setting up the desired AOVs
in a Maya scene.
"""

from maya import cmds
from mtoa.core import createOptions
from mtoa import aovs

import standin2aovs_ui

ARNOLD_DEFAULT_DRIVER = "defaultArnoldDriver"
ARNOLD_DEFAULT_FILTER = "defaultArnoldFilter"
AOV_DATA_TYPE_MAPPINGS = {
    "INT": 1,
    "BOOL": 3,
    "FLOAT": 4,
    "RGB": 5,
    "RGBA": 6,
    "VECTOR": 7,
    "VECTOR2": 9,
    "POINTER": 11,
}


class MayaCreateAovs(object):
    def __init__(self, aovs_info=None, output_window_logger=None):
        if aovs_info is None:
            raise ValueError(
                "ABORTING. To create an AOV in the scene. The dictionary containing "
                "the Information related to the AOVs to be created is required."
            )

        if output_window_logger is None:
            raise ValueError("ABORTING. Need a logger object to log the progress.")

        self.aovs_info = aovs_info
        self.output_window_logger = output_window_logger

    def create_aovs(self):
        """
        Creates an aov node for each key in aovs_info, and creates the required respective nodes and
        sets their parameters in the scene according the information provided in the aovs_info
        dict .
        """
        for aov_name in self.aovs_info:
            if aov_name in cmds.ls(type="aiAOV"):
                self.output_window_logger.update_output_window(
                    "AOV - {0}, already exists".format(aov_name)
                )
            else:
                self.output_window_logger.update_output_window(
                    "Creating AOV - {0}".format(aov_name)
                )

                a = aovs.AOVInterface().addAOV("RGBA")
                a.rename(aov_name)
                cmds.rename(a.node, aov_name)

            # Setting the Data Type
            data_type_index = AOV_DATA_TYPE_MAPPINGS[
                self.aovs_info[aov_name]["data_type"]
            ]
            cmds.setAttr("{0}.type".format(aov_name), data_type_index)

            # Configuring the AOV Drivers
            driver_name = self.aovs_info[aov_name]["driver"]
            if driver_name.split("@")[0] != ARNOLD_DEFAULT_DRIVER:
                self.create_aov_driver(aov_name, driver_name)

            # Configuring the AOV Filters
            filter_name = self.aovs_info[aov_name]["filter"]
            if filter_name.split("@")[0] != ARNOLD_DEFAULT_FILTER:
                self.create_aov_filter(aov_name, filter_name)

            # Finding Shader Connected to the AOV

    def create_aov_driver(self, aov_name, driver_name):
        print ("Creating AOV Driver for {0}".format(aov_name))
        # driver_node = cmds.createNode("aiAOVDriver")  # print aov_name  # print driver_name

    def create_aov_filter(self, aov_name, filter_name):
        pass  # print aov_name  # print filter_name

    def run(self):
        self.create_aovs()
