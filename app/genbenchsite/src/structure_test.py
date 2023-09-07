from configparser import ConfigParser
from pathlib import Path
from .logger import logger


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


def get_site_config(path_benchmark):
    site_config = StructureTest.read_config(
        *StructureTest.find_config_file(path_benchmark, name="project.ini"),
        listSection=["benchsite"],
    )
    if len(site_config) < 1:
        logger.error("No config file found for the website parameters")
        return {}
    return site_config["benchsite"]


def get_benchmark_config(path_benchmark):
    benchmark_config = StructureTest.read_config(
        *StructureTest.find_config_file(Path(path_benchmark), name="project.ini"),
        listSection=["benchmark"],
    )
    if len(benchmark_config) < 1:
        logger.error("No config file found for the benchmark parameters")
        return {}
    return benchmark_config["benchmark"]


def get_target_config(path_benchmark):
    target_config = StructureTest.read_config(
        *StructureTest.find_config_file(path_benchmark, name="target.ini"),
    )
    if len(target_config) < 1:
        logger.error("No config file found for the target parameters")
        return {}
    # we add the description of the target

    description_path = list(
        StructureTest.find_config_file(
            Path(path_benchmark) / "targets", name="description.html"
        )
    )
    if len(description_path) < 1:
        logger.info("No description file found for the target parameters")

    for path in description_path:
        with open(path, "r") as f:
            target_config[path.parent.stem]["description"] = f.read()
    return target_config


def get_theme_config(path_benchmark):
    theme_config = StructureTest.read_config(
        *StructureTest.find_config_file(path_benchmark, name="theme.ini"),
    )
    if len(theme_config) < 1:
        logger.error("No config file found for the theme parameters")
        return {}
    description_path = list(
        StructureTest.find_config_file(
            Path(path_benchmark) / "themes", name="description.html"
        )
    )
    if len(description_path) < 1:
        logger.info("No description file found for the target parameters")

    for path in description_path:
        with open(path, "r") as f:
            theme_config.get(path.parent.stem, {})["description"] = (
                f.read() if path.parent.stem in theme_config else ""
            )
    return theme_config


def get_task_config(path_benchmark):
    task_config = StructureTest.read_config(
        *StructureTest.find_config_file(path_benchmark, name="task.ini"),
    )
    if len(task_config) < 1:
        logger.error("No config file found for the task parameters")
        return {}
    description_path = list(
        StructureTest.find_config_file(
            Path(path_benchmark) / "themes", name="description.html"
        )
    )
    if len(description_path) < 1:
        logger.info("No description file found for the target parameters")

    for path in description_path:
        with open(path, "r") as f:
            task_config.get(path.parent.stem, {})["description"] = (
                f.read() if path.parent.stem in task_config else ""
            )

    extra_path = list(
        StructureTest.find_config_file(
            Path(path_benchmark) / "themes", name="extra.html"
        )
    )
    if len(extra_path) < 1:
        logger.info("No extra file found for the target parameters")

    for path in extra_path:
        with open(path, "r") as f:
            task_config[path.parent.stem]["extra_description"] = f.read()
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

    print(
        StructureTest.get_site_config(pathRepo),
        len(StructureTest.get_site_config(pathRepo)),
    )
    print(
        StructureTest.get_benchmark_config(pathRepo),
        len(StructureTest.get_benchmark_config(pathRepo)),
    )
    print(
        StructureTest.get_target_config(pathRepo),
        len(StructureTest.get_target_config(pathRepo)),
    )
    print(
        StructureTest.get_theme_config(pathRepo),
        len(StructureTest.get_theme_config(pathRepo)),
    )
    print(
        StructureTest.get_task_config(pathRepo),
        len(StructureTest.get_task_config(pathRepo)),
    )

    pass
