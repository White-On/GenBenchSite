from configparser import ConfigParser
from pathlib import Path
from logger import logger


class StructureTest:
    def __init__(self) -> None:
        pass

    @staticmethod
    def read_config(*pathConfig, listSection=[]):
        logger.info("=======Reading config file(s)=======")
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
            refElement = listSection[0] if len(listSection) == 1 else path.parent.name
            logger.debug(f"Ref element : {refElement}")
            try:
                config[refElement] = {
                    key: configParser.get(section, key)
                    for section in sections
                    for key in configParser.options(section)
                }
            except Exception as e:
                logger.error(f"Error while reading config file : {e}")
                # raise Exception(f"Error while reading config file : {e}")
                return {}

        logger.info(
            "=======Config file(s) read=======\nnumber of section(s) found: "
            + str(len(config.keys()))
        )
        logger.debug(f"Config file : {config}")
        return config

    @staticmethod
    def find_config_file(path, name="config.ini"):
        path = Path(path)
        if not path.exists():
            logger.error(f"Path not found: {path}")
            # raise FileNotFoundError(f"File not found: {path}")
            return []

        config_files = path.glob(f"**/{name}")
        if not config_files:
            logger.warning(f"Config file not found in {path}")
            # raise FileNotFoundError(f"Config file not found in {path}")
            return []

        return config_files

    @classmethod
    def get_site_config(cls, path_benchmark):
        site_config = cls.read_config(
            *cls.find_config_file(path_benchmark, name="project.ini"),
            listSection=["benchsite"],
        )
        if len(site_config) < 1:
            logger.error("No config file found for the website parameters")
            return {}
        return site_config["benchsite"]

    @classmethod
    def get_benchmark_config(cls, path_benchmark):
        benchmark_config = cls.read_config(
            *cls.find_config_file(Path(path_benchmark), name="project.ini"),
            listSection=["benchmark"],
        )
        if len(benchmark_config) < 1:
            logger.error("No config file found for the benchmark parameters")
            return {}
        return benchmark_config["benchmark"]

    @classmethod
    def get_target_config(cls, path_benchmark):
        target_config = cls.read_config(
            *cls.find_config_file(path_benchmark, name="target.ini"),
        )
        if len(target_config) < 1:
            logger.error("No config file found for the target parameters")
            return {}
        return target_config

    @classmethod
    def get_theme_config(cls, path_benchmark):
        theme_config = cls.read_config(
            *cls.find_config_file(path_benchmark, name="theme.ini"),
        )
        if len(theme_config) < 1:
            logger.error("No config file found for the theme parameters")
            return {}
        return theme_config

    @classmethod
    def get_task_config(cls, path_benchmark):
        task_config = cls.read_config(
            *cls.find_config_file(path_benchmark, name="task.ini"),
        )
        if len(task_config) < 1:
            logger.error("No config file found for the task parameters")
            return {}
        return task_config

    


if __name__ == "__main__":
    # pathSite = "C:/Users/jules/Documents/Git/BenchSite/repository/config"
    # listPathTarget = "C:/Users/jules/Documents/Git/BenchSite/repository/targets"
    # themePath = "C:/Users/jules/Documents/Git/BenchSite/repository/themes"

    pathRepo = "D:/Jules_Scolaire/Master_Androide_M1/BenchSite/repository"

    # test = StructureTest()
    # file_conf = test.findConfigFile(pathSite)
    # config = test.readConfig(*list(file_conf))

    # test = StructureTest()
    # file_conf = test.findConfigFile(listPathTarget)
    # config = test.readConfig(*list(file_conf))

    # test = StructureTest()
    # file_conf = test.find_config_file(themePath, "theme.ini")
    # config = test.read_config(*list(file_conf))

    print(StructureTest.get_site_config(pathRepo), len(StructureTest.get_site_config(pathRepo)))
    print(StructureTest.get_benchmark_config(pathRepo) , len(StructureTest.get_benchmark_config(pathRepo)))
    print(StructureTest.get_target_config(pathRepo) , len(StructureTest.get_target_config(pathRepo)))
    print(StructureTest.get_theme_config(pathRepo) , len(StructureTest.get_theme_config(pathRepo)))
    print(StructureTest.get_task_config(pathRepo) , len(StructureTest.get_task_config(pathRepo)))

    pass
