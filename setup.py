from setuptools import setup, find_packages

setup(
    name="todayi",
    version="0.0.1",
    author="Brighton Balfrey",
    author_email="balfrey@usc.edu",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "todayi = todayi.__main__:main",
        ],
    },
    install_requires=[
        "SQLAlchemy==1.3.20",
        "Jinja2==2.11.2",
        "google-cloud-storage==1.33.0",
        "requests==2.25.0",
    ],
)
