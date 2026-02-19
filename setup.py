#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="openclaw-vikingfs",
    version="0.1.0",
    author="二狗 (Tony Stark)",
    author_email="",  # GitHub会自动使用GitHub noreply邮箱
    description="基于OpenViking思想的轻量级上下文管理框架，专为OpenClaw优化设计",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/952800710/openclaw-vikingfs",
    packages=find_packages(where=".", exclude=["tests", "tests.*", "config", "config.*"]),
    package_dir={"": "."},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Archiving",
        "Topic :: Text Processing :: General",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "black>=23.0",
            "isort>=5.12",
            "pytest>=7.0",
            "pytest-cov>=4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "vikingfs=viking.integration.bridge_v2:main",
        ],
    },
    include_package_data=True,
    keywords=[
        "openclaw",
        "viking",
        "context-management",
        "memory-compression",
        "token-optimization",
        "ai-assistant",
    ],
    project_urls={
        "Bug Reports": "https://github.com/tonysatrk/openclaw-vikingfs/issues",
        "Source": "https://github.com/tonysatrk/openclaw-vikingfs",
        "Documentation": "https://github.com/tonysatrk/openclaw-vikingfs#readme",
    },
)