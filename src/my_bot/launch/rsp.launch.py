import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import xacro


def generate_launch_description():

    use_sim_time = LaunchConfiguration('use_sim_time')
    use_jsp_gui = LaunchConfiguration('use_jsp_gui')

    pkg_path = get_package_share_directory('my_bot')
    xacro_file = os.path.join(pkg_path, 'description', 'robot.urdf.xacro')
    robot_description_config = xacro.process_file(xacro_file).toxml()

    params = {
        'robot_description': robot_description_config,
        'use_sim_time': use_sim_time,
    }

    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[params]
    )

    # Only useful when there is no real joint-state source (e.g. viewing the
    # robot in RViz without Gazebo). When included from sim.launch.py this is
    # set to false, since Gazebo already publishes real joint states.
    node_joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(use_jsp_gui),
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true', # جعلناها true افتراضياً للمحاكاة
            description='Use simulation (Gazebo) clock if true'),
        DeclareLaunchArgument(
            'use_jsp_gui',
            default_value='false', # جعلناها false افتراضياً لأن Gazebo هو من سينشر المفاصل
            description='Launch joint_state_publisher_gui. Set false when a '
                        'real joint-state source (e.g. Gazebo) is present.'),
        node_robot_state_publisher,
        node_joint_state_publisher_gui,
    ])


#import os
#from ament_index_python.packages import get_package_share_directory
#from launch import LaunchDescription
#from launch.substitutions import LaunchConfiguration
#from launch.actions import DeclareLaunchArgument
#from launch_ros.actions import Node

#import xacro


#def generate_launch_description():

    # Check if we're told to use sim time
 #   use_sim_time = LaunchConfiguration('use_sim_time')

    # Process the URDF file
  #  pkg_path = os.path.join(get_package_share_directory('my_bot'))
   # xacro_file = os.path.join(pkg_path,'description','robot.urdf.xacro')
    #robot_description_config = xacro.process_file(xacro_file).toxml()
    
    # Create a robot_state_publisher node
   # params = {'robot_description': robot_description_config, 'use_sim_time': use_sim_time}
   # node_robot_state_publisher = Node(
    #    package='robot_state_publisher',
     #   executable='robot_state_publisher',
      #  output='screen',
       # parameters=[params]
  #  )

 #   node_joint_state_publisher = Node(
  #      package='joint_state_publisher_gui',
   #     executable='joint_state_publisher_gui',
    #    name='joint_state_publisher_gui'
   # )



    # Launch!
   # return LaunchDescription([
    #    DeclareLaunchArgument(
     #       'use_sim_time',
      #      default_value='false',
       #     description='Use sim time if true'),

     #   node_robot_state_publisher ,
      #  node_joint_state_publisher
   # ])
