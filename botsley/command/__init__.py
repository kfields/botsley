import os
import click

from botsley.command.compile import compile as do_compile
'''
@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        click.echo('I was invoked without subcommand')
    else:
        click.echo('I am about to invoke %s' % ctx.invoked_subcommand)
'''

@click.group()
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)

@cli.command()
@click.pass_context
def init(ctx):
    pass

@cli.command()
@click.pass_context
@click.argument('filename')
def compile(ctx, filename):
    do_compile(filename)

@cli.command()
@click.pass_context
@click.argument('filename')
def run(ctx, filename):
    do_compile(filename)
