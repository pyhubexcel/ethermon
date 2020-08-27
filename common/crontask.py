"""
period is similar to crontab period format, but add second as first parameter.
.------------------ second (0 - 59)
|   .--------------- minute (0 - 59)
|   |   .------------ hour (0 - 23)
|   |   |   .--------- day of month (1 - 31)
|   |   |   |   .------ month (1 - 12) or Jan, Feb ... Dec
|   |   |   |   |  .---- day of week (0 - 6) or Sun(0 or 7), Mon(1) ... Sat(6)
V   V   V   V   V  V
*   *   *   *   *  *

To add cron task, can use register_task decorator, or pass tasks array when call run.
Each group has its own backgroud process to run tasks. Tasks in same group will be run in same process.
If fork is True, the host will fork a temp process to run the task every time to prevent memory leak.

This module depends on the croniter library.
"""

import time
from itertools import groupby
from multiprocessing import Process
from datetime import datetime
from croniter import croniter
from logger import log
_crontab = []

def _total_seconds(td):
	return td.days * 86400.0 + td.seconds + td.microseconds * 1e-6

def _get_exec_time_iter(period):
	parts = period.split()
	# second is the last part in croniter format
	parts.append(parts.pop(0))
	return croniter(" ".join(parts), datetime.now())

def _reset_croniter(task):
	task["croniter"] = _get_exec_time_iter(task["period"])

def _update_next_exec(task):
	task["next_exec"] = task["croniter"].get_next(datetime)

def _pick_next_task(tasks):
	now = datetime.now()
	ret = None
	for t in tasks:
		if t["next_exec"] <= now:
			return t
		if ret is None or t["next_exec"] < ret["next_exec"]:	# pylint: disable=unsubscriptable-object
			ret = t
	return ret

def _run_task(task):
	try:
		task()
	except:
		logging.exception("crontask_exception|task=%s", task.__name__)

def _run_task_group(tasks):
	for task in tasks:
		_reset_croniter(task)
		_update_next_exec(task)

	while True:
		task = _pick_next_task(tasks)

		now = datetime.now()
		time_to_sleep = _total_seconds(task["next_exec"] - now)
		if time_to_sleep > 0:
			time.sleep(time_to_sleep)
		else:
			# only respect one missed exec
			_reset_croniter(task)

		if task["fork"]:
			p = Process(target=_run_task, args=(task["task"],))
			p.start()
			p.join()
		else:
			_run_task(task["task"])

		_update_next_exec(task)

		# ignore all execs between the updated next_exec and now:
		# we only respect one exec no matter how many number
		# of execs were missed when task was running
		if task["next_exec"] < datetime.now():
			_reset_croniter(task)

		# move task to rear to ensure no starvation
		tasks.remove(task)
		tasks.append(task)

def _run_tasks(crontab):
	processes = []
	def run_task_group(tasks):
		p = Process(target=_run_task_group, args=(tasks,))
		p.start()
		processes.append(p)

	get_group = lambda t: t["group"]
	crontab = sorted(crontab, key=get_group)
	for group, tasks in groupby(crontab, get_group):
		if group is None:
			for t in tasks:
				run_task_group([t])
		else:
			run_task_group(list(tasks))
	return processes

def register_task(period, group=None, fork=True, task=None):
	def _register_task(task):
		_crontab.append({"task": task, "period": period, "group": group, "fork": fork})
		return task
	if task is not None:
		_register_task(task)
		return
	return _register_task

def run(tasks=None, background=False):
	if tasks is not None:
		_crontab.update(tasks)
	processes = _run_tasks(_crontab)

	if not background:
		for p in processes:
			p.join()
