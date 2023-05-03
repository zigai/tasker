import pathlib

from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
REQUIREMENTS = (HERE / "requirements.txt").read_text()

setup(
    name="tasker-python",
    version="0.1.0",
    description="Function/CLI tasks with scheduling and notifications",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Žiga Ivanšek",
    author_email="ziga.ivansek@gmail.com",
    url="https://github.com/zigai/tasker",
    license="MIT",
    packages=find_packages(),
    install_requires=REQUIREMENTS,
    entry_points={},
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Office/Business :: Scheduling",
        "License :: OSI Approved :: MIT License",
    ],
    keywords=[
        "tasker",
        "python",
        "task scheduler",
        "scheduler notifications",
        "cron notifications",
    ],
)
