from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_desc = f.read()

setup(
    name="langchain-light",
    version="2.0.0",
    description="轻量级AI Agent编排框架 - 10行代码启动Agent",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    author="牧云野",
    packages=find_packages(exclude=["examples*", "docs*", "tests*"]),
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "full": ["openai>=1.0.0"],
    },
    entry_points={
        "console_scripts": [
            "lcl=langchain_light.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
