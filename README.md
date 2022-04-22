# target-google-ads
A Singer (https://singer.io) target that writes data to Google Ads.

This is a [Singer](https://singer.io) loader that writes data to Google Ads API following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

This tap: 

- Writes data to the [Google Ads API](https://developers.google.com/google-ads/api/docs/start). 

[![Python package](https://github.com/DTSL/target-google-ads/actions/workflows/python-package.yml/badge.svg)](https://github.com/DTSL/target-google-ads/actions/workflows/python-package.yml)

## Contents

- [Contact](#contact)
- [Dependencies](#dependencies)
- [How to use it](#how-to-use-it)
- [Unit tests set up](#unit-tests-set-up)
- [Config files in this project](#config-files-in-this-project)

## Contact

Email: `deke.li@sendinblue.com`

## Dependencies

Install requirements, using either of the two methods below.

**Method 1**
```
pip install -r requirements.txt 
```

**Method 2**

Alternatively, you can run the following command. It runs *setup.py* and installs target-bigquery into the env like the user would. **-e** emulates how a user of the package would install requirements.
```
pip install -e .
```
**Additional development and testing requirements**

Install additional dependencies required for development and testing. 
```
pip install -r dev-requirements.txt
```

## How to use it


## Unit tests set up

Add the following files to *sandbox* directory under project root directory:
- **target-config.json**: 
```
{
    "developer_token": "frfdqsfeDFZEFD",
    "oauth_client_id": "fqdsF342-sfqsdfeaa32432.apps.googleusercontent.com",
    "oauth_client_secret": "DSFRT4RDFGesfzer",
    "refresh_token": "1//03AumSAfqsdfqsf-qsdfqsdfrzetgb-f-dqfqsdfze-thgf-dqsfdfh-37A",
    "api_version": "v10",
    "customer_ids": [
        {"customerId": 23456434, "conversion_action_id": [2345325535]}
    ],
    "offline_conversion": "dummy_conversion"
}
```

---

Copyright &copy; 2022 Sendinblue
