from setuptools import setup, find_packages


def readme():
    with open("README.md", "r") as f:
        return f.read()


setup(
    name="moe-players",
    version="2024.11.1",
    author="nichind",
    author_email="nichinddev@gmail.com",
    description="Async aniboom/kodik player parser",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/nichind/moe-players",
    packages=find_packages(),
    install_requires=["aiohttp", "python-dotenv", "beautifulsoup4"],
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
