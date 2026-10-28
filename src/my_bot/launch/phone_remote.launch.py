import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node


def generate_launch_description():
    web_dir = os.path.join(get_package_share_directory('my_bot'), 'web')

    rosbridge = Node(
        package='rosbridge_server',
        executable='rosbridge_websocket',
        output='screen',
    )
    web = ExecuteProcess(
        cmd=['python3', '-m', 'http.server', '8000'],
        cwd=web_dir,
        output='screen',
    )
    return LaunchDescription([rosbridge, web])