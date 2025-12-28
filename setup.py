from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="python-pathfinder",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="An educational game for learning Python and web development",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/python-pathfinder",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Flask",
        "Topic :: Education",
        "Topic :: Games/Entertainment",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "pathfinder-init=scripts.init_db:main",
        ],
    },
)