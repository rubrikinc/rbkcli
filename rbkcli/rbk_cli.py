#!/usr/bin/python3

import sys
import click
from rbkcli.base import RbkcliException
from rbkcli.cli import Rbkcli


# Instantiating the target for the CLI as global var.
global rbk
rbk = Rbkcli()

# Definning the Command Line interface.
@click.command(name='rbkcli')

# The API endpoint to be requested, required argument.
@click.argument("api_endpoint",
                type=click.STRING,
                nargs=-1,
                required=True,
                autocompletion=rbk.provide_autocomplete)

# The method to reach the endpoint, default is get.
@click.option('-m', '--method',
              type=click.STRING,
              default='get',
              show_default=True)

# Version of the imported API in the target.
@click.option('-v', '--version', type=click.STRING, default='')

# Parameter passed to the API request, json.
@click.option('-p', '--parameter', type=click.STRING, default={})

# List of available operations.
@click.option('-q', '--query', type=click.STRING, default='')

# Documentation related to the provided endpoint and method.
@click.option('-i', '--info', is_flag=True)

def cli(api_endpoint, method, version, parameter, query, info):
    '''Easy calls of Rubrik APIs from CLI'''
    try:
        query_cmd = ','.join(query)
        output = rbk.cli_execute(api_endpoint, method, version, parameter,
                                 query, info)
        click.echo(output)
    except RbkcliException.ApiRequesterError as error:
        raise click.ClickException('ApiRequester # ' + str(error))
    except RbkcliException.DynaTableError as error:
        raise click.ClickException('DynamicTable # ' + str(error))
    except RbkcliException.ToolsError as error:
        raise click.ClickException('IOTools # ' + str(error))
    except RbkcliException.LoggerError as error:
        raise click.ClickException('Logger # ' + str(error))
    except RbkcliException.ClusterError as error:
        raise click.ClickException('ApiTarget # ' + str(error))
    except RbkcliException.ApiHandlerError as error:
        raise click.ClickException('ApiHandler # ' + str(error))
    except RbkcliException.RbkcliError as error:
        msg = str('\n\nFor all available commands run:'
                  '\n   $rbkcli commands'
                  '\n   $rbkcli commands -q <cmd_name>')
        raise click.UsageError(str(error) + msg)        

def main():
    '''Gather args and call cli function.'''

    # Getting provided arguments 
    args = sys.argv[1:]

    # Calling CLI
    cli(args)

if __name__ == '__main__':
    # If cli file is executed directly, will call main.
    main()
