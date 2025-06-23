from setuptools import setup, find_packages

setup(
    name='aws-genai-bot-cli',
    version='1.0.0',
    description='CLI tool for AWS GenAI Bot',
    author='Roxanne Wang',
    packages=find_packages(),
    install_requires=[
        'click>=8.0.0',
        'requests>=2.28.0',
        'pyyaml>=6.0',
        'rich>=13.0.0',
        'python-dotenv>=1.0.0',
    ],
    entry_points={
        'console_scripts': [
            'genai=cli.main:cli',
        ],
    },
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)