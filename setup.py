from setuptools import setup
# call point for the project is shinchan to change it one needs to replace shinchan with the required name.

setup(
    name='flask-cli-tool',
    version='0.1',
    py_modules=['cli_tools'],
    install_requires=[
        'Click',
        'requests',
    ],
    entry_points='''
        [console_scripts]
        shinchan=cli_tools:cli
    ''',
)
