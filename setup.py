from setuptools import setup, find_packages

setup(
    name="opensword-browser",
    version="0.1.0",
    description="Open-source AI-native web browser",
    author="hiimhermes-self",
    license="Apache-2.0",
    packages=find_packages(),
    install_requires=["PySide6>=6.5.0"],
    python_requires=">=3.10",
    entry_points={"console_scripts": ["opensword=opensword.browser:main"]},
)
