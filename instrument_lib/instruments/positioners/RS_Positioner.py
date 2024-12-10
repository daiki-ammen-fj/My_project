"""Driver for Rhode & Schwarz ATS1800C Positioner."""

from logging import Logger
import socket
import time
from typing import Optional, Tuple

import numpy as np

from instrument_lib.instruments.instrument import Instrument
from instrument_lib.utils import InstrumentError, InstrumentIdentificationInfo, PositionerError

BUFFER_SIZE: int = 1024
TERM_CHAR: str = "\x00"


class RS_Positioner(Instrument):  # noqa: N801
    """Positioner.

    This instrument controls the position of the DUT.
    """

    ACCEPTED_MODELS = [
        "ATS1800C",
    ]

    def __init__(
        self,
        ip_address: str | None = None,
        logger: Optional[Logger] = None,
        port: int = 200,
        retry: int = 10,
        theta_min: float = -181,
        theta_max: float = 181,
        phi_min: float = -181,
        phi_max: float = 181,
        position_accuracy_deg: float = 0.5,
        max_travel_time: float = 150,
    ):
        """Constructor.

        :param ip_address: IP Address as a string.
        :param logger: Logger object.
        :param port: Port to connect to.
        :param retry: Number of times to retry certain commands.
        :param theta_min: Minimum theta value.
        :param theta_max: Maximum theta value.
        :param phi_min: Minimum phi value.
        :param phi_max: Maximum phi value.
        :param position_accuracy_deg: Degree of accuracy for position.
        :param max_travel_time: Maximum time that the positioner can spend moving.
        """
        super().__init__()
        self.logger = logger
        self.ip_address: str | None = ip_address
        self.port: int = port
        self.retry: int = retry
        self.theta_min: float = theta_min
        self.theta_max: float = theta_max
        self.phi_min: float = phi_min
        self.phi_max: float = phi_max
        self.position_accuracy_deg: float = position_accuracy_deg
        self.max_travel_time: float = max_travel_time
        self.rsinstrument = True

    def connect(self) -> None:
        """Connect to instrument."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.ip_address, self.port))
            self.identify()
        except (InterruptedError, TimeoutError) as e:
            raise InstrumentError from e
        else:
            self.connected = True

    def identify(self) -> InstrumentIdentificationInfo:
        """Instrument identification."""
        positioner_id = self.get_positioner_id().split(",")
        self.identification = InstrumentIdentificationInfo(
            manufacturer=positioner_id[0],
            model=positioner_id[1],
            serial_number=positioner_id[2],
            firmware=positioner_id[3],
        )
        return self.identification

    def reset(self) -> None:
        """Reset device."""
        self.move_to_azimuth_elevation(0, 0)

    def close(self) -> None:
        """Close connection to instrument."""
        self.sock.close()

    def send_command(self, command: str) -> str:
        """Send raw command to instrument.

        :param command: string of command to send.
        """
        self.sock.sendall(f"{command}{TERM_CHAR}".encode())
        data: bytes = self.sock.recv(BUFFER_SIZE)
        return data.decode("utf-8").strip(TERM_CHAR)

    def check_angel_within_limits(self, axis: str, angle: float) -> bool:
        """Checks that the angle is within the limits set.

        during the creation of the positioner object.
        """
        if axis == "Theta":
            return self.theta_min < angle < self.theta_max
        else:
            return self.phi_min < angle < self.phi_max

    def translate_angle_to_ats1800c_coordinates(self, axis: str, angle_ets: float) -> float:
        """Angle translation to the coordinates of the ATS1800C chamber,.

        so that measurement angles are consistent between ATS1800C and ETS positioners
        In the ATS chamber case, the "top" of the antenna (closest to the "sky" in the ETS)
        corresponds to the position of the snowflake closest to the horn
        """
        if axis == "Phi":
            angle: float = -angle_ets
        else:
            angle = angle_ets

        if abs(angle) < 1e-6:
            angle = 1e-6

        return angle

    def translate_angle_to_ets_coordinates(self, axis: str, angle_ats: float) -> float:
        """Angle translation to the coordinates of the ETS chamber, so that measurement angles are.

        consistent between ATS1800C and ETS positioners
        In the ATS chamber case, the "top" of the antenna (closest to the "sky" in the ETS)
        corresponds to the position of the snowflake closest to the horn
        """
        if axis == "Phi":
            angle: float = -angle_ats
        else:
            angle = angle_ats

        return angle

    def get_motor_from_axis(self, axis: str) -> str:
        """Gets motor from the axis."""
        return "ELEV" if axis == "Theta" else "AZIM"

    def get_positioner_ip(self) -> str | None:
        """Return positioner IP."""
        return self.ip_address

    def get_positioner_id(self) -> str:
        """Return positioner ID."""
        return self.cmd_positioner_id()

    def get_current_position_phi(self) -> float:
        """Return the current Phi position (ie Azimuth positioner)."""
        return self.cmd_get_axis_position("Phi")

    def get_current_position_theta(self) -> float:
        """Return the current Theta position (ie Elevation positioner)."""
        return self.cmd_get_axis_position("Theta")

    def get_current_position_theta_phi(self) -> Tuple[float, float]:
        """Return the current position in Theta-Phi coordinate system."""
        return self.get_current_position_theta(), self.get_current_position_phi()

    def get_current_position(self) -> Tuple[float, float]:
        """Return the current position in Theta-Phi coordinate system."""
        return self.get_current_position_theta_phi()

    def get_current_position_az_el(self) -> Tuple[float, float]:
        """Return the current position in Azimuth-Elevation coordinate system."""
        theta: float = 0
        phi: float = 0
        theta, phi = self.get_current_position()

        azimuth: float = 0
        elevation: float = 0
        azimuth, elevation = self.thetaphi_to_azel(theta * np.pi / 180, phi * np.pi / 180)

        return azimuth, elevation

    def move_to_theta_phi(self, theta: float, phi: float) -> None:
        """Move the positioner to a certain angle defined in Theta-Phi coordinate system."""
        if (theta < self.theta_min) or (theta > self.theta_max):
            raise ValueError(f"Theta must be between {self.theta_max} and {self.theta_min}")

        if (phi < self.phi_min) or (phi > self.phi_max):
            raise ValueError(f"Phi must be between {self.phi_max} and {self.phi_min}")

        self.seek_position("Theta", theta)
        self.seek_position("Phi", phi)

    def move_to_azimuth_elevation(self, azimuth: float, elevation: float) -> None:
        """Move the positioner to a certain angle defined in Azimuth-Elevation coordinate system."""
        theta_rad: float = 0
        phi_rad: float = 0
        theta_rad, phi_rad = self.azel_to_thetaphi(azimuth * np.pi / 180, elevation * np.pi / 180)

        theta_deg: float = theta_rad * 180 / np.pi
        phi_deg: float = phi_rad * 180 / np.pi

        if (theta_deg < self.theta_min) or (theta_deg > self.theta_max):
            raise ValueError(f"Theta must be between {self.theta_max} and {self.theta_min}")

        if (phi_deg < self.phi_min) or (phi_deg > self.phi_max):
            raise ValueError(f"Phi must be between {self.phi_max} and {self.phi_min}")

        self.seek_position("Theta", theta_deg)
        self.seek_position("Phi", phi_deg)

    def move_to_degrees(self, id_: int, angle: float) -> None:
        """For compatibility with the other positioner."""
        if id_ == 2:
            self.seek_position("Theta", angle)
        elif id_ == 1:
            self.seek_position("Phi", angle)

    def cmd_get_axis_speed(self, axis: str) -> float:
        """Queries the speed of the azimuth/elevation axis in degrees per second (deg/s).

        CONT:AZIM:SPE
        CONT:ELEV:SPE
        Values below 0 or above the maximum limit are merged automatically
        to the minimum or maximum limit, respectively.
        We recommend a maximum azimuth speed of 70 deg/s for stepped
        measurement and 50 deg/s for hardware triggered measurement, or
        lower speeds for heavy DUTs.
        Range: 1 to 150
        """
        motor: str = self.get_motor_from_axis(axis)
        return float(self.send_command(f"CONT:{motor}:SPE?"))

    def cmd_set_axis_speed(self, axis: str, speed: float) -> None:
        """Sets the speed of the azimuth/elevation axis.

        CONT:AZIM:SPE <speed>
        CONT:ELEV:SPE <speed>
        Parameters:
        <speed> Sets the speed in degrees per second (deg/s).
        Values below 0 or above the maximum limit are merged automatically
        to the minimum or maximum limit, respectively.
        We recommend a maximum azimuth speed of 70 deg/s for stepped
        measurement and 50 deg/s for hardware triggered measurement, or
        lower speeds for heavy DUTs.
        Range: 1 to 150
        """
        motor: str = self.get_motor_from_axis(axis)
        self.send_command(f"CONT:{motor}:SPE {speed}")

    def cmd_get_axis_accceleration(self, axis: str) -> float:
        """Queries the acceleration of the azimuth/elevation axis.

        CONT:AZIM:ACC
        CONT:ELEV:ACC
        Parameters:
        <acceleration> Acceleration in degrees per second squared (deg /s2).
        Values below 0 or above the maximum limit are merged automatically
        to the minimum or maximum limit, respectively.
        We recommend a maximum azimuth acceleration of 2000 deg/s2.
        Range: 1 to 15000
        """
        motor: str = self.get_motor_from_axis(axis)
        return float(self.send_command(f"CONT:{motor}:ACC?"))

    def cmd_set_axis_acceleration(self, axis: str, accleration: float) -> None:
        """Sets or queries the acceleration of the azimuth/elevation axis.

        CONT:AZIM:ACC <acceleration>
        CONT:ELEV:ACC <acceleration>
        Parameters:
        <acceleration> Sets the acceleration in degrees per second squared (deg/s2).
        Values below 0 or above the maximum limit are merged automatically
        to the minimum or maximum limit, respectively.
        We recommend a maximum azimuth acceleration of 2000 deg/s2.
        Range: 1 to 15000
        """
        motor: str = self.get_motor_from_axis(axis)
        self.send_command(f"CONT:{motor}:ACC {accleration}")

    def cmd_axis_start(self, axis: str) -> None:
        """Starts the movement of the positioner axis to the target position."""
        motor: str = self.get_motor_from_axis(axis)
        self.send_command(f"CONT:{motor}:STAR")

    def cmd_axis_stop(self, axis: str) -> None:
        """Stops the movement of the azimuth/elevation axis."""
        motor: str = self.get_motor_from_axis(axis)
        self.send_command(f"CONT:{motor}:STOP")

    def cmd_get_axis_position(self, axis: str) -> float:
        """Queries the current position of the azimuth axis.

        (turntable, labeled 1 and 3 in Figure 4-9).
        The reply is a string that codes the current position in degrees with a resolution of 3
        digits after the period.
        """
        motor: str = self.get_motor_from_axis(axis)
        angle: float = float(self.send_command(f"SENS:{motor}:POS?"))

        return self.translate_angle_to_ets_coordinates(axis, angle)

    def cmd_get_axis_busy(self, axis: str) -> bool:
        """Queries the current activity state of the azimuth axis.

        * If the azimuth axis is busy, the reply is True.
        * If the axis is not busy, the reply is False.
        """
        motor: str = self.get_motor_from_axis(axis)
        return bool(int(self.send_command(f"SENS:{motor}:BUSY?")))

    def cmd_get_axis_trigger_enable(self, axis: str) -> str:
        """Queries the generation of a hardware trigger event at every given number.

        of degrees of elevation-axis movement. The number of degrees is specified by the
        command CONT:ELEV:TRIG:STEP.
        CONT:ELEV:TRIG:STAT
        Equivalent with "Trigger 1" in the user interface.
        The query command checks, if the trigger is enabled.
        Activating the elevation trigger deactivates the azimuth trigger.
        """
        motor: str = self.get_motor_from_axis(axis)
        return self.send_command(f"CONT:{motor}:TRIG:STAT?")

    def cmd_set_axis_trigger_enable(self, axis: str, flag: bool) -> None:
        """Enables or disables the generation of a hardware trigger event at every given number.

        of degrees of elevation-axis movement. The number of degrees is specified by the
        command CONT:ELEV:TRIG:STEP.
        Equivalent with "Trigger 1" in the user interface.
        The query command checks, if the trigger is enabled.
        Activating the elevation trigger deactivates the azimuth trigger.
        """
        motor: str = self.get_motor_from_axis(axis)
        flag_val: int = 1 if flag else 0
        self.send_command(f"CONT:{motor}:TRIG:STAT {flag_val}")

    def cmd_get_axis_trigger(self, axis: str) -> float:
        """Configures the elevation axis to generate a trigger event every given number of.

        degrees, if enabled by the command CONT:ELEV:TRIG:STAT.
        The range of step sizes depends on several parameters, for example azimuth speed
        and measurement instrument speed. We recommend a minimum step size of 3 deg for
        20 deg/s azimuth speed and 5deg for 50 deg/s azimuth speed.
        The query command returns the step size.
        """
        motor: str = self.get_motor_from_axis(axis)
        return float(self.send_command(f"CONT:{motor}:TRIG:STEP"))

    def cmd_set_axis_trigger(self, axis: str, step_size: float) -> None:
        """Configures the elevation axis to generate a trigger event every given number of.

        degrees, if enabled by the command CONT:ELEV:TRIG:STAT.
        The range of step sizes depends on several parameters, for example azimuth speed
        and measurement instrument speed. We recommend a minimum step size of 3 deg for
        20 deg/s azimuth speed and 5 deg for 50 deg/s azimuth speed.
        The query command returns the step size.
        """
        motor: str = self.get_motor_from_axis(axis)
        self.send_command(f"CONT:{motor}:TRIG:STEP {step_size}")

    def cmd_get_axis_offset(self, axis: str) -> float:
        """Configures an offset for the azimuth axis, or queries the offset.

        Parameters:
        <offset> Specifies the offset in degrees.
        Range: -180 to 180
        """
        motor: str = self.get_motor_from_axis(axis)
        angle_ats: float = float(self.send_command(f"CONT:{motor}:OFFS"))
        return self.translate_angle_to_ets_coordinates(axis, angle_ats)

    def cmd_set_axis_offset(self, axis: str, offset: float) -> None:
        """Configures an offset for the azimuth axis, or queries the offset.

        Parameters:
        <offset> Specifies the offset in degrees.
        Range: -180 to 180
        """
        offset_ats: float = self.translate_angle_to_ats1800c_coordinates(axis, offset)
        motor: str = self.get_motor_from_axis(axis)
        self.send_command(f"CONT:{motor}:OFFS:{offset_ats}")

    def cmd_positioner_id(self) -> str:
        """Return positioner ID."""
        return self.send_command("*IDN?")

    def cmd_get_power_status(self) -> str:
        """Queries the power state of the positioning system.

        See also CONT:FESW:APOW on page 98.
        Parameters:
        <state> 1         Positioner power on.
                0        Positioner power off.
        """
        return self.send_command("CONT:SYST:APOW")

    def cmd_set_power_status(self, flag: bool) -> None:
        """Sets the power state of the positioning system.

        See also CONT:FESW:APOW on page 98.
        Parameters:
        <state> 1         Positioner power on.
                0         Positioner power off.
        """
        flag_val: int = 1 if flag else 0
        self.send_command(f"CONT:SYST:APOW {flag_val}")

    def cmd_get_dut_power_status(self) -> str:
        """Enables or disables the AC power socket (labeled 6 in Figure 4-9) for providing power.

        to the DUT. The query returns the socket's power state.
        Parameters:
        <state> 1         Socket provides AC power for the DUT.
                0        Socket does not provide power.
        """
        return self.send_command("CONT:SYST:DUT:APOW")

    def cmd_set_dut_power_status(self, flag: bool) -> None:
        """Enables or disables the AC power socket (labeled 6 in Figure 4-9) for providing power.

        to the DUT. The query returns the socket's power state.
        Parameters:
        <state> 1         Socket provides AC power for the DUT.
                0        Socket does not provide power.
        """
        flag_val: int = 1 if flag else 0
        self.send_command(f"CONT:SYST:DUT:APOW {flag_val}")

    def cmd_door_status(self) -> bool:
        """Queries the door's status, as described in Chapter 7.3.1, "Door Status", on page 59.

        - "1" = door locked
        - "0" = door opened or unlocked
        """
        return bool(int(self.send_command("SYST:DOOR?")))

    def cmd_system_status(self) -> str:
        """Queries the chamber for its status.

        The server answers with a string composed of three
        tokens for each available axis, where the feed switcher is considered as an axis, too.
        Hence, there are six tokens without the feed switcher installed, or nine tokens with the
        feed switcher installed:
        <Axis idenitifier>, <current position>, <status of the axis>,
        <Axis idenitifier>, <current position>, <status of the axis>,
        <Axis idenitifier>, <current position>, <status of the axis>
        If an axis is unavailable (not addressable, for example without power supply), then it is
        not listed.
        Axis identifier; see Chapter 4.2, "Coordinate Systems", on page 23
        AZI = the azimuth axis (rotation about phi)
        ELE = the elevation axis (rotation about theta)
        FESW = the feed switcher
        Current position:
        Degrees of rotation of the azimuth or elevation axis, respectively, from their 0 degrees
        position.
        The elevation's theta = 0 position is the horizontal orientation of the DUT holder.
        Positive elevation angles (theta > 0) are in counterclockwise rotation when seen
        from the front of the chamber. You can define an arbitrary azimuth angle of
        your DUT as the phi = 0 position. Positive azimuth angles (phi > 0) are in counterclockwise
        rotation when seen from the top (while theta = 0). The arrows in Figure
        4-8 point in positive angular directions.
        The controller treats the feed switcher as a (quasi) 3rd axis. To represent the
        current position of the feed switcher, the query returns the sequential number of
        the enabled feed antenna. The numbers of the feed antennas are 1 to 4 from
        left to right, when seen from the chamber's door.
        For example, if the "current position" = "2", the feed switcher has moved the
        2nd "antenna mover" to the center position and hence enabled the 2nd feed
        antenna.
        System Commands
        R&S ATS1800C Model 03 Remote Control Commands
        Instructions Handbook 1179.4757.02 ─ 01 86
        Typically, the feed antennas (listed in Table 7-1) are arranged as in Figure 7-12.
        To see the actual antenna arrangement, refer to the "Feedswitcher" section
        (Figure 7-10) in the "Positioner Control" dialog of the user interface.
        Status of the axis:
         0: Idle, not moving
         1: Moving
        -1: Error condition
        """
        return self.send_command("SYST:STAT?")

    def cmd_system_errors(self) -> str:
        """Queries the chamber for an error. The server answers with the current error IDs for.

        both axes, including axis identifiers.
        Error codes are "Beckhoff Error IDs". Refer to Table 10-1 and to the Beckhoff positioner
        documentation for the meaning of these codes.
        Additional error codes:
        "0" = no error
        "-997" = unknown argument or argument out of range
        "-998" = unknown command
        "-999" = execution error
        """
        return self.send_command("SYST:ERR?")

    def cmd_reset_tcp_ip_server(self) -> None:
        """Resets the TCP/IP server.

        Use this command, if the chamber has stopped responding
        to control commands, see Table 10-1.
        The execution of reset and startup typically takes up to 3 s. You get no feedback on
        sending this command.
        """
        self.send_command("SYST:TCP")

    def cmd_reset_browser_interface(self) -> None:
        """Resets the entire TCP/IP connection, including the browser-based user interface.

        Use this command, if the user interface is not loading.
        """
        self.send_command("SYST:WEB:RST")

    def cmd_set_position_target(self, axis: str, angle: float) -> None:
        """Sets the target position in degrees for the next movement.

        of the azimuth/elevation axis (turntable).
        To start the movement, use the command CONT:AZIM:STAR.
        The movement stops automatically, when the target position is reached, or you can
        stop the movement with the command CONT:AZIM:STOP.
        Parameters:
        <targetposition> The position can be any number of digits, including 0, with any
        resolution.
        """
        angle_ats: float = self.translate_angle_to_ats1800c_coordinates(axis, angle)
        motor: str = self.get_motor_from_axis(axis)
        self.send_command(f"CONT:{motor}:POS:TARG {angle_ats}")

    # TODO: Verify that this algo works.
    def seek_position(self, axis: str, angle: float) -> None:
        """Instructs the device to begin seeking for a specified target position.

        axis= 'Theta' or 'Phi'

        angle in degrees
        """
        axis_index: int = 0 if axis == "Theta" else 1

        if not self.check_angel_within_limits(axis, angle):
            raise ValueError("Invalid angle supplied.")
        else:
            t0 = time.time()
            self.cmd_set_position_target(axis, angle)
            self.cmd_axis_start(axis)

            if self.logger is not None:
                self.logger.info(f"Seeking: {axis}, Position: {angle} deg.")

            done: bool = False
            while not done:
                if (time.time() - t0) > self.max_travel_time:
                    if self.logger is not None:
                        self.logger.error("Positioner is stuck.")
                        raise PositionerError

                response: bool = self.cmd_get_axis_busy(axis)

                if response:
                    pass
                else:
                    position: Tuple[float, float] = self.get_current_position()
                    while (abs(position[axis_index] - angle) > self.position_accuracy_deg) and (
                        (time.time() - t0) < self.max_travel_time
                    ):
                        position = self.get_current_position()

                    return

    def azel_to_thetaphi(self, azimuth: float, elevation: float) -> Tuple[float, float]:
        """Az-El to Theta-Phi conversion.

        :param az: Azimuth angle, in radians
        :param el: Elevation angle, in radians
        :returns: Tuple of corresponding (theta, phi) angles, in radians
                    theta in range [0,pi]
                    phi in range [0,2*pi]
        """
        cos_theta: float = np.cos(elevation) * np.cos(azimuth)
        theta: float = np.arccos(cos_theta)

        # TODO: Refactor this abomination.
        phi: float = np.arctan2(np.tan(elevation), (np.sin((azimuth + 1 * (azimuth == 0))))) * (
            azimuth != 0
        ) + np.pi / 2 * (azimuth == 0) * np.sign(elevation)

        return theta, phi

    def thetaphi_to_azel(self, theta: float, phi: float) -> Tuple[float, float]:
        """Theta-Phi to Az-El conversion.

        :param theta: theta angle, in radians
        :param azimuth: phi angle, in radians
        :returns: Tuple of corresponding (azimuth, elevation) angles, in radians
                    theta in range [0,pi]
                    phi in range [0,2*pi]
        """
        sin_elevation: float = np.sin(phi) * np.sin(theta)
        elevation: float = np.arcsin(sin_elevation)
        azimuth: float = np.arctan2(np.cos(phi) * np.sin(theta), np.cos(theta))

        return azimuth, elevation
