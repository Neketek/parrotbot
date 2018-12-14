from pprint import PrettyPrinter
from collections import abc
import requests


class Context:

    def __init__(self, client, message, next=None):
        self.client = client
        self.message = message
        self.next = next
        self.text = message.get('text')
        self.user = message.get('user')
        self.channel = message.get('channel')
        self.files = message.get('files', [])
        self.file = self.files[0] if len(self.files) > 0 else None

    def load_file_request(self, slack_file=None):
        slack_file = self.file if slack_file is None else slack_file
        return requests.get(
            slack_file['url_private_download'],
            headers=dict(
                Authorization='Bearer {0}'.format(self.client.token)
            )
        )

    def reply(self, text):
        return self.send(self.channel, text)

    def send(self, channel, text):
        return self.client.api_call(
            'chat.postMessage',
            channel=channel,
            text=text
        )

    @property
    def command(self):
        try:
            return self.__command
        except AttributeError:
            args = self.command_args
            self.__command = args[0] if len(args) > 0 else None
            return self.__command

    @property
    def command_args(self):
        try:
            return self.__command_args
        except AttributeError:
            self.__command_args = tuple(self.text.strip(' ').lower().split())
            return self.__command_args

    @property
    def cs_command_args(self):
        try:
            return self.__cs_command_args
        except AttributeError:
            self.__cs_command_args = tuple(self.text.strip(' ').split())
            return self.__cs_command_args

    @property
    def is_user_message(self):
        try:
            return self.__is_user_message
        except AttributeError:
            self.__is_user_message = not (
                self.user is None
                or self.channel is None
                or self.text is None
            )
            return self.__is_user_message

    def interactive(self, next_data=None):
        return next_data


def update_func_name(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    module = func.__module__.split('.')
    name = func.__name__
    if name == module[-1]:
        wrapper.__name__ = func.__module__
    else:
        wrapper.__name__ = '.'.join(module+[name])
    return wrapper


class __Actions:

    def __init__(
        self
    ):
        self.listeners = []
        self.interactive = []  # interactive commands

    def __start_interactive(
        self,
        func,
        message,
        next
    ):
        self.interactive.append(
            dict(
                func=func,
                next=next,
                channel=message['channel']
            )
        )

    def __continue_interactive(self, client, message):
        user = message.get('user')
        text = message.get('text')
        channel = message.get('channel')
        if user is None or text is None or channel is None:
            return False
        target = None
        for i in self.interactive:
            if i['channel'] == channel:
                target = i
                break
        if target is None:
            return False
        result = target['func'](Context(client, message, next=target['next']))
        if result is None:
            self.interactive.remove(target)
        else:
            target['next'] = result
        return True

    def __continue_non_interactive(self, client, message):
        context = Context(client, message)
        for l in self.listeners:
            if l['condition'](context):
                result = l['func'](context)
                if result is not None:
                    self.__start_interactive(l['func'], message, result)
                break

    def __register(self, condition, func):
        func = update_func_name(func)
        if condition is Conditions.default():
            self.listeners.append(
                dict(
                    condition=condition,
                    func=func
                )
            )
            return
        for l in self.listeners:
            if l['func'] is func:
                raise ValueError(
                    "Function {0} is already registered:".format(func.__name__)
                )
        self.listeners.insert(
            0,
            dict(
                condition=condition,
                func=func
            )
        )

    def register(self, condition):
        def decorator(func):
            self.__register(condition, func)
            return func
        return decorator

    def feed(self, client, messages):
        p = PrettyPrinter(indent=4)
        for m in messages:
            p.pprint(m)
            if not self.__continue_interactive(client, m):
                self.__continue_non_interactive(client, m)

    def __str__(self):
        res = "[\n"
        for l in self.listeners:
            res += " ({0}, {1})\n".format(
                l['func'].__name__,
                l['condition'].__name__
            )
        res += ']'
        return res


class Conditions:
    @staticmethod
    def __default_condition(c):
        return c.is_user_message

    @staticmethod
    def command(text, *args):
        def condition(c):
            command_match = False
            if not c.is_user_message or len(c.command_args) == 0:
                return False
            if isinstance(text, abc.Iterable):
                command_match = c.command_args[0] in text
            else:
                command_match = c.command_args[0] == text
            if command_match and len(args) > 0:
                if len(c.command_args) - len(args) < 1:
                    return False
                else:
                    expected_args = c.command_args[1:len(args)+1]
                    return expected_args == args
            else:
                return command_match
        if isinstance(text, abc.Iterable):
            condition.__name__ = "command {0}".format(text)
        else:
            condition.__name__ = "command '{0}'".format(text)
        if len(args) > 0:
            condition.__name__ += (" {}"*len(args)).format(*args)
        return condition

    @staticmethod
    def default():
        return Conditions.__default_condition


actions = __Actions()
