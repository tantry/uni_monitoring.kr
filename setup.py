from setuptools import setup, find_packages

setup(
    name="uni_monitoring",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'requests>=2.28.0',
        'beautifulsoup4>=4.11.0',
        'pyyaml>=6.0',
        'python-telegram-bot>=20.0',
    ],
    python_requires='>=3.8',
)
