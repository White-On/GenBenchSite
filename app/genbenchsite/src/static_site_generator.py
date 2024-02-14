"""Docstring for the module static_site_generator.py

This module contains the class StaticSiteGenerator and the differents function to manipulate the StaticSiteGenerator class.
You can use it to create and generate static html page with jinja2.

"""

from jinja2 import Environment, FileSystemLoader
import os
import shutil
from pathlib import Path


class StaticSiteGenerator:
    """
    Create the static site generator object.

    Attributes
    ----------
    scriptFilePath : str
        The path of the folder where the images are stored.
    htmlTemplateFilePath : str
        The path of the folder where the HTML templates are stored.
    assetsFilePath : str
        The path of the folder where the assets are stored.
    contentFilePath : str
        The path of the folder where the output files are stored.
    styleFilePath : str
        The path of the folder where the CSS files are stored.
    """

    def __init__(
        self,
        output_website_path: str = "website",
    ):
        """Create the static site generator object

        Check if the path exist, if not, create the folder if `createFolder` is True.

        Parameters
        ----------
        scriptFilePath : str
            The path of the folder where the script are stored, by default "script"
        htmlTemplateFilePath : str
            The path of the folder where the HTML templates are stored.
        assetsFilePath : str
            The path of the folder where the assets are stored.
        contentFilePath : str
            The path of the folder where the output files are stored.
        styleFilePath : str
            The path of the folder where the CSS files are stored.
        createFolder : bool, optional
            If True, create the folder if it does not exist, by default True
        """

        # the path of the script
        website_template_path = Path(__file__).parent.parent / "website_template"
        html_components_path = Path(__file__).parent.parent / "html_template"
        # first we make a copy of the website_template folder in the output folder
        self.output_website_path = Path(output_website_path)
        # if the output_website_path does exist, we delete it to create a updated version
        if self.output_website_path.exists():
            # we first check if the output_website_path is a directory containing the website_template folder
            if is_pages_directory(self.output_website_path):
                delete_directory(self.output_website_path)
            # if not we dont want to delete something that may be important

        # we copy the website_template folder in the output_website_path
        shutil.copytree(website_template_path, self.output_website_path)

        # we remove the __init__.py file if it exist
        if Path(self.output_website_path / "__init__.py").exists():
            Path(self.output_website_path / "__init__.py").unlink()
        # we remove the __pycache__ folder if it exist
        if Path(self.output_website_path / "__pycache__").exists():
            delete_directory(self.output_website_path / "__pycache__")

        # we create the content folder
        self.contentFilePath = self.output_website_path / "content"
        self.contentFilePath.mkdir()

        # we now link the differents attributes to the path of the website_template folder
        self.scriptFilePath = self.output_website_path / "script"
        self.assetsFilePath = self.output_website_path / "assets"
        self.styleFilePath = self.output_website_path / "style"
        self.contentFilePath = self.output_website_path / "content"
        self.htmlTemplateFilePath = html_components_path

        # for path in [
        #     scriptFilePath,
        #     htmlTemplateFilePath,
        #     assetsFilePath,
        #     contentFilePath,
        #     styleFilePath,
        # ]:
        #     if not self.CheckIfPathExist(path) and not createFolder:
        #         raise Exception(f"Path {path} does not exist")
        #     elif not self.CheckIfPathExist(path) and createFolder:
        #         # Create the folder relative to path of the script
        #         os.mkdir(os.path.join(current_path, path))

        # # we clean the output folder
        # for file in os.listdir(os.path.join(current_path, contentFilePath)):
        #     os.remove(os.path.join(current_path, contentFilePath, file))

        # we need the basename of these path to use it in the HTML template
        basename = lambda path: os.path.basename(os.path.normpath(path))

        self.scriptFilePath = basename(self.scriptFilePath)
        self.assetsFilePath = basename(self.assetsFilePath)
        self.styleFilePath = basename(self.styleFilePath)

    def CheckIfPathExist(self, path: str) -> bool:
        """Check if the path relative to the path of the script exist.

        Parameters
        ----------
        path : str
            The path to check

        Returns
        -------
        bool
            True if the path exist, False otherwise
        """

        return os.path.exists(os.path.join(os.path.dirname(__file__), path))

    def CreateHTMLComponent(self, templateName: str, **kwargs) -> str:
        """Create the HTML component from the template and the arguments. The arguments must be in the form of a dictionary.
        the key of the dictionary will be the name of the variable in the template.

        Parameters
        ----------
        templateName : str
            The name of the template to use.
        **kwargs : dict
            The arguments to pass to the template.

        Returns
        -------
        str
            The HTML component

        """
        file_loader = FileSystemLoader(self.htmlTemplateFilePath)
        env = Environment(loader=file_loader)
        template = env.get_template(templateName)
        return template.render(**kwargs)

    def CreateHTMLPage(
        self, HTMLComponent: list[str], pageName: str, manualOutputPath=None
    ) -> None:
        """Create the HTML page from the HTML component list. You can compose the HTML component list as you want,
        but the order is important. The first element of the list will be the first element of the HTML page.

        Parameters
        ----------
        HTMLComponent : list
            The list of the HTML component to use.
        pageName : str
            The name of the page to create.

        """
        html = "".join(HTMLComponent)
        outputPath = self.contentFilePath
        if manualOutputPath is not None:
            outputPath = manualOutputPath
        with open(f"{outputPath}/{pageName}", "w") as f:
            f.write(html)


def delete_directory(dir_path: str):
    """
    Clears the contents of a directory.

    Arguments
    ---------
    dir_path : str
        The path to the directory to clear.

    """
    path = Path(dir_path)
    if path.exists() and path.is_dir():
        shutil.rmtree(path)
    else:
        print(f"Directory {dir_path} does not exist.")

def is_pages_directory(path: str) -> bool:
    """
    Checks if a directory is a pages directory containing an index.html file, style repository, assets repository and script repository.

    Arguments
    ---------
    path : str
        The path to the directory to check.

    Returns
    -------
    bool
        True if the directory is a pages directory, False otherwise.

    """
    path = Path(path)
    if path.exists() and path.is_dir():
        if (
            Path(path / "index.html").exists()
            or Path(path / "style").exists()
            and Path(path / "assets").exists()
            and Path(path / "script").exists()
            and Path(path / "content").exists()
        ):
            return True
        else:
            return False
    return False


if __name__ == "__main__":
    ssg = StaticSiteGenerator()
