## Django backend

### Launching

#### Step 1: clon repo:

For user key:

``git clone https://github.com/codesshaman/posts_generator_back.git``

For special or corporate key:

``git clone github-repo:codesshaman/posts_generator_back.git``

Go inside directory:

``cd posts_generator_back``

#### Step 2: create .env file:

``make env``

Change file:

``nano .env``

Change debug, database options and settings.

Set your git login and email and launch:

``make git``

Set other variables. Do not touch .env.example!

#### Step 3: create python environment:

Create environment:

``make venv``

Install all requrements:

``make req``

#### Step 4: launch project:

``make``

Enjoy!