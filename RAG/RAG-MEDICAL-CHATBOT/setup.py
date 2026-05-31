from setuptools import find_packages, setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="rag-medical-chatbot",
    version="0.1",
    author="Azahar",
    packages=find_packages(),
    install_requires=requirements,
)
