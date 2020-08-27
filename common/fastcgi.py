from optparse import make_option, OptionParser

MONKEY_PATCH_NAMES = ('os', 'socket', 'thread', 'select', 'time', 'ssl', 'all')

class CommandError(Exception):
	pass

class FastcgiCommand(object):
	args = '<host>:<port> | <socket file>'
	help = 'Start fastcgi server'
	option_list = (
		make_option('--wsgi', type='str', dest='wsgi', metavar='WSGI',
					help='WSGI object to be loaded, module:object',
					),
		make_option('--max-conns', type='int', dest='max_conns', default=1024,
					metavar='MAX_CONNS',
					help='Maximum simulteneous connections (default %default)',
					),
		make_option('--buffer-size', type='int', dest='buffer_size',
					default=4096, metavar='BUFFER_SIZE',
					help='Read buffer size (default %default)',
					),
		make_option('--num-workers', type='int', dest='num_workers', default=1,
					metavar='NUM_WORKERS',
					help='Number of worker processes (default %default)',
					),
		make_option('--monkey-patch', dest='monkey_patch',
					help='Comma separated list of function names from '
					'gevent.monkey module. Allowed names are: ' + ', '.join(
						map('"{0}"'.format, MONKEY_PATCH_NAMES))),
		make_option('--socket-mode', type='int', dest='socket_mode',
					metavar='SOCKET_MODE',
					help='Socket file mode',
					),
		make_option('--work-dir', dest='our_home_dir', default='.',
					metavar='WORKDIR',
					help='Chande dir in daemon mode (default %default)'),
		make_option('--daemon', dest='daemon', metavar='DAEMON',
					help='Become a daemon, pid file path'),
		make_option('--stdout', dest='out_log', metavar='STDOUT',
					help='stdout and stderr in daemon mode (default sys.devnull)'),
	)

	def execute(self):
		import sys
		argv = sys.argv
		parser = OptionParser(prog=argv[0], usage=self.usage(argv[0]), option_list=self.option_list)
		options, args = parser.parse_args(argv[1:])
		try:
			self.handle(*args, **options.__dict__)
		except CommandError as e:
			sys.stderr.write('%s: %s' % (e.__class__.__name__, e))
			sys.exit(1)

	def handle(self, *args, **options):
		# pylint: disable=too-many-locals
		# gevent monkey patch
		# Note: after patch, gevent-fastcgi will spawn new greenlet for each request,
		# which means django models will create new connection for each request.
		# it is suggested to use gunicorn instead of gevent-fastcgi in gevent mode.
		if options['monkey_patch']:
			names = filter(None, map(str.strip, options['monkey_patch'].split(',')))
			if names:
				module = __import__('gevent.monkey', fromlist=['*'])
				for name in names:
					if name not in MONKEY_PATCH_NAMES:
						raise CommandError(
							'Unknown name "{0}" in --monkey-patch option'
							.format(name))
					patch_func = getattr(module, 'patch_{0}'.format(name))
					patch_func()

			# replace MySQLdb with pymysql for gevent
			import pymysql
			pymysql.install_as_MySQLdb()

		import os
		import sys
		from os.path import dirname, isdir

		# patch python2.6 logging module
		if sys.version_info < (2, 7):
			import logging
			class NullHandler(logging.Handler):
				def emit(self, record):
					pass
			logging.NullHandler = NullHandler

		# patch gevent fastcgi for werkzeug / flask
		from gevent_fastcgi.base import InputStream
		def readline(self, size=-1):
			self._eof_received.wait()
			return self._file.readline(size)
		InputStream.readline = readline

		from gevent_fastcgi.wsgi import WSGIRequest
		from gevent_fastcgi.interfaces import IRequestHandler
		from zope.interface import implements
		from gevent_fastcgi.server import FastCGIServer

		class WSGIRequestHandler(object):

			implements(IRequestHandler)

			def __init__(self, app):
				self.app = app

			def __call__(self, fastcgi_request):
				# pylint: disable=protected-access
				request = WSGIRequest(fastcgi_request)
				try:
					app_iter = self.app(request._environ, request.start_response)
					request.finish(app_iter)
					if hasattr(app_iter, 'close'):
						app_iter.close()
				except:
					try:
						from logger import log
						logging.exception('handle_http_request_exception')
					except:
						pass
					request.start_response('500 Internal Server Error', [('Content-type', 'text/plain'),])
					request.finish(['Internal Server Error (500)'])

		# subclass gevent fastcgi so each spawned process has distinctive random seeds
		class GFastCGIServer(FastCGIServer):

			def start_accepting(self):
				import random
				random.seed()
				return super(GFastCGIServer, self).start_accepting()

		if not args:
			raise CommandError('Please specify binding address')

		if len(args) > 1:
			raise CommandError('Unexpected arguments: %s' % ' '.join(args[1:]))

		bind_address = args[0]

		try:
			host, port = bind_address.split(':', 1)
			port = int(port)
		except ValueError:
			socket_dir = dirname(bind_address)
			if not isdir(socket_dir):
				raise CommandError(
					'Please create directory for socket file first %r' %
					dirname(socket_dir))
		else:
			if options['socket_mode'] is not None:
				raise CommandError('--socket-mode option can only be used '
									'with Unix domain sockets. Either use '
									'socket file path as address or do not '
									'specify --socket-mode option')
			bind_address = (host, port)

		pid_file = options.get('daemon')
		if pid_file:
			import daemon
			daemon = daemon.Daemon(None, pid_file, options.get('out_log', '/dev/null'))
			daemon.start()

		kwargs = dict((
			(name, value) for name, value in options.iteritems() if name in (
				'num_workers', 'max_conns', 'buffer_size', 'socket_mode')))

		os.chdir(options['our_home_dir'])
		if options['our_home_dir'] not in sys.path:
			sys.path.append(options['our_home_dir'])

		wsgi_args = options['wsgi'].split(':')
		wsgi_module = wsgi_args[0]
		if len(wsgi_args) > 1:
			wsgi_object = wsgi_args[1]
		else:
			wsgi_object = 'app'

		app_module = __import__(wsgi_module, fromlist=[wsgi_object])
		app = getattr(app_module, wsgi_object)

		request_handler = WSGIRequestHandler(app)
		server = GFastCGIServer(bind_address, request_handler, **kwargs)
		server.serve_forever()

	def usage(self, subcommand):
		usage = '%%prog %s [options] %s' % (subcommand, self.args)
		if self.help:
			return '%s\n\n%s' % (usage, self.help)
		else:
			return usage

if __name__ == '__main__':
	command = FastcgiCommand()
	command.execute()
