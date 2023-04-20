import platform
import psutil
import multiprocessing

import json

def GetRunMachineMetadata():
        """
        Get the metadata of the machine
        """
        return {
            "machine_os" : platform.system(),
            "machine_os_version" : platform.release(),
            "machine_os_architecture" : platform.architecture(),
            "machine_processor" : platform.processor(),
            "machine_processor_count" : multiprocessing.cpu_count(),
            "machine_memory" :psutil._common.bytes2human(psutil.virtual_memory().total),
            "machine_python_version" : platform.python_version()
        }

def SaveMachineDataInJson(outputPath:str):
        with open(outputPath, 'w') as file:
            json.dump(GetRunMachineMetadata(), file)

if __name__ == "__main__":
    SaveMachineDataInJson("machine.json")