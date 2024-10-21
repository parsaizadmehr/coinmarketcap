# Coinmarketcap

## Overview
This project is built using a template sourced from [GitHub](https://github.com/ade555/telegram-bot-starter-kit), with custom configurations for environment variables, database migrations using Alembic. 

## Features
- Fetch data through [api](https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listing)
- Crawl data from [Coinmarketcap Historical](https://coinmarketcap.com/historical)
- Show data in Telegram Chatbot

## Prerequisites
- Python 3.x
- PostgreSQL/MySQL (depending on your database choice)

## Setup

### Step 1: Clone the Repository
Clone this project from GitHub:

```bash
git clone https://github.com/parsaizadmehr/coinmarketcap.git
cd coinmarketcap
```

### Step 2: Environment & Install requirements.txt
```bash
virtualenv .venv

.\.venv\Scripts\activate (windows)
source .venv\script\activate (Linux)
```
#### Install requirements.txt
```bash
pip install -r requirements.txt
```
#### Environments
```bash
cp alembic.ini.sample alembic.ini
```
And Change this line
`sqlalchemy.url = postgresql://postgres:user@ip:port/database`

```bash
cp .env.sample .env
```
Set the database config and telegram bot token

#### Make migrations
```bash
alembic upgrade head
```
