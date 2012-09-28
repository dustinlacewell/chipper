import sys, datetime

import deconf

def from_file(filename, attribute):
    """
    Loads a standalone Python script and returns the
    named attribute, handy for loading a log definition
    from a user config file.

    filename - absolute path of config file
    attribute - module-level attribute containing log

    """

    conf_module = deconf.load_config(filename)
    try:
        return getattr(conf_module, attribute)
    except AttributeError:
        msg = "'{module}' has no log attribute '{attribute}'"
        msg = msg.format(module=conf_module.__name__, attribute=attribute)
        raise AttributeError(msg)

class Formatter(deconf.Deconfigurable):
    """
    A class for declaring log formatting configuration. Supports
    date, time and tag formatting options in addition to the main
    logging template.

    """

    @deconf.parameter('template', ensure_type=str, default="[{date} {time}][{tags}] : {message}")
    def handle_template(self, template):
        """
        The main logging template.

        Available template vars:
            date : the date of log emission
            time : the time of log emission
            tags : a delimited list of emission tags
            message : the emitted log message
        """
        if not template.endswith('\n'):
            template = template + '\n'
        return template

    @deconf.parameter('tag_delimiter', ensure_type=str, default=", ")
    def handle_tag_delimiter(self, delimiter):
        """
        The delimiter between joined tags.

        """
        pass

    @deconf.parameter('tag_formatter', ensure_type=type(lambda x: x), default=lambda tag: tag.upper().strip())
    def handle_tag_formatter(self, formatter):
        """
        Formatting lambda for transforming tags.

        """
        pass

    @deconf.parameter('date_format', ensure_type=str, default="%Y-%m-%d")
    def handle_date_format(self, format):
        """
        Strftime date format string.

        """
        print "Handling date format", format

    @deconf.parameter('time_format', ensure_type=str, default="%H:%M:%S")
    def handle_time_format(self, format):
        """
        Strftime time format string.

        """
        print "Handling time format", format


    def format_message(self, message, handler, tags, date, time):
        """
        Format the message template in preparation for emission
        """
        tags = [self.tag_formatter(t) for t in tags]
        tags = self.tag_delimiter.join(tags)
        return self.template.format(
            message=message, 
            handler=handler.name, 
            tags=tags, 
            date=date.strftime(self.date_format),
            time=time.strftime(self.time_format),
        )        

class Target(deconf.Deconfigurable):
    """
    A class for declaring a target for writing formatted
    emitted log messages to. Supports files on disk or
    the standard system stdout/stderr buffers. 

    """

    @deconf.parameter('filename', ensure_type=str, default='')
    def handle_filename(self, filename): 
        """
        Path of a file to write log messages to.

        """
        pass

    @deconf.parameter('stdout', ensure_type=bool, default=False)
    def handle_stdout(self, stdout): 
        """
        Flag declaring whether to write log messages to stdout.

        """
        pass

    @deconf.parameter('stderr', ensure_type=bool, default=False)
    def handle_stderr(self, stderr): 
        """
        Flag declaring whether to write log messages to stderr.

        """
        pass

    @deconf.parameter('formatter', ensure_type=Formatter, default=Formatter())
    def handle_format(self, format): 
        """
        A Formatter object for rendering the formatted log message.

        """
        pass

    def __init__(self, *args, **kwargs):
        super(Target, self).__init__(*args, **kwargs)
        self.targets = []
        if self.filename:
            self.targets.append(open(self.filename, 'a'))
        if self.stdout:
            self.targets.append(sys.stdout)
        if self.stderr:
            self.targets.append(sys.stderr)

    def log(self, message, handler, tags, date, time):
        message = self.formatter.format_message(message, handler, tags, date, time)

        # ensure each log message ends with a newline
        if not message.endswith('\n'):
            message = message + "\n"

        for target in self.targets:
            target.write(message)


class Handler(deconf.Deconfigurable):
    """
    Class for declaring a handler/sink for emitted log messages.
    Will only accept log messages that contain tags that this
    handler is listening for. Handled log messages will be written
    to the specified Target.

    """
    @deconf.parameter('name', ensure_type=str)
    def handle_name(self, name):
        """
        The name of this handler

        """
        pass

    @deconf.parameter('tags', ensure_type=tuple)
    def handle_tags(self, tags):
        """
        The list of tags this handler responds to.

        """
        if not len(tags):
            msg = "Handler 'tags' list must contain at least one tagname"
            raise deconf.ParameterValueError(msg)
        self.tags = tags
        return self.tags

    @deconf.parameter('target', ensure_type=Target)
    def handle_target(self, target):
        """
        The initialized Target object this Handler writes messages to.

        """
        pass

    def log(self, message, tags, date, time):
        self.target.log(message, self, tags, date, time)


default_handler = Handler(
    name='default',
    tags=('*', ),
    target=Target(stdout=True),
)


class TaggedLog(object):
    """
    Helper class that logs messages to a specific collection of
    tags.

    """
    def __init__(self, log, *tags):
        self.log = log
        self.tags = tags

    def __call__(self, message):
        self.log.log(message, *self.tags)

class Log(object):
    """
    A class for logging messages.

    A number of Handlers are initialized that route messages
    to files. Each Handler listens for one or more tags. Any
    message emitted with a tag that belongs to a Handler will
    be routed to that Handler and written to its Target.

    All matching Handlers are written to.

    In addition to the main Log.log(message, *tags) form, some
    convenience magic is provided. Calling any attribute on the
    Log instance that is not used by the class itself will
    invoke the base Log.log method. The passed tags will be
    derrived by splitting the attribute name by underscore.

    For example:

    >>> log.log("This is the raw log form", "info", "general")

    Is the same as:

    >>> log.general_info("This is the convenience form")

    The `default` logger will capture any messages that has
    no tags matching a configured Handler.
    """
    def __init__(self, handlers=None, default=default_handler):
        self.handlers = handlers or []
        self.default = default_handler

    def log(self, message, *tags):
        """
        Base logging method. Takes a message and any number of
        tags. Will be routed to any Handlers listening for those
        provided tags.

        """
        now = datetime.datetime.now()
        date = now.date()
        time = now.time()

        handlers = {}
        unhandled = []
        for tag in tags:
            found = False
            for handler in self.handlers:
                if tag in handler.tags:
                    taglist = handlers.get(handler, [])
                    taglist.append(tag)
                    handlers[handler] = taglist
                    found = True
            if not found:
                unhandled.append(tag)
        for handler, tags in handlers.items():
            handler.log(message, tags, date, time)
        if len(unhandled):
            self.default.log(message, unhandled, date, time)

    def __getattr__(self, name):
        try:
            return self.__getattribute__(name)
        except AttributeError:
            tags = name.split("_")
            return TaggedLog(self, *tags)

log = Log() # default log