# websocket-step-function

This demo application show how to use WebSockets over API Gateway to publish the state of long-running interactions to a client.

The long running task is simulated by a step function.

## Run the application

Deploy the application.
```
serverless deploy
```

Kick off the long-running tasks (step function)
```
http POST  https://<your-api-gateway-id>.execute-api.eu-central-1.amazonaws.com/dev/tasks
```

Copy the `taskId` from the response and establish the connection to the WebSocket API

```
websocat  wss://<your-websocket-api-id>.execute-api.eu-central-1.amazonaws.com/dev
```

Send a message to the server by pasting the `taskId` into the terminal.

After the long-running interaction has finished the server sends a message in turn that indicated the status of the interaction.
