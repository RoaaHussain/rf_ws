#include "my_bot/my_bot_hardware.hpp"
#include "hardware_interface/types/hardware_interface_type_values.hpp"
#include "rclcpp/rclcpp.hpp"

namespace my_bot
{

hardware_interface::CallbackReturn MyBotHardware::on_init(
  const hardware_interface::HardwareInfo & info)
{
  if (hardware_interface::SystemInterface::on_init(info) !=
      hardware_interface::CallbackReturn::SUCCESS)
  {
    return hardware_interface::CallbackReturn::ERROR;
  }

  cfg_.left_wheel_name = info_.hardware_parameters["left_wheel_name"];
  cfg_.right_wheel_name = info_.hardware_parameters["right_wheel_name"];
  cfg_.loop_rate = std::stof(info_.hardware_parameters["loop_rate"]);
  cfg_.device = info_.hardware_parameters["device"];
  cfg_.baud_rate = std::stoi(info_.hardware_parameters["baud_rate"]);
  cfg_.timeout_ms = std::stoi(info_.hardware_parameters["timeout_ms"]);
  cfg_.enc_counts_per_rev = std::stoi(info_.hardware_parameters["enc_counts_per_rev"]);

  if (info_.hardware_parameters.count("pid_p") > 0)
  {
    cfg_.pid_p = std::stoi(info_.hardware_parameters["pid_p"]);
    cfg_.pid_d = std::stoi(info_.hardware_parameters["pid_d"]);
    cfg_.pid_i = std::stoi(info_.hardware_parameters["pid_i"]);
    cfg_.pid_o = std::stoi(info_.hardware_parameters["pid_o"]);
  }
  else
  {
    RCLCPP_INFO(rclcpp::get_logger("MyBotHardware"), "PID values not supplied, using Arduino defaults.");
  }

  wheel_l_.setup(cfg_.left_wheel_name, cfg_.enc_counts_per_rev);
  wheel_r_.setup(cfg_.right_wheel_name, cfg_.enc_counts_per_rev);

  for (const hardware_interface::ComponentInfo & joint : info_.joints)
  {
    if (joint.command_interfaces.size() != 1 ||
        joint.command_interfaces[0].name != hardware_interface::HW_IF_VELOCITY)
    {
      RCLCPP_FATAL(rclcpp::get_logger("MyBotHardware"),
        "Joint '%s' must expose exactly 1 velocity command interface.", joint.name.c_str());
      return hardware_interface::CallbackReturn::ERROR;
    }
    if (joint.state_interfaces.size() != 2 ||
        joint.state_interfaces[0].name != hardware_interface::HW_IF_POSITION ||
        joint.state_interfaces[1].name != hardware_interface::HW_IF_VELOCITY)
    {
      RCLCPP_FATAL(rclcpp::get_logger("MyBotHardware"),
        "Joint '%s' must expose position then velocity state interfaces.", joint.name.c_str());
      return hardware_interface::CallbackReturn::ERROR;
    }
  }

  return hardware_interface::CallbackReturn::SUCCESS;
}

std::vector<hardware_interface::StateInterface> MyBotHardware::export_state_interfaces()
{
  std::vector<hardware_interface::StateInterface> state_interfaces;
  state_interfaces.emplace_back(wheel_l_.name, hardware_interface::HW_IF_POSITION, &wheel_l_.pos);
  state_interfaces.emplace_back(wheel_l_.name, hardware_interface::HW_IF_VELOCITY, &wheel_l_.vel);
  state_interfaces.emplace_back(wheel_r_.name, hardware_interface::HW_IF_POSITION, &wheel_r_.pos);
  state_interfaces.emplace_back(wheel_r_.name, hardware_interface::HW_IF_VELOCITY, &wheel_r_.vel);
  return state_interfaces;
}

std::vector<hardware_interface::CommandInterface> MyBotHardware::export_command_interfaces()
{
  std::vector<hardware_interface::CommandInterface> command_interfaces;
  command_interfaces.emplace_back(wheel_l_.name, hardware_interface::HW_IF_VELOCITY, &wheel_l_.cmd);
  command_interfaces.emplace_back(wheel_r_.name, hardware_interface::HW_IF_VELOCITY, &wheel_r_.cmd);
  return command_interfaces;
}

hardware_interface::CallbackReturn MyBotHardware::on_configure(const rclcpp_lifecycle::State &)
{
  RCLCPP_INFO(rclcpp::get_logger("MyBotHardware"), "Configuring...");
  if (comms_.connected()) { comms_.disconnect(); }
  comms_.connect(cfg_.device, cfg_.baud_rate, cfg_.timeout_ms);
  RCLCPP_INFO(rclcpp::get_logger("MyBotHardware"), "Configured.");
  return hardware_interface::CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn MyBotHardware::on_cleanup(const rclcpp_lifecycle::State &)
{
  if (comms_.connected()) { comms_.disconnect(); }
  return hardware_interface::CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn MyBotHardware::on_activate(const rclcpp_lifecycle::State &)
{
  RCLCPP_INFO(rclcpp::get_logger("MyBotHardware"), "Activating...");
  if (!comms_.connected()) { return hardware_interface::CallbackReturn::ERROR; }
  if (cfg_.pid_p > 0) { comms_.set_pid_values(cfg_.pid_p, cfg_.pid_d, cfg_.pid_i, cfg_.pid_o); }
  return hardware_interface::CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn MyBotHardware::on_deactivate(const rclcpp_lifecycle::State &)
{
  return hardware_interface::CallbackReturn::SUCCESS;
}

hardware_interface::return_type MyBotHardware::read(
  const rclcpp::Time &, const rclcpp::Duration & period)
{
  if (!comms_.connected()) { return hardware_interface::return_type::ERROR; }

  comms_.read_encoder_values(wheel_l_.enc, wheel_r_.enc);
  double dt = period.seconds();

  double pos_prev = wheel_l_.pos;
  wheel_l_.pos = wheel_l_.calc_enc_angle();
  wheel_l_.vel = (wheel_l_.pos - pos_prev) / dt;

  pos_prev = wheel_r_.pos;
  wheel_r_.pos = wheel_r_.calc_enc_angle();
  wheel_r_.vel = (wheel_r_.pos - pos_prev) / dt;

  return hardware_interface::return_type::OK;
}

hardware_interface::return_type MyBotHardware::write(
  const rclcpp::Time &, const rclcpp::Duration &)
{
  if (!comms_.connected()) { return hardware_interface::return_type::ERROR; }

  int l_counts_per_loop = wheel_l_.cmd / wheel_l_.rads_per_count / cfg_.loop_rate;
  int r_counts_per_loop = wheel_r_.cmd / wheel_r_.rads_per_count / cfg_.loop_rate;
  comms_.set_motor_values(l_counts_per_loop, r_counts_per_loop);

  return hardware_interface::return_type::OK;
}

}  // namespace my_bot

#include "pluginlib/class_list_macros.hpp"
PLUGINLIB_EXPORT_CLASS(my_bot::MyBotHardware, hardware_interface::SystemInterface)