# AUTO

**This is a proof of concept about how Multiagent Systems can be applied to self-driving cars in order to avoid potencial accidents.**

![img](https://raw.githubusercontent.com/iitzco/auto/master/auto.gif)

## Description

Cars communicate with each other exchanging information about their speed and position. Then, each car decides the correct action depending on the information it could collect from other cars.

#### Basic Architecture

This program was developed to be executed in a single thread environment. In each iteration, each car receives exclusive CPU time that need to be used to communicate with the environment and to update its state.

The communication flow is done through message queues following a Request/Response protocol. Each car contains a Request message queue and a Response message queue. The Request message queue will host all messages sent from other cars that the car needs to answer. The Response message queue hosts all responses from requests that the car did in the past processing.

Each car when it receives CPU time:

1. Process responses from other cars.
2. Answer requests that were done by other cars
3. Update its own state.
4. Sends requests to nearby cars.

## How to run

This is a Python 3 project with no special libs. Just download (or clone) the repo and you are good to go.

You will need a config file to configurate the city parameters. An example is provided in the `config.ini` file.

Run:

```
$ python3 main.py config.ini
```

If other config file is used, just invoke its filename as the second paramenter.

You should see this GUI:

![img](https://github.com/iitzco/auto/blob/master/auto.png?raw=true)

Where you can add new cars to the city and keep track of some interesting metrics.
