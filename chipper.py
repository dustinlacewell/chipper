import os, sys, datetime, traceback

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
    if conf_module:
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

    @deconf.parameter('template', ensure_type=str, default="{datetime}{trace}{tags} :")
    def handle_template(self, template):
        """
        The main logging template.
            date : the date of log emission
            time : the time of log emission
            tags : a delimited list of emission tags
            trace: the trace information if present
        """
        pass
        
    @deconf.parameter('tags_template', ensure_type=str, default="[{tags}]")
    def handle_tags_template(self, template):
        """
        The template for rendering the formatted tags list.
            tags : the list of tags
        """
        pass

    @deconf.parameter('tag_template', ensure_type=str, default="{tag}")
    def handle_tag_template(self, template):
        """
        The template for rendering each tag.
            tag : the tag to render
        """
        pass

    @deconf.parameter('tag_formatter', ensure_type=type(lambda x: x), default=lambda tag: tag.upper().strip())
    def handle_tag_formatter(self, formatter):
        """
        Formatting lambda for transforming tags.

        """
        pass

    @deconf.parameter('tag_delimiter', ensure_type=str, default=", ")
    def handle_tag_delimiter(self, delimiter):
        """
        The delimiter between joined tags.

        """
        pass

    @deconf.parameter('date_template', ensure_type=str, default="{date}")
    def handle_date_template(self, template):
        """
        The template for rendering the date.
            date : the date to render
        """
        pass

    @deconf.parameter('date_format', ensure_type=str, default="%Y-%m-%d")
    def handle_date_format(self, format):
        """
        Strftime date format string.

        """
        pass

    @deconf.parameter('time_template', ensure_type=str, default="{time}")
    def handle_time_template(self, template):
        """
        The template for rendering the time.
            time : the time to render
        """
        pass

    @deconf.parameter('time_format', ensure_type=str, default="%H:%M:%S")
    def handle_time_format(self, format):
        """
        Strftime time format string.

        """
        pass

    @deconf.parameter('datetime_template', ensure_type=str, default="[{date} {time}]")
    def handle_datetime_template(self, template):
        """
        The template for rendering the date and time.
            date : the formatted date to render
            time : the formatted time to render
        """
        pass

    @deconf.parameter('file_template', ensure_type=str, default="{file}")
    def handle_file_template(self, template):
        """
        The template for rendering the filename.
            file : the filename to render
        """
        pass

    @deconf.parameter('line_template', ensure_type=str, default=":{line}")
    def handle_line_template(self, template):
        """
        The template for rendering the line number.
            line : the line number to render
        """
        pass

    @deconf.parameter('module_template', ensure_type=str, default=":{module}")
    def handle_module_template(self, template):
        """
        The template for rendering the module name.
            module : the module name to render
        """
        pass

    @deconf.parameter('trace_template', ensure_type=str, default="[{file}{line}]")
    def handle_trace_template(self, template):
        """
        The template for rendering the trace info.
            file : the formatted filename
            line : the formatted line number
            module : the formatted module name
        """
        pass


    def format_message(self, message, handler, tags, date, time, file='', line='', module=''):
        """
        Format the message template in preparation for emission
        """

        tags = [self.tag_formatter(t) for t in tags]
        tags = [self.tag_template.format(tag=t) for t in tags]
        tags = self.tag_delimiter.join(tags)
        tags = self.tags_template.format(tags=tags)

        date = date.strftime(self.date_format)
        date = self.date_template.format(date=date)

        time = time.strftime(self.time_format)
        time = self.time_template.format(time=time)

        datetime = self.datetime_template.format(date=date, time=time)

        trace = ''
        if file or line or module:
            file = self.file_template.format(file=file)
            line = self.line_template.format(line=line)
            module = self.module_template.format(module=module)
            trace = self.trace_template.format(file=file, line=line, module=module)

        return self.template.format(
            handler=handler.name, 
            tags=tags, 
            datetime=datetime,
            trace=trace,
        ) + message

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

    def __init__(self, *args, **kwargs):
        super(Target, self).__init__(*args, **kwargs)
        self.targets = []
        if self.filename:
            self.targets.append(open(self.filename, 'a'))
        if self.stdout:
            self.targets.append(sys.stdout)
        if self.stderr:
            self.targets.append(sys.stderr)

    def log(self, message):
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

    @deconf.parameter('formatter', ensure_type=Formatter, default=Formatter())
    def handle_format(self, format): 
        """
        A Formatter object for rendering the formatted log message.

        """
        pass

    def log(self, message, tags, date, time, **trace):
        message = self.formatter.format_message(message, self, tags, date, time, **trace)
        self.target.log(message + "\n")

default_handler = Handler(
    name='default',
    tags=('*', ),
    target=Target(stdout=True),
    formatter=Formatter(
        template="{trace}{tags}:",
    )
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
        if "trace" in self.tags:
            trace = traceback.extract_stack()[-2]
            file, line, module = (os.path.basename(trace[0]), trace[1], trace[2])

            error = traceback.format_exc()
            if error != "None\n":
                message = "{0}\n{1}".format(message, error)
            self.log.log(message, *self.tags, file=file, line=line, module=module)
        else:
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
        self.__handlers = handlers or []
        self.__default = default

    def _get_date_and_time(self):
        now = datetime.datetime.now()
        date = now.date()
        time = now.time()
        return (date, time)


    def __call__(self, message):
        date, time = self._get_date_and_time()
        self.__default.log(message, ('default', ), date, time)

    def log(self, message, *tags, **trace):
        """
        Base logging method. Takes a message and any number of
        tags. Will be routed to any Handlers listening for those
        provided tags.

        """
        date, time = self._get_date_and_time()

        handlers = {}
        unhandled = []
        for tag in tags:
            found = False
            for handler in self.__handlers:
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
            self.__default.log(message, unhandled, date, time, **trace)

    def __getattr__(self, name):
        try:
            return self.__getattribute__(name)
        except AttributeError:
            tags = [t for t in name.split("_") if t]
            return TaggedLog(self, *tags)

log = Log() # default log