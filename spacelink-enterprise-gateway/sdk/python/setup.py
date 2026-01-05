from setuptools import setup, find_packages

setup(
    name="spacelink",
    version="1.0.0",
    description="Python SDK for SpaceLink Enterprise Gateway",
    author="SpaceLink Team",
    packages=find_packages(),
    install_requires=[
        "requests>=2.32.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
