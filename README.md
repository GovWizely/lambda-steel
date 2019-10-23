# Steel Data Lambda

This project provides an AWS Lambda that concatenates individual reporter country spreadsheets into one.  

## Prerequisites

Follow instructions from [python-lambda](https://github.com/nficano/python-lambda) to ensure your basic development environment is ready,
including:

* Python
* Pip
* Virtualenv
* Virtualenvwrapper
* AWS credentials

## Getting Started

* git clone git@github.com:GovWizely/lambda-steel.git
* cd lambda-steel
* mkvirtualenv -r requirements.txt lambda-steel

## Configuration

* Define AWS credentials in either `config.yaml` or in the [default] section of ~/.aws/credentials.
* Edit `config.yaml` if you want to specify a different AWS region, role, and so on.
* Make sure you do not commit the AWS credentials to version control

## Invocation

  lambda invoke -v
 
## Deploy

  lambda deploy
