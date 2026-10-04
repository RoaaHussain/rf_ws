import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, RegisterEventHandler
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch.event_handlers import OnProcessStart
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    package_name = 'my_bot'

    # Robot State Publisher — this is the REAL robot, so:
    #   - use_sim_time must be false
    #   - since ros2_control.xacro's sim_mode is tied to use_sim_time,
    #     'false' here is what makes it load MyBotHardware (real Arduino
    #     plugin) instead of the Gazebo hardware interface
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory(package_name),
                'launch',
                'rsp.launch.py'
            )
        ]),
        launch_arguments={
            'use_sim_time': 'false',
            'use_jsp_gui': 'false',
        }.items()
    )

    # Pull the already-processed robot_description straight from the running
    # robot_state_publisher node (avoids re-running xacro here, and guarantees
    # we get exactly the URDF rsp is using). Needs Command with a capital C.
    robot_description = Command(['ros2 param get --hide-type /robot_state_publisher robot_description'])

    controller_params_file = os.path.join(
        get_package_share_directory(package_name),
        'config',
        'controllers.yaml'
    )

    controller_manager = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[{'robot_description': ParameterValue(robot_description, value_type=str)}, controller_params_file],
        output='screen',
    )

    # Give robot_state_publisher time to fully start and declare the
    # robot_description param before we try to read it above, or the
    # controller_manager will fail to start.
    delayed_controller_manager = TimerAction(period=3.0, actions=[controller_manager])

    diff_drive_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_cont'],
        output='screen',
    )

    delayed_diff_drive_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=controller_manager,
            on_start=[diff_drive_spawner],
        )
    )

    joint_broad_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_broad'],
        output='screen',
    )

    delayed_joint_broad_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=controller_manager,
            on_start=[joint_broad_spawner],
        )
    )

    return LaunchDescription([
        rsp,
        delayed_controller_manager,
        delayed_diff_drive_spawner,
        delayed_joint_broad_spawner,
    ])

#import os
#from ament_index_python.packages import get_package_share_directory
#from launch import LaunchDescription
#from launch.actions import IncludeLaunchDescription
#from launch.launch_description_sources import PythonLaunchDescriptionSource
#from launch_ros.actions import Node
#from launch.substitutions import PathJoinSubstitution
#from launch_ros.substitutions import FindPackageShare

#def generate_launch_description():
   # package_name = 'my_bot'

    # Robot State Publisher
   # rsp = IncludeLaunchDescription(
    #    PythonLaunchDescriptionSource([
     #       os.path.join(
      #          get_package_share_directory(package_name),
       #         'launch',
        #        'rsp.launch.py'
         #   )
      #  ]),
      #  launch_arguments={'use_sim_time': 'true'}.items()
   # )

    # World path
  #  world_path = PathJoinSubstitution([
   #     FindPackageShare(package_name),
    #    'worlds',
     #   'my_world.sdf'
   # ])

    # Gazebo Sim
   # gazebo = IncludeLaunchDescription(
    #    PythonLaunchDescriptionSource([
     #       os.path.join(
      #          get_package_share_directory('ros_gz_sim'),
       #         'launch',
        #        'gz_sim.launch.py'
         #   )
      #  ]),
      #  launch_arguments={'gz_args': ['-r ', world_path]}.items()
  #  )

    # Spawn the robot
   # spawn_entity = Node(
    #    package='ros_gz_sim',
     #   executable='create',
      #  arguments=['-topic', 'robot_description',
       #            '-name', 'my_bot',
        #           '-allow_renaming', 'false',
         #          '-z', '0.1'],
     #   output='screen'
   # )

    # Bridges
   # bridge = Node(
    #    package='ros_gz_bridge',
     #   executable='parameter_bridge',
      #  arguments=[
       #     '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
        #    '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
         #   '/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',
          #  '/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan',
           # '/joint_states@sensor_msgs/msg/JointState@gz.msgs.Model',
       # ],
      #  output='screen'
   # )

    # Joint State Publisher GUI (for continuous joints like wheels)
   # joint_state_publisher_gui = Node(
    #    package='joint_state_publisher_gui',
     #   executable='joint_state_publisher_gui',
      #  name='joint_state_publisher_gui',
       # output='screen'
  #  )

   # return LaunchDescription([
    #    rsp,
     #   gazebo,
      #  spawn_entity,
       # bridge,
        #joint_state_publisher_gui,   # ←←← ADD THIS LINE
   # ])
