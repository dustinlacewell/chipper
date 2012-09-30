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
    >>> log.log('Hello World', 'general', 'info')
    [2012-09-28 11:46:58][GENERAL, INFO] : Hello World

In addition to the main Log.log(message, *tags) form, some convenience magic is provided. Calling any attribute on the Log instance that is not used by the class itself will invoke the base Log.log method. The passed tags will be derrived by splitting the attribute name by underscore. The following call is equivalent:

    >>> log.general_info('Hello World')
    [2012-09-28 11:49:16][GENERAL, INFO] : Hello World


Multi-tag Handlers:
-------------------

In a traditional logging system, each log emission specifies one of a number of possible logging levels. Traditional logging systems typically include levels such as `debug`, `warn`, `info`, and `error`.

In `chipper` log emissions can include any number of arbitrary *single-word* tags. Logging handlers are setup to listen for one or more tags. Any log messages that have tags that match will be routed to such handlers.

    >>> from chipper import Log, Handler, Target
    >>> log = Log(
    ...   handlers=(
    ...     Handler(
    ...       name='templog',
    ...       tags=('debug', ),
    ...       target=Target(
    ...         filename='/tmp/templog.txt'
    ...       ),
    ...    ),
    ...  ),
    ... )
    >>> log.stdout('This should show in stdout')
    [2012-09-28 11:53:44][STDOUT] : This should show in stdout
    >>> log.debug('This should show in templog.txt')
    $ cat /tmp/templog.txt
    [2012-09-28 11:53:56][DEBUG] : This should show in templog.txt

With this system, you can log different views of activity within your application. For example, you may have a handler that routes all "sql" emissions to `logs/sql.txt`, a handler that routes all "blog" emissions to `logs/apps/blog.txt` and a third handler that routes all "warning" emissions to `stdout`. With this setup, the following call is routed to all three logging targets:

    >>> log.blog_sql_warning("Unusual query generated here. Query: '{0}'".format(new_query))
    [2012-09-28 11:59:28][BLOG, SQL, WARNING] : Unusual query generated here. Query: 'select * from 48.000f where'
