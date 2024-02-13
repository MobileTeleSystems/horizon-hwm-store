# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import os
from pathlib import Path

from setuptools import find_packages, setup

here = Path(__file__).parent.resolve()


def get_version():
    if os.getenv("GITHUB_REF_TYPE", "branch") == "tag":
        return os.environ["GITHUB_REF_NAME"]

    version_file = here / "horizon_hwm_store" / "VERSION"
    version = version_file.read_text().strip()  # noqa: WPS410

    build_num = os.environ.get("GITHUB_RUN_ID", "0")
    branch_name = os.environ.get("GITHUB_REF_NAME", "")

    if not branch_name:
        return version

    return f"{version}.dev{build_num}"


def parse_requirements(file: Path) -> list[str]:
    lines = file.read_text().splitlines()
    return [line.rstrip() for line in lines if line and not line.startswith("#")]


requirements = parse_requirements(here / "requirements.txt")
long_description = (here / "README.rst").read_text()

setup(
    name="horizon-hwm-store",
    version=get_version(),
    author="DataOps.ETL Team",
    author_email="onetools@mts.ru",
    description="onETL Plugin for Horizon store",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    license="Apache License 2.0",
    license_files=("LICENSE.txt",),
    url="https://github.com/MobileTeleSystems/horizon-hwm-store",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries",
        "Typing :: Typed",
    ],
    project_urls={
        "Documentation": "https://horizon-hwm-store.readthedocs.io/",
        "Source": "https://github.com/MobileTeleSystems/horizon-hwm-store",
        "CI/CD": "https://github.com/MobileTeleSystems/horizon-hwm-store/actions",
        "Tracker": "https://github.com/MobileTeleSystems/horizon-hwm-store/issues",
    },
    keywords=["ETL", "Horizon", "HWM"],
    entry_points={
        "etl_entities.plugins": ["horizon-hwm-store=horizon_hwm_store"],
        "tricoder_package_spy.register": ["horizon-hwm-store=horizon_hwm_store"],
    },
    packages=find_packages(exclude=["docs", "docs.*", "tests", "tests.*"]),
    python_requires=">=3.7",
    install_requires=requirements,
    include_package_data=True,
    zip_safe=False,
)
