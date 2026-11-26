# my_bot - setup on a new board (Ubuntu 24.04 + ROS 2 Jazzy)

## 1. System
Flash Ubuntu 24.04, then do ONE full upgrade before installing ROS:

    sudo apt update && sudo apt full-upgrade -y && sudo reboot

## 2. ROS packages

    sudo apt install -y ros-jazzy-ros-base ros-dev-tools \
      ros-jazzy-ros2-control ros-jazzy-hardware-interface \
      ros-jazzy-diff-drive-controller ros-jazzy-joint-state-broadcaster \
      ros-jazzy-gz-ros2-control ros-jazzy-ros-gz ros-jazzy-xacro \
      ros-jazzy-rplidar-ros ros-jazzy-slam-toolbox \
      ros-jazzy-navigation2 ros-jazzy-nav2-bringup \
      ros-jazzy-twist-mux ros-jazzy-twist-stamper \
      ros-jazzy-teleop-twist-keyboard ros-jazzy-rosbridge-suite \
      ros-jazzy-camera-info-manager ros-jazzy-cv-bridge

## 3. Get and build the code

    git clone https://github.com/RoaaHussain/rf_ws.git ~/rf_ws
    cd ~/rf_ws && source /opt/ros/jazzy/setup.bash
    colcon build --symlink-install --packages-select my_bot

Build only my_bot first; the camera/libcamera packages take very long.

## 4. Device names
The code uses /dev/serial/by-id paths, no udev rules needed:

- Arduino Uno: /dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_5513931333535180C152-if00 (set in src/my_bot/description/ros2_control.xacro). The path contains this Uno's serial number: if the Uno is replaced, update it (ls /dev/serial/by-id/).
- RPLIDAR: /dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0 (set in src/my_bot/launch/rplidar.launch.py)

Permissions:

    sudo usermod -aG dialout,video $USER   # then log out and in

## 5. ~/.bashrc

    source /opt/ros/jazzy/setup.bash
    source ~/rf_ws/install/setup.bash
    export ROS_DOMAIN_ID=1
    export ROS_AUTOMATIC_DISCOVERY_RANGE=SUBNET
    export ROS_STATIC_PEERS=<IP of the PC running RViz>

## 6. Firmware
Arduino Uno (genuine), uploaded from the Arduino IDE.

## 7. Run
    ros2 launch my_bot launch_robot.launch.py
