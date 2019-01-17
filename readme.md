# README
Parrotbot is simple lightweight self hosted solution for automatization of daily reports routine.

### Deployment guide(Linux)

1. Go to **Slack** and obtain [BOT_TOKEN](https://api.slack.com/apps?new_app=1).  
2. On the host install docker, docker-compose, make
3. cd to project dir
4. Create file `.env` according to `template.env` file. Replace **BOT_TOKEN** value placeholder with previously obtained token.
5. Run `make dcdrun`. It will build&launch **parrotbot** server docker container in detached mode
6. ???
7. PROFIT!!!

### Bot initialization guide:
Bot uses its private channel as CLI, therefore all commands should be ran through it.
1. Once bot is deployed you need to run one command to synchronize it with **Slack** workspace users. Run `update sub`. Bot will respond with available **subscribers(workspace users)** list which you can use in the next stage.
2. Run `create quest`. You must be slack or bot_admin to use this command. To set subscriber as bot_admin run `set sub bot_admin true <sub_name>` This command is interactive. It will ask you to provide a file with new questionnaire data.
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
3. Questionnaire parameters can be updated by `update quest` command. It will ask to provide update file.
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
2. Non admin users commands:
  * `update report` provide answers in interactive mode for all pending questionnaires. Answer messages can be edited if report did not expire yet. Edit works through native Slack message edit functionality. 
