class Context:

    def __init__(self, client, message, next=None):
        self.client = client
        self.message = message
        self.next = next
        self.text = message.get('text')
        self.channel = message.get('channel')

    def reply(self, text):
        self.client.api_call(
            'chat.postMessage',
            channel=self.channel,
            text=text
        )

    def interactive(self, next_data=None):
        return next_data


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
        for l in self.listeners:
            if l['condition'](message):
                result = l['func'](Context(client, message))
                if result is not None:
                    self.__start_interactive(l['func'], message, result)
                break

    def __register(self, condition, func):
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
        for m in messages:
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
    def __default_condition(m):
        user = m.get('user')
        text = m.get('text')
        channel = m.get('channel')
        return user is not None and channel is not None and text is not None

    @staticmethod
    def command(text):
        text = text.strip(' ').lower()

        def condition(m):
            user = m.get('user')
            command = m.get('text', '').strip(' ').lower()
            return user is not None and command == text
        condition.__name__ = "command '{0}'".format(text)
        return condition

    @staticmethod
    def default():
        return Conditions.__default_condition


actions = __Actions()
