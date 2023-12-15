#!/usr/bin/env python3

# Copyright (c) 2020-2023, Michael Ferguson
# All rights reserved.
#
# Software License Agreement (BSD License 2.0)
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import os
import sys

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription, LaunchService
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node

def launch_file(name):
    # Get the path to an included launch file
    return os.path.join(
        get_package_share_directory('robomagellan'),
        'launch',
        name
    )

def generate_launch_description():
    return LaunchDescription([
        # Arguments first
        DeclareLaunchArgument('offline', default_value='false'),
        DeclareLaunchArgument('gen', default_value='gen1'),

        # Drivers
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([
                    get_package_share_directory('robomagellan'),
                    'launch',
                    LaunchConfiguration('gen'),
                    'drivers.launch.py']
                )
            ),
            condition=UnlessCondition(LaunchConfiguration('offline')),
        ),

        # Process GPS sentences into Fix
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([launch_file('compute/gps.launch.py')]),
            launch_arguments={'use_sim_time': LaunchConfiguration('offline')}.items()
        ),

        # Process IMU into usable values
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([launch_file('compute/imu.launch.py')]),
            launch_arguments={'use_sim_time': LaunchConfiguration('offline')}.items()
        ),

        # TODO: Local frame localization (base_link to odom)
        #<include file="$(find robomagellan)/launch/compute/ekf_local.launch.xml" />

        # TODO: Global frame localization (map to odom)
        #<include file="$(find robomagellan)/launch/compute/ekf_global.launch.xml" />

        # TODO: Setup global localization

        # TODO: add navigation, yeah, that is totally one line

    ])


def main(argv=sys.argv[1:]):
    """Run nodes via launch."""
    ld = generate_launch_description()
    ls = LaunchService(argv=argv)
    ls.include_launch_description(ld)
    return ls.run()


if __name__ == '__main__':
    main()
