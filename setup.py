from setuptools import setup, find_packages

with open('requirements.txt') as f:
    REQUIREMENTS = f.read().splitlines()

setup(name="tasker",
      version="0.0.1",
      author="Ziga Ivansek",
      description="",
      python_requires='>=3.8.10',
      install_requires=REQUIREMENTS,
      entry_points={
          'console_scripts': ['task = tasker.task:cli',],
      },
      packages=find_packages())
