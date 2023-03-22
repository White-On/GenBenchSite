"""Docstring for the module static_site_generator.py

This module contains the class StaticSiteGenerator and the differents function to manipulate the StaticSiteGenerator class.
You can use it to create and generate static html page with jinja2.

"""

from jinja2 import Environment, FileSystemLoader
import os

class StaticSiteGenerator:
    """
    Create the static site generator object.

    Attributes
    ----------
    imgFilePath : str
        The path of the folder where the images are stored.
    htmlTemplateFilePath : str
        The path of the folder where the HTML templates are stored.
    assetsFilePath : str
        The path of the folder where the assets are stored.
    outputFilePath : str
        The path of the folder where the output files are stored.
    styleFilePath : str
        The path of the folder where the CSS files are stored.
    """
    
    def __init__(self, imgFilePath="img", htmlTemplateFilePath="template", assetsFilePath="assets", outputFilePath="output", styleFilePath="style", createFolder:bool = True):
        """Create the static site generator object

        Check if the path exist, if not, create the folder if `createFolder` is True.

        Parameters
        ----------
        imgFilePath : str
            The path of the folder where the images are stored.
        htmlTemplateFilePath : str
            The path of the folder where the HTML templates are stored.
        assetsFilePath : str
            The path of the folder where the assets are stored.
        outputFilePath : str
            The path of the folder where the output files are stored.
        styleFilePath : str
            The path of the folder where the CSS files are stored.
        createFolder : bool, optional
            If True, create the folder if it does not exist, by default True
        """
        
        for path in [imgFilePath, htmlTemplateFilePath, assetsFilePath, outputFilePath, styleFilePath]:
            if not self.CheckIfPathExist(path) and not createFolder:
                raise Exception(f"Path {path} does not exist")
            elif not self.CheckIfPathExist(path) and createFolder:
                # Create the folder relative to path of the script
                os.mkdir(os.path.join(os.path.dirname(__file__), path))


        self.imgFilePath = imgFilePath
        self.htmlTemplateFilePath = htmlTemplateFilePath
        self.assetsFilePath = assetsFilePath
        self.outputFilePath = outputFilePath
        self.styleFilePath = styleFilePath

    def CheckIfPathExist(self, path:str) -> bool:
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
    
    def CreateHTMLComponent(self, templateName:str, **kwargs) -> str:
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
    
    def CreateHTMLPage(self, HTMLComponent:list[str], pageName:str) -> None:
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
        with open(f"{self.outputFilePath}/{pageName}", "w") as f:
            f.write(html)
        