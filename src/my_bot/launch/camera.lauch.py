import os

from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # تشغيل نود الكاميرا مع تحديد الأبعاد المطلوبة (320x240)
        Node(
            package='camera_ros',
            executable='camera_node',
            name='camera_node',
            parameters=[
                {'width': 320},
                {'height': 240}
            ],
            output='screen'
        )
    ])