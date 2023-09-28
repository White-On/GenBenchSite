from setuptools import setup, find_packages

# load the README file.
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="genbenchsite",
    version="0.0.8",
    description="Generate a benchmark website from a set of benchmark tests",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Jules Cassan",
    author_email="jules.cassan@hotmail.com",
    url="https://white-on.github.io/GenBenchSite/",
    project_urls={
        "Github": "https://github.com/White-On/GenBenchSite",
    },
    entry_points={
        "console_scripts": [
            "gbs = genbenchsite.src.main:main",
        ]
    },
    package_dir={"": "app"},
    packages=find_packages(where="app"),
    package_data={"": ["html_template/*", ".template.txt", "website_template/**"]},
    python_requires=">=3.9",
    install_requires=[
        "colorama>=0.4.6",
        "Jinja2>=3.1.2",
        "MarkupSafe>=2.1.2",
        "numpy>=1.24.2",
        "psutil>=5.9.5",
        "Pygments>=2.15.1",
        "tqdm>=4.65.0",
        "rich>=12.5.1",
    ],
    extras_require={
        "dev": [
            "twine>=4.0.2",
        ],
    },
)
