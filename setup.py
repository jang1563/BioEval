from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bioeval",
    version="0.2.0",
    description="Multi-dimensional Evaluation of LLMs for Biological Research",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="JangKeun Kim",
    author_email="jang1563@gmail.com",
    url="https://github.com/jang1563/BioEval",
    project_urls={
        "Bug Tracker": "https://github.com/jang1563/BioEval/issues",
        "Documentation": "https://github.com/jang1563/BioEval#readme",
        "Source Code": "https://github.com/jang1563/BioEval",
    },
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "anthropic>=0.18.0",
        "openai>=1.0.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "scikit-learn>=1.3.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "tqdm>=4.65.0",
        "pyyaml>=6.0",
        "requests>=2.28.0",
        "jupyter>=1.0.0",
        "aiohttp>=3.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Operating System :: OS Independent",
    ],
    keywords="llm, evaluation, biology, bioinformatics, nlp, machine-learning, benchmark",
    entry_points={
        "console_scripts": [
            "bioeval=bioeval.cli:main",
        ],
    },
)
