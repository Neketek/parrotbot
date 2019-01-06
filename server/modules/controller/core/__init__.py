from pprint import PrettyPrinter
from collections import abc
import requests
from datetime import datetime
import threading
import logging
from modules.config.env import config as envconf
from . import exc


DEFAULT_BYE_MSG = "Interactive session is over. I waited too long."

printer = PrettyPrinter(indent=4)

logger = logging.getLogger(__name__.split('.')[-1].upper())
logger.setLevel(logging.DEBUG if envconf.DEBUG else logging.INFO)


class Context(object):
    class Interactive(object):
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

    class CommandResult(object):

        def __init__(
            self,
            wait_msg=None,
            interactive=None
        ):
            self.wait_msg = wait_msg
            self.i = interactive

        def wait(self, msg):
            self.wait_msg = msg
            return self

        def interactive(self, *args, **kwargs):
            self.i = Context.Interactive(*args, **kwargs)
            return self

    def __init__(self, client, message, interactive=None):
        self.client = client
        self.client_msg_id = message.get('client_msg_id')
        self.msg_type = message.get('type')
        self.msg_subtype = message.get('subtype')
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

    def send_and_wait(self, *args, **kwargs):
        return self.result().wait(self.send(*args, **kwargs).get('message'))

    def reply_and_wait(self, *args, **kwargs):
        return self.send_and_wait(self.channel, *args, **kwargs)

    def reply_code(self, text, **kwargs):
        return self.reply(text, code_block=True, **kwargs)

    def reply(self, text, **kwargs):
        return self.send(self.channel, text, **kwargs)

    def send(
        self,
        channel,
        text,
        code_block=False,
        **kwargs
    ):
        if code_block:
            text = "```{}```".format(text)
        response = self.client.api_call(
            'chat.postMessage',
            channel=channel,
            text=text,
            **kwargs
        )
        error = response.get('error')
        if error is None:
            return response
        raise exc.SlackAPICallException(error)

    @staticmethod
    def result():
        return Context.CommandResult()

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
        self.interactive = dict()
        self.keep_alive_wait_msg = 180  # seconds
        self.channel_cmd_wait_msg = dict()
        self.keep_alive_running_cmd = 60  # seconds
        self.channel_running_cmd = dict()
        self.threads = []

        self.__user_msg_edit_handler = None
        self.__user_msg_default_handler = None

        self.interactive_lock = threading.RLock()
        self.channel_cmd_wait_msg_lock = threading.RLock()
        self.channel_running_cmd_lock = threading.RLock()

    def __register(self, condition, func):
        func = update_func_name(func)
        if condition is Conditions.default():
            self.__user_msg_default_handler = func
            return
        elif condition is Conditions.user_msg_edit():
            self.__user_msg_edit_handler = func
            return
        for l in self.listeners:
            if l['func'] is func:
                raise exc.DuplicateHandlerFunction(func)
        self.listeners.insert(
            0,
            dict(
                cond=condition,
                func=func
            )
        )

    def register(self, condition):
        def decorator(func):
            self.__register(condition, func)
            return func
        return decorator

    def __try_to_add_cmd_wait_msg(self, context, cmd, result):
        if result is None or result.wait_msg is None:
            return False
        with self.channel_cmd_wait_msg_lock:
            try:
                cmd_wait_msg = self.channel_cmd_wait_msg[context.channel]
            except KeyError:
                cmd_wait_msg = dict()
                self.channel_cmd_wait_msg[context.channel] = cmd_wait_msg

            cmd_wait_msg[cmd] = dict(
                msg=result.wait_msg,
                ts=datetime.now().timestamp()
            )
            logger.debug(
                "C:{} CMD:{} WAIT_MSG".format(
                    context.channel,
                    cmd.__name__
                )
            )
            return True

    @staticmethod
    def __is_wait_message(wm, m):
        return (
            wm.get('bot_id') == m.get('bot_id')
            and wm.get('ts') == m.get('event_ts')
        )

    def __try_to_remove_channel_cmd_wait_msg(self, context):
        with self.channel_cmd_wait_msg_lock:
            try:
                cmd_wait_msg = self.channel_cmd_wait_msg[context.channel]
            except KeyError:
                return True
            for cmd in cmd_wait_msg:
                is_wait_msg = self.__is_wait_message(
                    cmd_wait_msg[cmd]['msg'],
                    context.message
                )
                if is_wait_msg:
                    remove = cmd
                    break
            else:
                return False
            del cmd_wait_msg[remove]
            logger.debug(
                "C:{} CMD:{} RECEIVED_WAIT_MSG".format(
                    context.channel,
                    cmd.__name__
                )
            )
            return True

    def __is_cmd_waiting(self, context, cmd):
        with self.channel_cmd_wait_msg_lock:
            try:
                cmd_wait_msg = self.channel_cmd_wait_msg[context.channel]
                if cmd_wait_msg.get(cmd) is not None:
                    logger.debug(
                        "C:{} CMD:{} SKIP_MSG:{}".format(
                            context.channel,
                            cmd.__name__,
                            context.text
                        )
                    )
                    return True
            except KeyError:
                self.channel_cmd_wait_msg[context.channel] = {}

    @staticmethod
    def __create_interactive_entry(
        m,
        cmd,
        res
    ):
        if res is None or res.i is None:
            return None
        return dict(
            ts=datetime.now().timestamp(),
            channel=m['channel'],
            cmd=cmd,
            i=res.i
        )

    def __try_to_start_interactive(
        self,
        context,
        cmd,
        res
    ):
        entry = self.__create_interactive_entry(
            context.message,
            cmd,
            res
        )
        if entry is None:
            return False
        logger.debug(
            'C:{} CMD:{} INTERACTIVE_START'
            .format(context.channel, cmd.__name__)
        )
        self.interactive[context.channel] = entry
        return True

    def __try_to_kill_interactive(self, client):
        with self.interactive_lock:
            now = datetime.now().timestamp()
            remove = []
            for data in self.interactive.values():
                if now - data['ts'] > data['i'].keep_alive:
                    remove.append(data)
            for data in remove:
                channel = data['channel']
                i = data['i']
                del self.interactive[channel]
                if i.bye_msg:
                    client.api_call(
                        "chat.postMessage",
                        channel=channel,
                        text=i.bye_msg
                    )

    def __try_to_remove_expired_channel_wait_cmd_msg(self):
        with self.channel_cmd_wait_msg_lock:
            now = datetime.now().timestamp()
            for channel in self.channel_cmd_wait_msg:
                cmd_wait_msg = self.channel_cmd_wait_msg[channel]
                remove = []
                for cmd in cmd_wait_msg:
                    msg = cmd_wait_msg[cmd]
                    if now - msg['ts'] > self.keep_alive_wait_msg:
                        remove.append(msg)
                if remove:
                    self.channel_cmd_wait_msg[channel] = [
                        msg
                        for msg in cmd_wait_msg
                        if msg not in remove
                    ]

    def __process_cmd_result(self, context, cmd, res):
        if res is not None and not isinstance(res, Context.CommandResult):
            raise exc.IncorrectHandlerResult()
        if not self.__try_to_start_interactive(context, cmd, res):
            # means that cmd was interactive but now it's interrupted
            if context.i is not None:
                try:
                    # stopping interactive session
                    del self.interactive[context.channel]
                except KeyError:
                    pass
                logger.debug(
                    "C:{} CMD:{} INTERACTIVE_STOP".format(
                        context.channel,
                        cmd.__name__
                    )
                )
        self.__try_to_add_cmd_wait_msg(context, cmd, res)

    def __run_cmd(self, context, cmd):
        with self.channel_running_cmd_lock:
            now = datetime.now().timestamp()
            try:
                running = self.channel_running_cmd[context.channel]
            except KeyError:
                running = dict()
                self.channel_running_cmd[context.channel] = running
            if cmd in running.keys():
                return
            running[cmd] = now
        res = cmd(context)
        with self.channel_running_cmd_lock:
            del running[cmd]
        self.__process_cmd_result(context, cmd, res)

    def __try_to_clear_expired_channel_running_cmd(self):
        with self.channel_running_cmd_lock:
            now = datetime.now().timestamp()
            for channel in self.channel_running_cmd:
                running = self.channel_running_cmd[channel]
                remove = []
                for key in running:
                    if now - running[key] > self.keep_alive_running_cmd:
                        remove.append(key)
                for key in remove:
                    del running[key]

    def __try_to_get_non_interactive(self, c):
        if not c.is_user_message:
            return None
        for l in self.listeners:
            cond = l['cond']
            if cond(c):
                return l['func']
        else:
            return self.__user_msg_default_handler

    def __try_to_get_interactive(self, c):
        if not c.is_user_message:
            return None
        with self.interactive_lock:
            target = self.interactive.get(c.channel)
            if target is None:
                return None
            logger.debug('C:{} INTERACTIVE_CONTINUE'.format(c.channel))
            # this was the "best" fking fix in the world, I just leave it here
            # del self.interactive[context.channel]
            c.i = target.get('i')
            return target['cmd']

    def __process_message(self, client, msg):
        context = Context(client, msg)
        # logger.debug(printer.pformat(msg))
        if context.is_user_message:
            logger.debug(
                "C:{} USER_MSG:{}".format(context.channel, context.text)
            )
        cmd = self.__try_to_get_interactive(context)
        if cmd is None:
            cmd = self.__try_to_get_non_interactive(context)
        # if this is edit msg use specific handler
        if cmd is None and context.msg_subtype == 'message_changed':
            cmd = self.__user_msg_edit_handler
        if cmd is None:
            self.__try_to_remove_channel_cmd_wait_msg(context)
            return
        if self.__is_cmd_waiting(context, cmd):
            return
        self.__run_cmd(context, cmd)

    def __create_msg_thread_worker(self, client, msg):
        def worker():
            try:
                self.__process_message(client, msg)
            finally:
                self.threads.remove(threading.current_thread())
        thread = threading.Thread(target=worker)
        self.threads.append(thread)
        thread.start()

    def feed(self, client, messages, log=False):
        for m in messages:
            self.__create_msg_thread_worker(client, m)
        self.__try_to_remove_expired_channel_wait_cmd_msg()
        self.__try_to_clear_expired_channel_running_cmd()
        self.__try_to_kill_interactive(client)

    def __str__(self):
        res = "[\n"
        for l in self.listeners:
            res += " ({0}, {1})\n".format(
                l['func'].__name__,
                l['cond'].__name__
            )
        res += ']'
        return res


class Conditions:
    @staticmethod
    def __default_condition(c):
        return True

    def __user_msg_edit(c):
        return True

    @staticmethod
    def user_msg_edit():
        return Conditions.__user_msg_edit

    @staticmethod
    def command(text, *args):
        def condition(c):
            command_match = False
            if len(c.command_args) == 0:
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
