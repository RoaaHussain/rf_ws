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

## 4. Device names (udev)
Create /etc/udev/rules.d/99-robot.rules with:

    # LiDAR RPLIDAR (CP210x)
    SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", SYMLINK+="rplidar"
    # ESP32 board (CH340)
    SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", SYMLINK+="esp32"

Then:

    sudo udevadm control --reload-rules && sudo udevadm trigger
    sudo usermod -aG dialout,video $USER   # then log out and in

Devices appear as /dev/rplidar and /dev/esp32.

## 5. ~/.bashrc

    source /opt/ros/jazzy/setup.bash
    source ~/rf_ws/install/setup.bash
    export ROS_DOMAIN_ID=1
    export ROS_AUTOMATIC_DISCOVERY_RANGE=SUBNET
    export ROS_STATIC_PEERS=<IP of the PC running RViz>

## 6. Firmware
Uploaded from the Arduino IDE. Board / port: (fill in)

## 7. Run
    ros2 launch my_bot launch_robot.launch.py
