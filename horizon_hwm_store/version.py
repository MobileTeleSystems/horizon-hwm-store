# SPDX-FileCopyrightText: 2023-2025 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
"""
__version__ parameter required to be able to output to the console
"""

from pathlib import Path

VERSION_FILE = Path(__file__).parent / "VERSION"

__version__ = VERSION_FILE.read_text().strip()  # noqa: WPS410
