import contextvars
from contextlib import contextmanager

ROOT = "root"
PARENT = "parent"

#
#
#
bot_ctx_root = contextvars.ContextVar("bot_ctx_root", default=None)

#
# Neuron Context Management
#

neuron_ctx_root = contextvars.ContextVar("neuron_ctx_root", default=None)
neuron_ctx_parent = contextvars.ContextVar("neuron_ctx_parent", default=None)


def neuron_ctx_enter(child):
    bot = bot_ctx_root.get()
    child.bot = bot

    root = neuron_ctx_root.get()
    if not root:
        neuron_ctx_root.set(child)

    child.parent = parent = neuron_ctx_parent.get()
    if parent:
        parent.add(child)

    neuron_ctx_parent.set(child)
    return {ROOT: root, PARENT: parent}


def neuron_ctx_exit(ctx):
    root = ctx[ROOT]
    neuron_ctx_root.set(root)
    parent = ctx[PARENT]
    neuron_ctx_parent.set(parent)



#
# Behavior Context Management
#

task_ctx_parent = contextvars.ContextVar("task_ctx_parent", default=None)


def task_ctx_enter(child):
    bot = bot_ctx_root.get()
    child.bot = bot
    
    child.neuron = neuron_ctx_root.get()

    child.parent = parent = task_ctx_parent.get()
    if parent:
        parent.add(child)

    task_ctx_parent.set(child)
    return {PARENT: parent}


def task_ctx_exit(ctx):
    task_ctx_parent.set(ctx[PARENT])
