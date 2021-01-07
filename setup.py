import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ghost-word-game",
    # own username
    version="0.3.9",
    author="Joyce Yeo",
    author_email="jycyeo@yahoo.com.sg",
    description="Python engine for Ghost word game",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pikulet/ghost",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
