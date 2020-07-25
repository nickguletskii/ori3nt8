#  Copyright 2020 Nick Guletskii
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Tuple

from grundzeug.config.providers.argparse import ArgParseConfigurationProvider
from grundzeug.config.providers.common import ConfigurationProvider
from grundzeug.config.providers.toml import TOMLConfigurationProvider
from grundzeug.container import Container
from grundzeug.container.plugins import ContainerConverterResolutionPlugin, ContainerConfigurationResolutionPlugin, \
    BeanList
from grundzeug.converters import Converter


def build_container(config_classes):
    container = Container()
    container.add_plugin(ContainerConverterResolutionPlugin())
    container.register_instance[Converter[list, Tuple[float, float, float]]](tuple)
    config_plugin = ContainerConfigurationResolutionPlugin()
    container.add_plugin(config_plugin)
    arg_parse_provider = ArgParseConfigurationProvider()
    for config_class in config_classes:
        arg_parse_provider.manage_configuration(config_class)
    arg_parser = ArgumentParser()
    arg_parser.add_argument(
        "--config-path",
        type=Path,
        help="Path to JSON config file",
        required=False
    )
    arg_parse_provider.register_arguments(arg_parser)
    args = arg_parser.parse_args(sys.argv[1:])
    arg_parse_provider.process_parsed_arguments(args)
    container.register_instance[BeanList[ConfigurationProvider]](arg_parse_provider)
    if args.config_path is not None:
        config_path: Path = args.config_path
        container.register_instance[BeanList[ConfigurationProvider]](
            TOMLConfigurationProvider(config_path.read_text())
        )
    return container