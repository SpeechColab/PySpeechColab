from pathlib import Path

from setuptools import find_packages, setup

project_root = Path(__file__).parent

install_requires = (project_root / 'requirements.txt').read_text().splitlines()
extras_require = {'test': ['pytest']}
extras_require['dev'] = extras_require['test']

setup(
    name='speechcolab',
    version='0.0.2-alpha',
    python_requires='>=3.6.0',
    description='A library of speech gadgets.',
    author='The SpeechColab Development Team',
    long_description=(project_root / 'README.md').read_text(),
    long_description_content_type="text/markdown",
    license='Apache-2.0 License',
    packages=find_packages(),
    install_requires=install_requires,
    extras_require=extras_require,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Intended Audience :: Science/Research",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed"
    ],
)
