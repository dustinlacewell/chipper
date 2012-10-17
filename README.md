chipper
======

Refreshingly simple declarative logging that utilizes arbitrary tag sinks instead of traditional level handling

chipper uses `Deconfigurable` configurations provided by the [deconf library](https://github.com/dustinlacewell/deconf). You should look it over to learn more about how chipper's log configuration works.

Introduction:
-------------

`chipper` is a module that provides a logging system that attempts to make logging as easy as possible. The main aspects unique to it are:

    * Multi-tag logging handlers
    * Declarative logging configuration

To get started immediately, you can simply use the default logger. This logger will route all emissions to stdout:

    >>> from chipper import log
    >>> log('Hello World')
    [DEFAULT] : Hello World

You can pass in your own tags with Log.log:

    >>> from chipper import log
    >>> log.log("Here's some general info", 'general', 'info')
    >>> [GENERAL, INFO] : Here's some general info

In addition to the main Log.log(message, *tags) form, some convenience magic is provided. Calling any attribute on the Log instance that is not used by the class itself will invoke the base Log.log method. The passed tags will be derrived by splitting the attribute name by underscore. The following call is equivalent:

    >>> log.general_info("Here's some general info')
    [GENERAL, INFO] : Here's some general info


Multi-tag Handlers:
-------------------

In a traditional logging system, each log emission specifies one of a number of possible logging levels. Traditional logging systems typically include levels such as `debug`, `warn`, `info`, and `error`.

In `chipper` log emissions can include any number of arbitrary *single-word* tags. Logging handlers are setup to listen for one or more tags. Any log messages that have tags that match will be routed to such handlers.

    >>> from chipper import Log, Handler, Target, Formatter
    >>> log = Log(
    ...   handlers=(
    ...     Handler(
    ...       name='templog',
    ...       tags=('debug', ),
    ...
    ...       target=Target(
    ...         filename='/tmp/templog.txt'
    ...       ),
    ...
    ...       formatter=Formatter(
    ...         template="{datetime}{tags} : "            
    ...       ),
    ...    ),
    ...  ),
    ... )
    >>> log('This should show in stdout')
    [DEFAULT] : This should show in stdout
    >>> log.debug('This should show in templog.txt')
    $ cat /tmp/templog.txt
    [2012-09-28 11:53:56][DEBUG] : This should show in templog.txt

With this system, you can log different views of activity within your application. For example, you may have a handler that routes all "sql" emissions to `logs/sql.txt`, a handler that routes all "blog" emissions to `logs/apps/blog.txt` and a third handler that routes all "warning" emissions to `stdout`. With this setup, the following call is routed to all three logging targets:

    >>> log.blog_sql_warning("Unusual query generated here. Query: '{0}'".format(new_query))
    [2012-09-28 11:59:28][BLOG, SQL, WARNING] : Unusual query generated here. Query: 'select * from 48.000f where'

Traced Emissions:
-----------------

If you'd like to include information in your emission about where the emission came from or any related exception information a special `trace` tag is handled:

    >>> log.trace("Use the source, Luke!")
    [<stdin>:1][TRACE]:Use the source, Luke!

You can capture handled exceptions and include their tracebacks in your log too:

    >>> def error():
    ...  raise SystemExit("Fatal Error!")
    ... 
    >>> try: error()
    ... except: log.trace("Something bad happened.")
    ... 
    [<stdin>:2][TRACE]:Something bad happened.
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "<stdin>", line 2, in error
    SystemExit: Fatal Error!


Tagged Loggers:
---------------

The magical attribute access has another nice aspect in that you can store log objects that always emit with the same tags. Simply store a reference to any log attribute:

    >>> bloginfo = log.blog_info
    >>> bloginfo("Updating comment cache...")
    [BLOG, INFO]:Updating comment cache...


chipper.Handler:
----------------

The `Handler` object is for specifying where log emissions with specific tags should be written to and how they should be formatted.

**name** `str`: The textual name of the handler

**tags** `tuple(str,)`: The tags to capture

**target** `chipper.Target`: The file object to write to

**formatter** `chipper.Formatter`: The object that will 
format the emissions


chipper.Target:
---------------

The `Target` object represents where the `Handler` will write captured emissions. It can write to any of the following that are configured.

**filename** `str`: The path of a file to write to

**stdout** `bool`: Whether to write to sys.stdout or not (default:`false`)

**stderr** `bool`: Whether to write to sys.stderr or not (default:`false`)


chipper.Formatter:
------------------

The `Formatter` is responsible for constructing the log prefix that is prepended to each log emission. It does this in a very configurable way that should be satisfactory for most needs.

There are essentially three "*item groups" that are processed. `Date and Time`, `Tags` and `Trace` information. The entire formatting process follows these steps:

  *  Format each item (the date, the time, each tag, etc) 
  *  Format each item-group (date/time, tags, etc)
  *  Format the entire log emission line


Item format options:
--------------------

**tag_template** `str`: Individual tag render template (default:`"{tag}"`)

**tag_formatter** `lambda`: Individual tag formatter lambda (default:`lambda tag: tag.upper().strip()`)

**tag_delimiter** `str`: Delimiter with which to join the tags (default:`,`)

**date_template** `str`: Date render template (default:`"{date}"`)

**date_format** `str`: Strftime format pattern (default:`"%Y-%m-%d"`)

**time_template** `str`: Time render template (default:`"{time}"`)

**time_format** `str`: Strftime format pattern (default:`"%Y-%m-%d"`)

**file_template** `str`: Filename render template (default:`"{file}"`)

**line_template** `str`: Line number render template (default:`":{line}"`)

**module_template** `str`: Module name render template (default:`":{module}"`)


Item-group format options:
--------------------------

**tags_template** `str`: Joined tags item-group template (default:`"[{tags}]"`)

**datetime_template** `str`: Datetime item-group render template (default:`"[{date} {time}]"`)

**trace_template** `str`: Collective trace info item-group template (default:`"{file}{line}"`)


Final emission format option:
-----------------------------

**template** `str`: The final render template incorporating all of the item-groups. Note that the `{trace}` format variable is only provided if the emission includes a trace tag. (default:`"{datetime}{trace}{tags} : "`)