"""Init module for rbkcli"""

from rbkcli.interface.rbk_cli import RbkCli
from rbkcli.core.handlers.customizer import RbkCliBlackOps
from rbkcli.base import RbkcliException

__version__ = '1.0.0-beta.2'
__author__ = 'Bruno Giovanini Manesco'
__all__ = [RbkCli, RbkCliBlackOps, RbkcliException]
