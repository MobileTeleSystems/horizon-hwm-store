from __future__ import annotations

import os
from pathlib import Path

from setuptools import find_packages, setup

here = Path(__file__).parent.resolve()


def get_version():
    if "CI_COMMIT_TAG" in os.environ:
        return os.environ["CI_COMMIT_TAG"]

    version_file = here / "horizon_hwm_store" / "VERSION"
    version = version_file.read_text().strip()  # noqa: WPS410

    build_num = os.environ.get("CI_PIPELINE_IID", "")
    branch_name = os.environ.get("CI_COMMIT_REF_SLUG", "")
    branches_protect = ["master", "develop"]

    if not branch_name or branch_name in branches_protect:
        return f"{version}.dev{build_num}"

    return f"{version}.dev{build_num}+{branch_name}"


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
    url="https://gitlab.services.mts.ru/bigdata/platform/onetools/horizon-hwm-store",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Data engineers",
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
        "Topic :: Software Development :: Libraries",
        "Typing :: Typed",
    ],
    project_urls={
        "Documentation": "https://bigdata.pages.mts.ru/platform/onetools/horizon-hwm-store/",
        "Source": "https://gitlab.services.mts.ru/bigdata/platform/onetools/horizon-hwm-store",
        "CI/CD": "https://gitlab.services.mts.ru/bigdata/platform/onetools/horizion-hwm-store/-/pipelines",
        "Tracker": "https://jira.mts.ru/projects/DOP/issues",
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
