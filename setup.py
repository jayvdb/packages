# Copyright 2015-2017 Louis Paternault
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Installer"""

from setuptools import setup, find_packages
import codecs
import os


def readme():
    directory = os.path.dirname(os.path.join(os.getcwd(), __file__))
    with codecs.open(
        os.path.join(directory, "README.rst"),
        encoding="utf8",
        mode="r",
        errors="replace",
    ) as file:
        return file.read()


setup(
    name="sphinxcontrib-packages",
    version="1.0.1",
    packages=find_packages(exclude=["test*"])
    + [
        "sphinxcontrib.packages"
    ],  # TODO: Remove this line when bug https://github.com/pypa/setuptools/issues/97 is fixed.
    setup_requires=["hgtools"],
    install_requires=["sphinx"],
    include_package_data=True,
    author="Louis Paternault",
    author_email="spalax@gresille.org",
    description="This packages contains the Packages sphinx extension, which provides directives to display packages installed on the host machine",
    url="https://git.framasoft.org/spalax/sphinxcontrib-packages",
    project_urls={
        "Documentation": "http://packages.readthedocs.io",
        "Source": "https://framagit.org/spalax/sphinxcontrib-packages",
        "Tracker": "https://framagit.org/spalax/sphinxcontrib-packages/issues",
    },
    license="AGPLv3 or any later version",
    test_suite="test.suite",
    keywords="sphinx packages system",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Sphinx :: Extension",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Documentation :: Sphinx",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    long_description=readme(),
    zip_safe=False,
)
