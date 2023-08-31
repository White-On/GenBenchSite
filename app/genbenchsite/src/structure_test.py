from configparser import ConfigParser
from pathlib import Path
from genbenchsite.src.logger import logger


class StructureTest:
    def __init__(self) -> None:
        pass

    def read_config(self, *pathConfig, listSection=[]):
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

        logger.info(
            "=======Config file(s) read=======\nnumber of section(s) found: "
            + str(len(config.keys()))
        )
        logger.debug(f"Config file : {config}")
        return config

    def find_config_file(self, path, name="config.ini"):
        path = Path(path)
        if not path.exists():
            logger.error(f"Path not found: {path}")
            raise FileNotFoundError(f"File not found: {path}")

        config_files = path.glob(f"**/{name}")
        if not config_files:
            logger.warning(f"Config file not found in {path}")
            raise FileNotFoundError(f"Config file not found in {path}")

        return config_files
    
    @classmethod
    def get_site_config(cls, pathSite):
        siteConfig = cls.read_config(
            *cls.find_config_file(Path(pathSite) / "config"),
            listSection=["site"],
        )
        return siteConfig["config"]
    
    @classmethod
    def get_target_config(cls, pathTarget):
        targetConfig = cls.read_config(
            *cls.find_config_file(Path(pathTarget) / "config"),
            listSection=["targets"],
        )
        return targetConfig
    
    @classmethod
    def get_theme_config(cls, pathTheme):
        themeConfig = cls.read_config(
            *cls.find_config_file(Path(pathTheme) / "config",name="theme.ini"),
            listSection=["theme"],
        )
        return themeConfig
    
    @classmethod
    def get_task_config(cls, pathTask):
        taskConfig = cls.read_config(
            *cls.find_config_file(Path(pathTask) / "config"),
            listSection=["task"],
        )
        return taskConfig
    
    @classmethod
    def get_benchmark_config(cls, pathBenchmark):
        benchmarkConfig = cls.read_config(
            *cls.find_config_file(Path(pathBenchmark) / "config"),
            listSection=["benchmark"],
        )
        return benchmarkConfig["config"]


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

    # test = StructureTest()
    # file_conf = test.find_config_file(themePath, "theme.ini")
    # config = test.read_config(*list(file_conf))

    pass