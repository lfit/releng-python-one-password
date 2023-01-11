# -*- code: utf-8 -*-
# SPDX-License-Identifier: EPL-1.0
##############################################################################
# COPYRIGHT
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
##############################################################################

import os
from setuptools import find_packages, setup

with open("requirements.txt") as f:
    f.readline()  # Skip the first requirements.txt line
    install_reqs = f.read().splitlines()

setup(
    setup_requires=[ "click" ],
    pbr=True,
    install_requires=install_reqs,
    packages=find_packages(),
)
