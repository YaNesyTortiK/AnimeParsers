from setuptools import setup

setup(
    name="anime_parsers_ru",
    version="1.9.3",
    author="YaNesyTortiK",
    author_email="ya.nesy.tortik.email@gmail.com",
    maintainer="YaNesyTortiK",
    maintainer_email="ya.nesy.tortik.email@gmail.com",
    description="Python package for parsing russian anime players",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/YaNesyTortiK/AnimeParsers",
    download_url="https://pypi.python.org/pypi/anime_parsers_ru",
    keywords=["anime", "parser", "kodik", "parsing", "aniboom", "animego", "jutsu", "shikimori", "аниме", "парсинг", "кодик", "парсер", "анибум", "анимего", "джутсу", "шикимори"],
    install_requires=[
        "beautifulsoup4>=4.12",
        "requests>=2.32"
    ],
    extras_require={
        "async": ["aiohttp>=3.9.5"],
        "lxml": ["lxml>=5.2"]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["anime_parsers_ru"],
    license="MIT",
    license_file="LICENSE",
)