from setuptools import find_packages, setup

setup(
    name='data-droid-sdk',
    setup_requires=['wheel'],
    packages=find_packages(),
    include_package_data=True,
    version='0.0.2',
    description='Data Factory Library from Doctor Droid to fetch data from various sources',
    author='Mohit Goyal',
    author_email="mohit.goyal@drdroid.io",
    license='MIT',
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'awscli==1.33.35',
        'azure-identity==1.17.1',
        'azure-mgmt-loganalytics==12.0.0',
        'azure-monitor-query==1.4.0',
        'boto3==1.34.148',
        'clickhouse-connect==0.7.18',
        'Command==0.1.0',
        'datadog-api-client==2.26.0',
        'elasticsearch==8.14.0',
        'google==3.0.0',
        'google-api-python-client==2.139.0',
        'gql==3.5.0',
        'grpc-tools==0.0.1',
        'grpcio-tools==1.65.1',
        'kubernetes==30.1.0',
        'mypy-protobuf==3.6.0',
        'paramiko==3.4.0',
        'pipdeptree==2.23.1',
        'psycopg2-binary==2.9.9',
        'pytest==8.3.1',
        'SQLAlchemy==2.0.31',
        'toml==0.10.2',
        'twine==5.1.1',
        'wheel==0.37.1',
    ]
)
