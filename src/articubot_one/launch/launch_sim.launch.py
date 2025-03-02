import os

from ament_index_python.packages import get_package_share_directory


from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.actions import ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node



def generate_launch_description():
    # Include the robot_state_publisher launch file, provided by our own package. Force sim time to be enabled
    # !!! MAKE SURE YOU SET THE PACKAGE NAME CORRECTLY !!!

    package_name='articubot_one' #<--- เปลี่ยนPackageตรงนี้
    
    # Paths to parameter files
    pkg_share = get_package_share_directory(package_name)
    world_file = os.path.join(pkg_share, 'worlds', 'MNP_mapNoBot.world')
    nav2_params = os.path.join(pkg_share, 'config', 'nav2_params.yaml')
    slam_params = os.path.join(pkg_share, 'config', 'mapper_params_online_async.yaml')
    

    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','rsp.launch.py'
                )]), launch_arguments={'use_sim_time': 'true'}.items()
    )

    # Include the Gazebo launch file, provided by the gazebo_ros package
    gazebo = IncludeLaunchDescription(
             PythonLaunchDescriptionSource([os.path.join(
                get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')]),
             launch_arguments={
                 'world': world_file,'use_sim_time': 'true'}.items(),
    )

    # Run the spawner node from the gazebo_ros package. The entity name doesn't really matter if you only have a single robot.
    spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py',
                        arguments=['-topic', 'robot_description',
                                   '-entity', 'MiniP_bot',#<--- เปลี่ยนชื่อหุ่นยนต์ตรงนี้
                                   '-x', '0', '-y', '0', '-z', '0.6',# Set initial point
                                   '-R', '0', '-P', '0', '-Y', '1.57'# Set Rotage
                                ],
                        output='screen')
    
     # Launch SLAM tool with parameters from the provided YAML file
    slam = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('slam_toolbox'),'launch','online_async_launch.py'
                )]), 
                launch_arguments={'use_sim_time': 'true', 'params_file': slam_params}.items()
    )

    # Nav2 Stack
    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('nav2_bringup'), 'launch', 'navigation_launch.py')]),
        launch_arguments={'use_sim_time': 'true', 'params_file': nav2_params}.items()
    )

    twist_mux = Node(
        package='twist_mux',
        executable='twist_mux',
        output='screen',
        parameters=[os.path.join(pkg_share, 'config', 'twist_mux.yaml')],
        remappings=[('/cmd_vel', '/diff_cont/cmd_vel_unstamped')],
    )
    controller_manager = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "gripper_controller",
        ],
    )


    # Launch them all!
    return LaunchDescription([
        nav2,
        rsp,
        gazebo,
        spawn_entity,
        twist_mux,
        slam,
        controller_manager
    
    ])
