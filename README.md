# susdb

SusDB is a secure user string database system designed to manage and protect sensitive user data. This wiki serves as a guide to understanding SusDB's architecture, features, data security, and the post office metaphor that helps illustrate its functions.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Architecture](#architecture)
- [Data Security](#data-security)
- [Account Recovery](#account-recovery)
- [The Classical Post Office Story](#the-classical-post-office-story)
- [Testing SusDB locally using Docker](#running-locally)

## Introduction

SusDB is a secure and efficient database system built to manage sensitive user data. It focuses on securing user strings and enables data recovery when needed. It operates using a post office metaphor, where each user has a secured "box" to store their sensitive data.

For a detailed overview of SusDB, visit the [Introduction](https://github.com/Terre8055/sus-db/wiki) page.

## Features

SusDB boasts a set of essential features that ensure data privacy and security. These features include hashing user strings, integrity checks, data serialization, and account recovery management. Understanding these features is crucial for utilizing SusDB effectively.

Explore the full list of features on the [Features](https://github.com/Terre8055/sus-db/wiki/sus%E2%80%90db:-Secured-User-Strings-Database) page.

## Architecture

The architecture of SusDB revolves around securely storing user data and ensuring its integrity. The system uses a unique file-based approach for database management and a central repository (Redis) for critical resources. Learn how SusDB operates to protect user data.

Check out the [Architecture](https://github.com/Terre8055/sus-db/wiki/Data-Persistency-Architecture) page for a comprehensive understanding.

## Data Security

Data security is a top priority for SusDB. It relies on the Argon2 hashing algorithm to safeguard user strings, ensuring that sensitive information remains confidential. Frequent maintenance and backup procedures are in place to protect against data loss and corruption.

Visit the [Data Security](https://github.com/Terre8055/sus-db/wiki/Data-Security-and-Account-Recovery) page for a deep dive into how SusDB prioritizes your data's safety.

## Account Recovery

SusDB includes an account recovery system to assist users in regaining access to their data if they forget their user strings. This process involves verifying user identity and integrity checks to protect sensitive information.

Learn more about the account recovery process in the [Account Recovery](https://github.com/Terre8055/sus-db/wiki/Data-Security-and-Account-Recovery) section.

## The Classical Post Office Story

To help understand SusDB's operations, we've drawn a metaphor with a classical post office. Just like a post office assigns secure boxes and manages keys, SusDB uses file IDs to protect user data. Redis serves as a central repository, but it doesn't store data directly. This metaphor highlights SusDB's unique approach to data management.

Read the [Classical Post Office Story](https://github.com/Terre8055/sus-db/wiki/The-Classical-Post-Office-Story:-A-Metaphor-for-SusDB) for a creative perspective on SusDB's functions.

## Running Locally

### Using Docker Compose

For a more streamlined setup, consider using Docker Compose. This allows you to specify an environment file directly in your `docker-compose.yml`, making it easier to manage environment variables. Here’s a basic example of how to set it up:

```yaml
version: '3'
services:
  susdb:
    image: terre8055/susdb
    env_file: .env
```

## Running without external storage and server

If you prefer to use plain Docker commands, you can specify the environment file using the `--env-file` flag. Here’s how to run the `susdb` container with an environment file:

```bash
docker run --name <any-name> --env-file .env -v /path/to/home/sus-db/:/path/to/home/sus-db/ -it terre8055/susdb
```

This command will load the environment variables from the specified `.env` file, ensuring your container has the necessary configuration.

### Pull the `susdb` Container Image

To get the latest `susdb` container image from Docker Hub, run:

```bash
sudo docker pull terre8055/susdb
```

### Run the `susdb` Container

To run the `susdb` container and mount a volume for local access to log files and dbm, use the following command:

First, make sure this directory and file exists on your local machine

```bash
mkdir -p $HOME/sus-db/ && touch $HOME/sus-db/susdb.log
```
if you are running docker as rootless; 

```bash
docker run --name <any-name> -v /path/to/home/sus-db/:/path/to/home/sus-db/ -it terre8055/susdb 
```
else; add the sudo

This command mounts your local `$HOME/sus-db` directory to the container's `$HOME/sus-db` directory, enabling access to log files and dbm.

### Store User Data

To store user data using `susdb`, run the following command:

```bash
docker run --name tiger-woodye -v /path/to/home/sus-db/:/path/to/home/sus-db/ -it terre8055/susdb  python /app/src/susdb_cli.py store --string='Mike'
```
A unique id will be generated used to access for local dbs
Replace `<user_string: str>` with the actual user string you want to store.

### Deserialize and Retrieve User Data

To retrieve user data using `susdb`, run the following command:

```bash
docker run --name tiger-woodye -v /path/to/home/sus-db/:/path/to/home/sus-db/ -it terre8055/susdb  python /app/src/susdb_cli.py retrieve --key=<data_to_retrieve: str> --uid=<uid: str>
```

Replace `<uid: str>` with the generated unique id after storing your string.
Replace `<key: str>` with the actual user data you want to retrieve.

### Display contents of user db

To display user db using `susdb`, run the following command:

```bash
docker run --name tiger-woodye -v /path/to/home/sus-db/:/path/to/home/sus-db/ -it terre8055/susdb  python /app/src/susdb_cli.py python /app/src/susdb_cli.py view --uid=<uid: str>
```

Replace `<uid: str>` with the generated unique id after storing your string.

### Verify Credentials

To verify user cred using `susdb`, run the following command:

```bash
docker run --name tiger-woodye -v /path/to/home/sus-db/:/path/to/home/sus-db/ -it terre8055/susdb  python /app/src/susdb_cli.py python /app/src/susdb_cli.py verify --string=<user_string: str> --uid=<uid: str>
```


Replace `<uid: str>` with the generated unique id after storing your string.
Replace `<user_string: str>` with the actual user string.


## Environment Variables

The following table explains the values that need to be set in the `.env` file:

| Variable Name              | Description                                                                                     | Example Value                |
|----------------------------|-------------------------------------------------------------------------------------------------|-------------------------------|
| `FILE_NAME`                | The name of the file to be used.                                                               | `my_database_file`        |
| `GET_PATH`                 | The path where the file is located.                                                            | `/path/to/my/file`           |
| `LOG_PATH`                 | The path where log files will be stored.                                                       | `/path/to/logs/susdb.log`    |
| `SSDB_EXTERNAL_SUPPORT`     | Indicates whether to store the database file locally or externally using S3 (true/false).     | `true` or `false`            |
| `AWS_ACCESS_KEY_ID`       | Your AWS access key ID for S3 access.                                                          | `AKIA...`                    |
| `AWS_SECRET_ACCESS_KEY`   | Your AWS secret access key for S3 access.                                                      | `wJalr...`                   |
| `AWS_REGION`               | The AWS region where your S3 bucket is located.                                               | `us-west-2`                  |
| `S3_BUCKET_NAME`           | The name of your S3 bucket where the database file will be stored if using external support.  | `my-s3-bucket`               |


## Conclusion

SusDB is designed to secure and manage sensitive user data efficiently. Its unique architecture and security features make it an ideal choice for applications that require privacy and data protection. Explore the wiki to learn how to utilize SusDB effectively and ensure the security of your user data.

![sus_db_design](images/arch.png)

Find docs here [SUS-DB Documentation](https://github.com/Terre8055/sus-db/wiki)


Issues are welcome and will be resolved as early as possible

