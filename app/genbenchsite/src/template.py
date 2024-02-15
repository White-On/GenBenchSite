from pathlib import Path
from .logger import logger


class Repository:
    def __init__(self, path):
        self.path = Path(path)
        self.file_list = []
        self.repository_list = []
        self.path.mkdir(parents=False, exist_ok=False)

    def __repr__(self):
        return (
            f"Repository({self.path})\n"
            + "\n".join([f"├── {f}" for f in self.file_list])
            + "\n"
            + "\n".join([f"└── {r}" for r in self.repository_list])
        )

    def add_file(self, file_name, content=""):
        self.file_list.append(file_name)
        with open(self.path / file_name, "w") as f:
            f.write(content)
        return self

    def add_repository(self, repository_name):
        new_repository = Repository(self.path / repository_name)
        self.repository_list.append(new_repository)
        return new_repository


def load_template(path):
    # check that the file exists
    if not Path(path).exists():
        raise ValueError(f"{path} does not exists")
    config = ""
    section = ["config", "task", "target", "theme", "readme"]
    with open(path, "r") as f:
        config = f.read()
    return {s: c for s, c in zip(section, config.split("|"))}


def create_template(target_path="repository", nb_targets=1, nb_themes=1, nb_tasks=1):
    # we look for the template file
    template_path = Path(__file__).parent / ".template.txt"
    logger.info(f"Loading template from {template_path}")

    config = load_template(template_path)
    logger.info(f"Creating benchmark template in {target_path}")

    # we check that no repository already exists
    if Path(target_path).exists():
        logger.error(
            f"The benchmark or directory {target_path} already exists, please choose another name"
        )
        # raise ValueError(
        #     f"The benchmark or directory {target_path} already exists, please choose another name"
        # )
        return

    # main repository
    main_repo = Repository(target_path)
    (
        main_repo.add_file("README.md", content=config["readme"])
        .add_file("project.ini", content=config["config"])
        .add_repository("res")
    )

    # targets repository
    target_repo = main_repo.add_repository("targets")
    for i in range(1, nb_targets + 1):
        (
            target_repo.add_repository(f"target{i}")
            .add_file("target.ini", content=config["target"])
            .add_file("description.html", content="<p>Description of the library</p>")
        )

    # themes repository
    themes_repo = main_repo.add_repository("themes")
    for i in range(1, nb_themes + 1):
        theme_repo = (
            themes_repo.add_repository(f"theme{i}")
            .add_file("theme.ini", content=config["theme"])
            .add_file(
                "description.html",
                content="<p>Here you can add a html element to the page to display</p>",
            )
        )
        for j in range(1, nb_tasks + 1):
            task_repo = (
                theme_repo.add_repository(f"task{j}")
                .add_file("task.ini", content=config["task"])
                .add_file(
                    "preparation.py",
                    content="",
                )
                .add_file(
                    "evaluation1.py",
                    content="",
                )
                .add_file(
                    "evaluation2.py",
                    content="",
                )
                .add_file(
                    "description.html",
                    content="<p>Description of the task</p>",
                )
                .add_file(
                    "extra.html",
                    content="<p>Optional description, for details, images and extra explanation</p>",
                )
            )
            task_repo.add_repository("data")
            task_repo.add_repository("outputs")
            for t in range(1, nb_targets + 1):
                (
                    task_repo.add_repository(f"target{t}")
                    .add_file(
                        f"before.py",
                        content="# This file is used to mesure the time before the task",
                    )
                    .add_file(
                        f"run.py",
                        content="# This file is executed to run the task (runtime = run - before_run)",
                    )
                    .add_repository("outputs")
                )
    return main_repo


if __name__ == "__main__":
    print(create_template(nb_targets=2, nb_themes=2, nb_tasks=2))
