import pathlib

from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
REQUIREMENTS = (HERE / "requirements.txt").read_text()

setup(name="tasker",
      version="0.1.2",
      description="Automate shell tasks with python",
      long_description=README,
      long_description_content_type="text/markdown",
      author="Ziga Ivansek",
      author_email="ziga.ivansek@gmail.com",
      url="https://github.com/zigai/tasker",
      license="MIT",
      classifiers=[
          "Programming Language :: Python",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9",
          "Programming Language :: Python :: 3.10",
          "Programming Language :: Python :: 3 :: Only",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      packages=find_packages(),
      install_requires=REQUIREMENTS,
      entry_points={
          'console_scripts': ['tasker = tasker.tasker_cli:cli',],
      })
