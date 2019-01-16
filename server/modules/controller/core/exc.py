class SlackAPICallException(Exception):
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return self.reason


class IncorrectHandlerResult(Exception):
    def __str__(self):
        return "Handler result should be None or instance of CommandResult"


class DuplicateHandlerFunction(Exception):
    def __init__(self, func):
        self.__func_name = func.__name__

    def __str__(self):
        "Function {0} is already registered:".format(self.__func_name)
