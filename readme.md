# README

Parrotbot is simple lightweight self hosted solution for automatization of daily reports routine.

### Deployment guide(Linux)

#### Important detail. Don't skip.
This bot is for personal use only. It shouldn't be published in Slack App Repositories
because it designed to be used privately for single workspace therefore it doesn't contain
authorization system which can determine different workspace users therefore it will treat
all registered users as members of the same workspace which will result in unauthorized
access to private data.

**I repeat. This bot is only for private single workspace use. Publishing it will lead to unauthorized access to private data.**

Security of the bot is the same as generic Slack user has, because bot uses **RTM** which is technically UIless Slack client.

#### Deployment
1. Go to [Create Slack App page](https://api.slack.com/apps?new_app=1) and create app. Select your workspace as development workspace. Then under **OAuth & Permissions** of the newly created app find **Bot User OAuth Access Token**.
1. Install packer, make
1. CD to project root
1. Create .env file and copy content of the template.env file. Replace BOT_TOKEN_PLACEHOLDER with previously obtained **Bot User OAuth Access Token**
1. Get **Github** deploy key.
1. CD to project root/deploy
1. Run **make build-ami** this will build image for bot server instance.
1. Create ec2 instance using previously built ami.
1. Get ssh identity file(key) for previously created instance.
1. Get ec2 public host or ip.
1. Create keys directory. Default is **~/.ssh/parrotbot**
1. Copy identity file to keys directory as **key**
1. Copy Github deploy to keys directory as **deploy**
1. In keys directory create single line file **host** and insert host name or ip of the ec2 instance to it.
1. CD project root/deploy
1. Run make upload-project. Follow instructions.
1. Run make start-bot.
1. Read project root/deploy/makefile to find additional functionality. Everything is pretty self-explanatory.
1. ???
1. PROFIT!!!

### Bot initialization guide:
Bot uses its private channel as CLI, therefore all commands should be ran through it.
1. Once bot is deployed you need to run one command to synchronize it with **Slack** workspace users. Run `update sub`. Bot will respond with available **subscribers(workspace users)** list which you can use in the next stage.
1. Run `create quest`. You must be slack or bot_admin to use this command. To set subscriber as bot_admin run `set sub bot_admin true <sub_name>` This command is interactive. It will ask you to provide a file with new questionnaire data.
```json
  {
    "name":"daily",
    "title":"Daily",
    "expiration":"6:00",
    "retention":5,
    "questions":[
      "What was you doing yesterday?",
      "What are you going to do today?",
      "What is a chance that everything will not go as planned?"
    ],
    "subscribers":[
      "subscriber1",
      "subscriber2"
    ],
    "schedule":[
      {"start":1, "end":2, "time":"20:00"},
      {"start":3, "end":5, "time":"18:00"}
    ]
  }
```
  * name(required) - UID of the questionnaire.
  * title(required) - Display name of the questionnaire.
  * expiration(optional) - Determine how much time subscriber has to provide report answers until it expires. Default day end. Report expires tomorrow `00:00`.
  * retention(optional) - How many days reports kept in database after expiration. Default is 2 days.
  * questions(required) - List of questions.
  * subscribers(required) - names(UIDs) of subscribers who should be subscribed to this questionnaire upon creation. Subscriber names can be viewed via `ls sub` command.
  * schedule(optional) - List of weekday intervals with time of report request.  Note weekday intervals can't intersect therefore bot can't request specific questionnaire reports more than once per day. If schedules was empty or undefined questionnaire will not request reports automatically, only manually using `create report` command.
  If creation was successful bot will send request reports from the subscribers according to the schedule. You can add as many questionnaires as you want.
1. Questionnaire parameters can be updated by `update quest` command. It will ask to provide update file.
  Questionnaire update file can contain same fields as create file, except questions field, because changing questions is equal to questionnaire recreation, therefore you should run `delete quest <quest_name>` and `create quest` to create new questionnaire. Note that existing reports will be deleted. Name field defines which questionnaire should be updated by this file.
```json
{
  "name":"daily",
  "title":"Updated Daily",
  "subscribers":[
    "subscriber1",
    "subscriber3"
  ],
  "schedule":[
    {"start":1, "end":7, "time":"20:00"}
  ]
}
```

### Using bot
1. **Slack** or bot admins commands:
  * `update sub` - updates subscribers cache. Run if new user added/removed to/from workspace.
  * `create quest` - Run to create new questionnaire.
  * `delete quest <quest_name,...>` - Run to completely delete questionnaire and related reports.
  * `update quest` - Run to change questionnaire creation parameters.
  * `set quest active <value> <quest_name,...>` - Run to deactivate questionnaire which prevents report request from it.
  * `set subscr quest <quest_name> active <value> <sub_name,...>` and `set subscr sub <sub_name> active <value> <quest_name,...>` activate/deactivate subscriptions. Prevents report requests for specified subscriptions.
  * `set sub active <value> <sub_name,...>` activate/deactivate subscriber. May be used to stop report requests from specified subscribers. Designed to be used if sub is on vacation or can't/shouldn't temporarily receive report requests.
  * `set sub bot_admin <value(boolean)> <sub_name,...>`
  grant/remove bot admin rights to not slack admin user.
  * `ls report quest <max_age_days> <quest_name,...>` list all reports not older than N days for specified questionnaires
  * `ls report sub <max_age_days> <sub_name,...>` list all reports not older than N days for specified subscribers.
  * `ls sub` list all subscribers in subscriber cache.
  * `ls subscr <quest_name>` list subscriptions of specified questionnaire
  * `ls question <quest_name>` list questions of specified questionnaire.
  * `ls quest` list all questionnaires.
1. Non admin users commands:
  * `update report` provide answers in interactive mode for all pending questionnaires. Answer messages can be edited if report did not expire yet. Edit works through native Slack message edit functionality.
