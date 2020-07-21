"""
Processing logic for the Standin2Aovs App.
The intention was for this to be called from the UI and then perform some actions based on the
method calls in the UI.
"""

# importing third party modules
import arnold
import maya_create_aovs

SUPPORTED_APPS = ["maya", "houdini", "gaffer", "katana"]


class Standin2Aovs(object):
    def __init__(self, ass_file, output_window_logger):
        """
        init method for the class Standin2Aovs
        """
        self.ass_file = ass_file

        # Beginning an Arnold session and loading the ass file in memory to process
        arnold.AiBegin()
        arnold.AiMsgSetConsoleFlags(arnold.AI_LOG_ALL)
        arnold.AiASSLoad(self.ass_file, arnold.AI_NODE_ALL)

        # Initialising object variables
        self.aovs_info = {}
        self.drivers_info = {}
        self.output_window_logger = output_window_logger

    @staticmethod
    def get_param_value(param_type, param_name, node):
        """
        Gets the parameter value based on the param type for the given node/

        :param param_type: Type pf the parameter whose value is to be queried.
        :param param_name: Name of the Parameter whose value is to be queried.
        :param node: Node for which the parameter needs is to be queried.
        """
        param_val = None

        if param_type == arnold.AI_TYPE_BYTE:
            param_val = arnold.AiNodeGetByte(node, param_name)
        elif param_type == arnold.AI_TYPE_INT:
            param_val = arnold.AiNodeGetInt(node, param_name)
        elif param_type == arnold.AI_TYPE_UINT:
            param_val = arnold.AiNodeGetUInt(node, param_name)
        elif param_type == arnold.AI_TYPE_FLOAT:
            param_val = arnold.AiNodeGetFlt(node, param_name)
        elif param_type == arnold.AI_TYPE_STRING:
            param_val = arnold.AiNodeGetStr(node, param_name)
        elif param_type == arnold.AI_TYPE_BOOLEAN:
            param_val = arnold.AiNodeGetBool(node, param_name)
        elif param_type == arnold.AI_TYPE_RGB:
            param_val = arnold.AiNodeGetRGB(node, param_name)
        elif param_type == arnold.AI_TYPE_RGBA:
            param_val = arnold.AiNodeGetRGBA(node, param_name)
        elif param_type == arnold.AI_TYPE_VECTOR:
            param_val = arnold.AiNodeGetVec(node, param_name)
        elif param_type == arnold.AI_TYPE_VECTOR2:
            param_val = arnold.AiNodeGetVec2(node, param_name)
        elif param_type == arnold.AI_TYPE_ENUM:
            param_val = arnold.AiNodeGetStr(node, param_name)

        return param_val

    def get_driver_info(self, driver_node_name):
        driver_info = {}
        driver_node = arnold.AiNodeLookUpByName(driver_node_name)
        driver_node_entry = arnold.AiNodeGetNodeEntry(driver_node)

        if driver_node_name not in driver_info.keys():
            param_iterator = arnold.AiNodeEntryGetParamIterator(driver_node_entry)

            while not arnold.AiParamIteratorFinished(param_iterator):
                param_entry = arnold.AiParamIteratorGetNext(param_iterator)
                param_name = arnold.AiParamGetName(param_entry)
                param_type = arnold.AiParamGetType(param_entry)

                driver_info[param_name] = self.get_param_value(
                    param_type, param_name, driver_node
                )

            arnold.AiParamIteratorDestroy(param_iterator)

        return driver_info

    def get_all_aovs(self):
        """
        Gets the aovs found in the ass_file provided and return a dictionary of the information
        collected that would be required to recreate these aovs in the current scene.

        :return dict: Dictionary containing information about the the aovs
                      to be created in the scene.
        """
        options_iterator = None

        try:
            # Getting all AOVs in the ass file
            options_iterator = arnold.AiUniverseGetNodeIterator(arnold.AI_NODE_OPTIONS)
            while not arnold.AiNodeIteratorFinished(options_iterator):
                node = arnold.AiNodeIteratorGetNext(options_iterator)
                outputs = arnold.AiNodeGetArray(node, "outputs")

                for i in range(arnold.AiArrayGetNumElements(outputs)):
                    output = arnold.AiArrayGetStr(outputs, i)
                    (
                        aov_display_name,
                        aov_data_type,
                        aov_filter,
                        aov_driver,
                    ) = output.split(" ")

                    self.aovs_info[aov_display_name] = {
                        "data_type": str(aov_data_type),
                        "filter": str(aov_filter),
                        "driver": {aov_driver: self.get_driver_info(aov_driver)},
                    }


        except ValueError as ver:
            print ver.message
        finally:
            if options_iterator is not None:
                arnold.AiNodeIteratorDestroy(options_iterator)

    def create_aovs_in_maya(self):
        # Invoking the Maya Create Aovs, which will take care of the AOVs creation in the scene
        # and return the results.
        from pprint import pprint

        pprint(self.aovs_info)
        create_aovs = maya_create_aovs.MayaCreateAovs(
            self.aovs_info, self.output_window_logger
        )

        create_aovs.run()  # Running the AOV creation

    def run(self, current_app=None):
        """
        This method first collects all the aovs info and then creates the AOVs in the scene based
        on the app we are in.

        :return:
        """
        self.get_all_aovs()
        print self.aovs_info

        if current_app is None:
            raise ValueError(
                "An App is needed to proceed with the process. This App is the DCC "
                "you are running this tool with. For eg. Maya, Houdini, Gaffer, "
                "Katana."
            )

        if current_app not in SUPPORTED_APPS:
            raise ValueError(
                "Sorry, the app {0} is not currently supported by this tool.".format(
                    current_app
                )
            )

        # Executing teh appropriate function based on the current app selection
        if current_app == "maya":
            print "Creating"
            # self.create_aovs_in_maya()

    def __del__(self):
        """
        Destructor for the class Standin2Aovs.
        :return:
        """
        # Destroying the Arnold Session
        arnold.AiEnd()
