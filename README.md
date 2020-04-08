[![CircleCI](https://circleci.com/gh/GovWizely/lambda-steel/tree/master.svg?style=svg)](https://circleci.com/gh/GovWizely/lambda-steel/tree/master)
[![Maintainability](https://api.codeclimate.com/v1/badges/2bd83d33a78e7297be95/maintainability)](https://codeclimate.com/github/GovWizely/lambda-steel/maintainability)
[![Dependabot Status](https://api.dependabot.com/badges/status?host=github&repo=GovWizely/lambda-steel)](https://dependabot.com)

# Steel Data Lambda
This project provides an AWS Lambda that concatenates individual reporter country spreadsheets from one S3 bucket into a single file in another S3 bucket, and then invokes a special freshen AWS lambda to update an endpoint.  

## Prerequisites

- This project is tested against Python 3.7+ in [CircleCI](https://app.circleci.com/github/GovWizely/lambda-steel/pipelines).

## Getting Started

	git clone git@github.com:GovWizely/lambda-steel.git
	cd lambda-steel
	mkvirtualenv -p /usr/local/bin/python3.8 -r requirements-test.txt steel

If you are using PyCharm, make sure you enable code compatibility inspections for Python 3.7/3.8.

### Tests

```bash
python -m pytest
```

## Configuration

* Define AWS credentials in either `config.yaml` or in the [default] section of `~/.aws/credentials`. To use another profile, you can do something like `export AWS_DEFAULT_PROFILE=govwizely`.
* Edit `config.yaml` if you want to specify a different AWS region, role, and so on.
* Make sure you do not commit the AWS credentials to version control.

## Invocation

	lambda invoke -v
 
## Deploy
    
To deploy:

	lambda deploy --requirements requirements.txt
