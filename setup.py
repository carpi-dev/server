from setuptools import setup, find_packages

setup(
    long_description_content_type="text/markdown",
    long_description=open("readme.md", "r").read(),
    name="carpi_server",
    version="0.1",
    description="carpi module server",
    author="Pascal Eberlein",
    author_email="pascal@eberlein.io",
    url="https://github.com/smthnspcl/carpi_server",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={
        'console_scripts': [
            'carpi_server = carpi_server.__main__:main'
        ]
    },
    keywords="carpi module server",
    packages=find_packages(),
)
