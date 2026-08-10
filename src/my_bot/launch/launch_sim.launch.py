import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    package_name = 'my_bot'

    # Robot State Publisher (with the fake joint-state GUI disabled, since
    # Gazebo provides the real joint states through the bridge below)
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory(package_name),
                'launch',
                'rsp.launch.py'
            )
        ]),
        launch_arguments={
            'use_sim_time': 'true',
            'use_jsp_gui': 'false',
        }.items()
    )

    world_path = PathJoinSubstitution([
        FindPackageShare(package_name),
        'worlds',
        'my_world.sdf'
    ])

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            )
        ]),
        launch_arguments={'gz_args': ['-r ', world_path]}.items()
    )

    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'my_bot',
            '-allow_renaming', 'false',
            '-z', '0.1',
        ],
        output='screen'
    )

    # Small delay so robot_state_publisher has published robot_description
    # before Gazebo is asked to spawn from that topic.
    delayed_spawn_entity = TimerAction(period=2.0, actions=[spawn_entity])

    # ROS <-> GZ bridge. Directions are restricted to the direction each
    # topic actually needs: '[' = GZ->ROS only, ']' = ROS->GZ only.
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
        ],
        output='screen',
        parameters=[{'use_sim_time': True}],
    )


    joint_broad_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_broad'],
        output='screen',
    )

    diff_drive_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_cont'],
        output='screen',
    )

    return LaunchDescription([
        rsp,
        gazebo,
        delayed_spawn_entity,
        bridge,
        joint_broad_spawner,
        diff_drive_spawner,
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