![Lint-free](https://github.com/software-students-spring2025/5-final-let-s-get-it-over-with/actions/workflows/lint.yml/badge.svg)
![CD-Digitial Ocean](https://github.com/software-students-spring2025/5-final-let-s-get-it-over-with/actions/workflows/deploy.yml/badge.svg)
![ML-CLient CI](https://github.com/software-students-spring2025/5-final-let-s-get-it-over-with/actions/workflows/ml-client.yml/badge.svg)
![Web-app CI](https://github.com/software-students-spring2025/5-final-let-s-get-it-over-with/actions/workflows/web-app.yml/badge.svg)
# Final Project

# 👾 Fake It Till You Make It: AI-Powered Livestream Simulator

This is a Twitch-style live-stream simulator where AI chatbots stand in for human viewers 
which is ideal for boosting social credit, building confidence, or simulating a streaming presence before going live.
So whether you’re rehearsing a broadcast, giving your setup a test run, or just having fun, there’s always an audience waiting for you.

## Overview:

This application is split into three subsystems with each one running in their own container:

1. **ML-client**: grabs webcam frames and sends them to the OpenAI API for image and speech recognition.
2. **Web-app**: lets users run a Twitch-style live-stream simulation.
3. **MongoDB Atlas**: stores data produced by the ML-client and Web-app.

## Team Members

1. [Jasmeen Kaur](https://github.com/jk7297)
2. [Preston Lee](https://github.com/prestonglee0805)
3. [Andy Cabindol](https://github.com/andycabindol)
4. [David Yu](https://github.com/DavidYu00)

## Docker Images

Our containerized applications are available on Docker Hub:

- [ML-Client](https://hub.docker.com/r/jasmeen30/fake-it-till-you-make-it-ml-client)
- [Web App](https://hub.docker.com/r/jasmeen30/fake-it-till-you-make-it-web-app)

## Deployed application

This web application is deployed and accessible at:
- [https://fakeittillyoumakeit.live](https://fakeittillyoumakeit.live/auth/login)

## Developer's Guide

### Setup and Installation

1. Clone the Repository:
```
git clone git@github.com:software-students-spring2025/5-final-let-s-get-it-over-with.git
```
2. Navigate into the Project Directory:
```
cd 5-final-let-s-get-it-over-with
```
3. Ensure pip and pipenv are Installed and Up to Date
```
python -m pip install --upgrade pip
pip install pipenv
```
4. Install Dependencies:
- ML Client
```
cd ml-client
pipenv install
```
- Web App
```
cd ../web-app
pipenv install
```

### Environment Variables

Both the ML Client and Web App uses environment variables stored in .env file to connect to MongoDB Atlas and OpenAI API

- Setup your .env file in the root directory:
1. Create a new .env file:
```
touch env
```
2. Open it and add your MongoDB details [(env.example file)]():
```
MONGO_URI=your_mongo_uri_here
MONGO_DBNAME=your_mongodb_database_name_here
OPENAI_API_KEY=your_openai_api_here
```

### Database Initialization

The database is automatically initialized with default categories when the application starts.

### Docker Setup - Install and Run

In order to build and run this system in a containerized environment, you need to install docker first:

1. Install the [Docker Desktop client.](https://www.docker.com/products/docker-desktop/)
2. Create an acount at [Docker Hub.](https://hub.docker.com)
3. Once Docker Desktop is installed, run it.
4. Then, open up a terminal and log in to Docker Hub with docker login

To Run All Containers Together (The Complete System)

1. From the project root:
```
cd 5-final-let-s-get-it-over-with
docker-compose up --build
```
2. Then visit http://localhost:5001 in your web browser to start streaming
3. When you're done, shut everything down cleanly with:
```
docker-compose down
```
This stops and removes all running containers and releases system resources.

### Development Workflow:

1. Once the Repository is cloned from github, create a feature branch for your changes:
```
git checkout -b your-branch-name
```
2. Make changes and commit by running this command below:
```
git add .
git commit -m "your_commit_message_here"
```
3. Push your changes to you remote branch
```
git push origin your-branch-name
```
4. Create a pull request
5. Get code review from at least one team member
6. Merge after approval

### Testing:

All unit tests must pass before merging any changes. Simply run the following commands to test:
```
cd ml-client
python -m pytest tests/

cd web-app
python -m pytest tests/
```

