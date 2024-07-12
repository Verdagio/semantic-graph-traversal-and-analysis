from setuptools import setup, find_packages

setup(
    name="semantic-graph-traversal-and-analysis",
    version="0.1.0",
    description="A graph traversal and analysis tool",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Verdagio/semantic-graph-traversal-and-analysis",
    author="Daniel Verdejo",
    author_email="dverdagio@gmail.com",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn[standard]",
        "pydantic",
        "numpy",
        "openai",
        "nltk",
        "transformers",
        "torch",
        "mistralai",
        "python-dotenv",
        "sentence-transformers",
        "scikit-learn",
        "networkx",
        "matplotlib",
        "langchain_core",
        "pandas",
        "ollama",
    ],
    entry_points={
        "console_scripts": [
            "semantic-graph-traversal-and-analysis=app.main:app",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10.13",
)