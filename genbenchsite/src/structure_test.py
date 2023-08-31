from configparser import ConfigParser
from pathlib import Path
from genbenchsite.src.logger import logger


class StructureTest:
    def __init__(self) -> None:
        pass

    def readConfig(self, *pathConfig, listSection=[]):
        logger.info("Reading config file(s)")
        logger.debug(f"Path config : {pathConfig}")
        if len(pathConfig) == 0:
            logger.warning("No path given")
            return {}

        config = {}
        for path in pathConfig:
            logger.debug(f"Reading config file in {path.absolute()}")
            configParser = ConfigParser()
            configParser.read(path.absolute())
            sections = configParser.sections() if len(listSection) == 0 else listSection
            logger.debug(f"Sections : {sections}")
            refElement = path.parent.name
            logger.debug(f"Ref element : {refElement}")
            try:
                config[refElement] = {
                    key: configParser.get(section, key)
                    for section in sections
                    for key in configParser.options(section)
                }
            except Exception as e:
                logger.error(f"Error while reading config file : {e}")
                raise Exception(f"Error while reading config file : {e}")

        # if len(pathConfig) == 1:
        #     config = config[pathConfig[0].parent.name]

        logger.info(
            "=======Config file(s) read=======\nnumber of section(s) found: "
            + str(len(config.keys()))
        )
        logger.debug(f"Config file : {config}")
        return config

    def findConfigFile(self, path, name="config.ini"):
        path = Path(path)
        if not path.exists():
            logger.error(f"Path not found: {path}")
            raise FileNotFoundError(f"File not found: {path}")

        config_files = path.glob(f"**/{name}")
        if not config_files:
            logger.warning(f"Config file not found in {path}")
            raise FileNotFoundError(f"Config file not found in {path}")

        return config_files


if __name__ == "__main__":
    pathSite = "C:/Users/jules/Documents/Git/BenchSite/repository/site"
    listPathTarget = "C:/Users/jules/Documents/Git/BenchSite/repository/targets"
    themePath = "C:/Users/jules/Documents/Git/BenchSite/repository/themes"

    # test = StructureTest()
    # file_conf = test.findConfigFile(pathSite)
    # config = test.readConfig(*list(file_conf))

    # test = StructureTest()
    # file_conf = test.findConfigFile(listPathTarget)
    # config = test.readConfig(*list(file_conf))

    test = StructureTest()
    file_conf = test.findConfigFile(themePath, "theme.ini")
    config = test.readConfig(*list(file_conf))
