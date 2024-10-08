# Author: Addison Sears-Collins
# Date: August 27, 2021
# Description: Launch a basic mobile robot URDF file using Rviz.
# https://automaticaddison.com

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():

  # Set the path to different files and folders.
  pkg_gazebo_ros = FindPackageShare(package='gazebo_ros').find('gazebo_ros')   
  pkg_share = FindPackageShare(package='bigfootbot_description').find('bigfootbot_description')
  default_launch_dir = os.path.join(pkg_share, 'launch')
  default_model_path = os.path.join(pkg_share, 'urdf/bigfootbot.urdf')
  robot_name_in_urdf = 'bigfootbot'
  default_rviz_config_path = os.path.join(pkg_share, 'rviz/urdf_config.rviz')
  world_file_name = 'bigfootbot_world/smalltown.world'
  world_path = os.path.join(pkg_share, 'worlds', world_file_name)
  
  # Launch configuration variables specific to simulation
  #gui = LaunchConfiguration('gui') # Flag to enable joint_state_publisher_gui
  headless = LaunchConfiguration('headless') # Whether to execute gzclient
  model = LaunchConfiguration('model')
  rviz_config_file = LaunchConfiguration('rviz_config_file')
  use_robot_state_pub = LaunchConfiguration('use_robot_state_pub') # Whether to start the robot state publisher
  use_rviz = LaunchConfiguration('use_rviz') # Whether to start RVIZ
  use_sim_time = LaunchConfiguration('use_sim_time') # Use simulation (Gazebo) clock if true
  use_simulator = LaunchConfiguration('use_simulator') # Whether to start the simulator
  world = LaunchConfiguration('world') # Full path to the world model file to load

  # Declare the launch arguments  
  declare_model_path_cmd = DeclareLaunchArgument(
    name='model', 
    default_value=default_model_path, 
    description='Absolute path to robot urdf file')
    
  declare_rviz_config_file_cmd = DeclareLaunchArgument(
    name='rviz_config_file',
    default_value=default_rviz_config_path,
    description='Full path to the RVIZ config file to use')
    
  #declare_use_joint_state_publisher_cmd = DeclareLaunchArgument(
  # name='gui',
  # default_value='True',
  # description='Flag to enable joint_state_publisher_gui')

  declare_simulator_cmd = DeclareLaunchArgument(
    name='headless',
    default_value='False',
    description='Whether to execute gzclient')
  
  declare_use_robot_state_pub_cmd = DeclareLaunchArgument(
    name='use_robot_state_pub',
    default_value='True',
    description='Whether to start the robot state publisher')

  declare_use_rviz_cmd = DeclareLaunchArgument(
    name='use_rviz',
    default_value='True',
    description='Whether to start RVIZ')
    
  declare_use_sim_time_cmd = DeclareLaunchArgument(
    name='use_sim_time',
    default_value='True',
    description='Use simulation (Gazebo) clock if true')

  declare_use_simulator_cmd = DeclareLaunchArgument(
    name='use_simulator',
    default_value='True',
    description='Whether to start the simulator')

  declare_world_cmd = DeclareLaunchArgument(
    name='world',
    default_value=world_path,
    description='Full path to the world model file to load')
   
  # Specify the actions

  # Publish the joint state values for the non-fixed joints in the URDF file.
  #start_joint_state_publisher_cmd = Node(
  # condition=UnlessCondition(gui),
  # package='joint_state_publisher',
  # executable='joint_state_publisher',
  # name='joint_state_publisher')

  # A GUI to manipulate the joint state values
  #start_joint_state_publisher_gui_node = Node(
  # condition=IfCondition(gui),
  # package='joint_state_publisher_gui',
  # executable='joint_state_publisher_gui',
  # name='joint_state_publisher_gui')

  # Start Gazebo server
  start_gazebo_server_cmd = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')),
    condition=IfCondition(use_simulator),
    launch_arguments={'world': world}.items())

  # Start Gazebo client    
  start_gazebo_client_cmd = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')),
    condition=IfCondition(PythonExpression([use_simulator, ' and not ', headless])))

  # Subscribe to the joint states of the robot, and publish the 3D pose of each link.
  start_robot_state_publisher_cmd = Node(
    condition=IfCondition(use_robot_state_pub),
    package='robot_state_publisher',
    executable='robot_state_publisher',
    parameters=[{'use_sim_time': use_sim_time, 
    'robot_description': Command(['xacro ', model])}],
    arguments=[default_model_path])  # TODO: Check - it seems robot_state_publisher 
                                     # doesn't have this argument anymore

  # Launch RViz
  start_rviz_cmd = Node(
    condition=IfCondition(use_rviz),
    package='rviz2',
    executable='rviz2',
    name='rviz2',
    output='screen',
    arguments=['-d', rviz_config_file])
  
  # Create the launch description and populate
  ld = LaunchDescription()

  # Declare the launch options
  ld.add_action(declare_model_path_cmd)
  ld.add_action(declare_rviz_config_file_cmd)
  #ld.add_action(declare_use_joint_state_publisher_cmd)
  ld.add_action(declare_simulator_cmd)
  ld.add_action(declare_use_robot_state_pub_cmd)  
  ld.add_action(declare_use_rviz_cmd) 
  ld.add_action(declare_use_sim_time_cmd)
  ld.add_action(declare_use_simulator_cmd)
  ld.add_action(declare_world_cmd)

  # Add any actions
  #ld.add_action(start_joint_state_publisher_cmd)
  #ld.add_action(start_joint_state_publisher_gui_node)
  ld.add_action(start_gazebo_server_cmd)
  ld.add_action(start_gazebo_client_cmd)
  ld.add_action(start_robot_state_publisher_cmd)
  ld.add_action(start_rviz_cmd)

  return ld