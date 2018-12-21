from pprint import PrettyPrinter
from collections import abc
import requests
from datetime import datetime
import threading

NO_INTENTIONAL_INTERACTIVE_EXCEPTION = """
Function should return instance of Context.Interactive to start/continue
interactive session or None to stop interactive session.
c.interactive(*args,**kwargs)
is shortcut to the
Context.Interactive(*args, **kwargs)
"""

DEFAULT_BYE_MSG = "Interactive session is over. I waited too long."

printer = PrettyPrinter(indent=4)


class Context(object):

    class Interactive(object):
        class NonIntentionalInteractive(Exception):
            def __str__(self):
                return NO_INTENTIONAL_INTERACTIVE_EXCEPTION

        def __init__(
            self,
            next=None,
            keep_alive=600,  # seconds
            bye_msg=DEFAULT_BYE_MSG
        ):
            self._next = next
            self._keep_alive = keep_alive
            self._bye_msg = bye_msg

        @property
        def next(self):
            return self._next

        @property
        def keep_alive(self):
            return self._keep_alive

        @property
        def bye_msg(self):
            return self._bye_msg

    def __init__(self, client, message, interactive=None):
        self.client = client
        self.message = message
        self.text = message.get('text')
        self.user = message.get('user')
        self.channel = message.get('channel')
        self.files = message.get('files', [])
        self.file = self.files[0] if len(self.files) > 0 else None
        self.i = interactive

    def load_file_request(self, slack_file=None):
        slack_file = self.file if slack_file is None else slack_file
        return requests.get(
            slack_file['url_private_download'],
            headers=dict(
                Authorization='Bearer {0}'.format(self.client.token)
            )
        )

    def reply_code(self, text, **kwargs):
        return self.reply(text, code_block=True, **kwargs)

    def reply(self, text, **kwargs):
        return self.send(self.channel, text, **kwargs)

    def send(self, channel, text, code_block=False, **kwargs):
        if code_block:
            text = "```{}```".format(text)
        return self.client.api_call(
            'chat.postMessage',
            channel=channel,
            text=text,
            **kwargs
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

    def interactive(self, *args, **kwargs):
        return Context.Interactive(*args, **kwargs)


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
        self.listeners = list()
        # interactive commands channels
        self.interactive = dict()
        # pending channels which wait for answer
        self.pending_channels_cmd = dict()

        self.interactive_lock = threading.RLock()
        self.pending_channel_cmd_lock = threading.RLock()

    def __start_interactive(
        self,
        message,
        func,
        result
    ):
        if not isinstance(result, Context.Interactive):
            raise Context.Interactive.NonIntentionalInteractive()
        channel = message['channel']
        self.interactive[channel] = (
            dict(
                func=func,
                i=result,
                started=datetime.now().timestamp(),
                channel=channel
            )
        )

    def __continue_interactive(self, c):
        # saving initial value of channel to avoid side effects
        channel = c.channel
        if not c.is_user_message:
            return False
        with self.interactive_lock:
            target = self.interactive.get(channel)
            if target is None:
                return False
            # to prevent deletion while operation is running
            target['started'] = datetime.now().timestamp()
        cmd = target['func']
        c.i = target['i']
        result = self.__run_cmd(c, cmd)
        if result is None:
            del self.interactive[channel]
        else:
            if not isinstance(result, Context.Interactive):
                raise Context.Interactive.NonIntentionalInteractive()
            with self.interactive_lock:
                # Updating target by link, if it's killed
                # no exc will be thrown
                # TODO: need to think about behavior here
                target['i'] = result
                target['started'] = datetime.now().timestamp()
        return True

    def __run_cmd(self, context, cmd):
        channel = context.channel
        with self.pending_channel_cmd_lock:
            try:
                cmds = self.pending_channels_cmd[channel]
            except KeyError:
                cmds = []
                self.pending_channels_cmd[channel] = cmds
            #  if this cmd is already running on specified channel
        if cmd in cmds:
            return None
        cmds.append(cmd)
        result = cmd(context)
        with self.pending_channel_cmd_lock:
            cmds = self.pending_channels_cmd.get(channel)
            cmds.remove(cmd)
            if not cmds:
                del self.pending_channels_cmd[channel]
            return result

    def __continue_non_interactive(self, c):
        for l in self.listeners:
            if l['condition'](c):
                result = self.__run_cmd(c, l['func'])
                if result is not None:
                    self.__start_interactive(c.message, l['func'], result)
                break

    def __try_to_kill_interactive(self, client, log=False):
        now = datetime.now().timestamp()
        kill = []
        for data in self.interactive.values():
            i = data['i']
            if now - data['started'] >= i.keep_alive:
                kill.append(dict(i=i, channel=data['channel']))
        if log and kill:
            print('KILLING INTERACTIVE SESSIONS...')
        with self.interactive_lock:
            for t in kill:
                channel = t['channel']
                if log:
                    print(channel, 'KIA')
                del self.interactive[channel]
                client.api_call(
                    'chat.postMessage',
                    channel=channel,
                    text=t['i'].bye_msg
                )

        if log and kill:
            print("STATE:")
            printer.pprint(self.interactive)

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

    def __process_message(self, context):
        if not self.__continue_interactive(context):
            self.__continue_non_interactive(context)

    def feed(self, client, messages, log=False):
        for m in messages:
            printer.pprint(m)
            threading.Thread(
                target=lambda c: self.__process_message(c),
                args=(Context(client, m),)
            ).start()
        self.__try_to_kill_interactive(client, log)

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
