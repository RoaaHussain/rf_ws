import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def launch_setup(context, *args, **kwargs):
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_ros2_control = LaunchConfiguration('use_ros2_control')
    use_jsp_gui = LaunchConfiguration('use_jsp_gui')
    sim_mode = LaunchConfiguration('sim_mode')

    pkg_path = get_package_share_directory('my_bot')
    xacro_file = os.path.join(pkg_path, 'description', 'robot.urdf.xacro')

    robot_description_config = ParameterValue(
        Command([
            'xacro ', xacro_file,
            ' use_ros2_control:=', use_ros2_control,
            ' sim_mode:=', sim_mode,
        ]),
        value_type=str,
    )

    params = {
        'robot_description': robot_description_config,
        'use_sim_time': use_sim_time,
    }

    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[params],
    )

    node_joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(use_jsp_gui),
    )

    return [node_robot_state_publisher, node_joint_state_publisher_gui]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'),
        DeclareLaunchArgument(
            'use_ros2_control',
            default_value='true',
            description='Use ros2_control if true'),
        DeclareLaunchArgument(
            'sim_mode',
            default_value='false',
            description='Use Gazebo ros2_control plugin if true, '
                        'real hardware plugin if false'),
        DeclareLaunchArgument(
            'use_jsp_gui',
            default_value='false',
            description='Launch joint_state_publisher_gui. Set false when a '
                        'real joint-state source (e.g. Gazebo) is present.'),
        OpaqueFunction(function=launch_setup),
    ])