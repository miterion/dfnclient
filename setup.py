from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
        name='dfnclient',
        version='0.4.9',
        license='MIT',
        description='Certificate client based on the soap API of the dfn',
        install_requires =['click==8.3.1', 'termcolor==3.2.0', 'suds-py3==1.4.5.0', 'cryptography==46.0.3'],
        packages=find_packages(),
        long_description=long_description,
        long_description_content_type="text/markdown",
        url='https://github.com/Miterion/dfnclient',
        entry_points={
            'console_scripts': [
                'dfnclient=dfngen.dfnclient:cli',
            ],
        }
)
