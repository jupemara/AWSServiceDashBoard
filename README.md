AWSServiceDashBoard
===================

Get all Amazon Web Service service status from http://status.aws.amazon.com/ by using RSS feed information. And this script can notice to some chat channel.

We don't use third-party python module. So you don't need to be afraid of breaking system python site-packages or other modules dependency.

We implemented below chats.

* Chatwork
* Slack


How to execute
--------------

1. Download this script.

```
git clone https://github.com/JumpeiArashi/AWSServiceDashBoard.git
```

2. Execute!

```
python main.py
```


Options
-------

You can use following options.

| Option name           | short hand | Detail |
|-----------------------|------------|--------|
| --help                | -h         | Show help message and exit. |
| --log-level           | -l         | Specify log level. |
| --duration            | -D         | Time duration. You can use some strings as duration suffix. |
| --region              | -R         | AWS Region name. You can specify mutilple regions by comma delimiter. |
| --chat-integration    | -C         | Chat integration. You can use "slack" or "chatwork". |
| --chat-api-token      | -k         | Chat API Token. |
| --chat-api-channel-id | -c         | Chat Channel ID. |

### Log Level

Specify below log levels.

* DEBUG
* INFO
* WARNING
* ERROR
* CRITICAL

If you want to get no log message, you can specify _CRITICAL_.

### Duration suffix

| suffix      | meaning |
|:------------|---------|
| d           | days    |
| h           | hours   |
| m           | minutes |
| **nothing** | seconds |

### Chat API Token

#### Case of Chatwork

It's so simple! Specify API Token.

#### Case of Slack

We use [Incoming Webhook](https://caadtech.slack.com/services/new/incoming-webhook) for implementation slack. So when you use slack integration, you must spcify _Incoming Webhook URL_ as `--chat-api-token` option.

```
# e.g
python main.py --chat-integration slack --chat-api-token https://hooks.slack.com/services/XXXXXXXXX/YYYYYYYYY/ZZZZZZZZZZZZZZZZZZZZZZZZ
```

And you must not specify `--chat-api-channel-id`.


Notes
-----

### Not specify `--chat-integration`

Default chat integration is `stdout`. So this script outputs below json message to `stdout'.

```
$python main.py --log-level CRITICAL --duratioon 1d  | jq .
[
  {
    "service_name": "route53",
    "guid": "http://status.aws.amazon.com/#route53_1418544000",
    "description": "We can confirm slow propagation of DNS edits to the Route 53 DNS servers and continue to work towards resolution. This does not impact queries to existing DNS records.",
    "pubDate": "2014-12-14 08:00:00",
    "title": "Service is operating normally: [RESOLVED] Slow propagation times "
  }
]
```
