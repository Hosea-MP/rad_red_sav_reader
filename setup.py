from setuptools import setup, find_packages

setup(
    name="rr_parser",
    version="1.0",
    description="Radical Red savegame editor.",
    url="https://gitlab.com/IppSD/radicalred-savegame-editor",
    author="Imanol Sardón Delgado",
    author_email="sardondelgadoimanol@gmail.com",
    license="MIT",
    classifiers=[
        'Development Status :: 5 - Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords="pokemon radical red radicalred editor",
    packages=find_packages(include=["rr_parser", "rr_parser.*"]),
    install_requires=[
        "pokebase>=1.3.0"
    ],
    python_requires=">=3.7"

)
