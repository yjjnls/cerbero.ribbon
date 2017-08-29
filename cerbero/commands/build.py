# cerbero - a multi-platform build system for Open Source software
# Copyright (C) 2012 Andoni Morales Alastruey <ylatuya@gmail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.


#from cerbero.oven import Oven
from cerbero.commands import Command, register_command
from cerbero.build.cookbook import CookBook
from cerbero.build.oven import Oven
from cerbero.utils import _, N_, ArgparseArgument


class Build(Command):
    doc = N_('Build a recipe')
    name = 'build'

    def __init__(self, force=None, no_deps=None):
            args = [
                ArgparseArgument('recipe', nargs='*',
                    help=_('name of the recipe to build')),
                ArgparseArgument('--missing-files', action='store_true',
                    default=False,
                    help=_('prints a list of files installed that are '
                           'listed in the recipe')),
                ArgparseArgument('--dry-run', action='store_true',
                    default=False,
                    help=_('only print commands instead of running them '))]
            if force is None:
                args.append(
                    ArgparseArgument('--force', action='store_true',
                        default=False,
                        help=_('force the build of the recipe ingoring '
                                    'its cached state')))
            if no_deps is None:
                args.append(
                    ArgparseArgument('--no-deps', action='store_true',
                        default=False,
                        help=_('do not build dependencies')))

            self.force = force
            self.no_deps = no_deps
            Command.__init__(self, args)

    def run(self, config, args):
        if self.force is None:
            self.force = args.force
        if self.no_deps is None:
            self.no_deps = args.no_deps
        self.runargs(config, args.recipe, args.missing_files, self.force,
                     self.no_deps, dry_run=args.dry_run)

    def runargs(self, config, recipes, missing_files=False, force=False,
                no_deps=False, cookbook=None, dry_run=False):
        if cookbook is None:
            cookbook = CookBook(config)

        oven = Oven(recipes, cookbook, force=self.force,
                    no_deps=self.no_deps, missing_files=missing_files,
                    dry_run=dry_run)
        oven.start_cooking()


class BuildOne(Build):
    doc = N_('Build or rebuild a single recipe without its dependencies')
    name = 'buildone'

    def __init__(self):
        Build.__init__(self, True, True)


class BuildX(Command):
    doc = N_('Build a recipe')
    name = 'buildx'

    def __init__(self):
        args = [
            ArgparseArgument('recipe', nargs='*',
                help=_('name of the recipe to build')),
            ArgparseArgument('--directory', default='.',
                         help=_('directory of the module to be built')),
                
            ArgparseArgument('--configure', action='store_true',
                default=False,
                help=_('with configure')),
            ArgparseArgument('--compile', action='store_true',
                default=False,
                help=_('with compile')),
            ArgparseArgument('--check', action='store_true',
                default=False,
                help=_('with check')),
            ArgparseArgument('--install', action='store_true',
                default=False,
                help=_('with install')),
            ArgparseArgument('--dry-run', action='store_true',
                default=False,
                help=_('only print commands instead of running them '))]
        Command.__init__(self, args)

    def run(self, config, args):
        import cerbero
        import os
        from cerbero.build.recipe import BuildSteps
        cerbero.build.recipe.Recipe.package_name = os.path.basename( args.directory)
        cerbero.build.recipe.Recipe._default_steps = []
        if args.configure:
            cerbero.build.recipe.Recipe._default_steps.append(BuildSteps.CONFIGURE)
        if args.compile:
            cerbero.build.recipe.Recipe._default_steps.append(BuildSteps.COMPILE)
        if args.check:
            cerbero.build.recipe.Recipe._default_steps.append(BuildSteps.CHECK)
        if args.install:
            cerbero.build.recipe.Recipe._default_steps.append(BuildSteps.INSTALL)
            cerbero.build.recipe.Recipe._default_steps.append(BuildSteps.POST_INSTALL)
            
        config.sources = os.path.dirname( args.directory )
        config.local_sources= os.path.dirname( args.directory )
        config.repo_dir = os.getcwd()

        cookbook = CookBook(config)

        oven = Oven(args.recipe, cookbook, force=True,
                    no_deps=True, missing_files=False,
                    dry_run=args.dry_run)
        oven.start_cooking()



register_command(BuildOne)
register_command(Build)
register_command(BuildX)
