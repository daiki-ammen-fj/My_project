"""Driver for ETS 2035 Maps Positioner."""

from logging import Logger
import time
from typing import cast, Optional, Tuple

import numpy as np
import pyvisa
from pyvisa.resources import TCPIPSocket

from instrument_lib.instruments.instrument import SCPIInstrument
from instrument_lib.utils import InstrumentIdentificationInfo, PositionerError


def retry_on_failure(func):  # noqa
    def wrapper(self, *args, **kwargs):  # noqa
        failures = 0
        while failures <= self.retry:
            try:
                return func(self, *args, **kwargs)
            except Exception:
                failures = failures + 1

    return wrapper


class ETS_Positioner(SCPIInstrument):
    """ETS Positioner Driver."""

    ACCEPTED_MODELS = [
        "Precision MAPS 2305-001",
    ]

    def __init__(
        self,
        ip_address: str = "192.168.0.100",
        logger: Optional[Logger] = None,
        retry: int = 10,
        theta_min: float = 0,
        theta_max: float = 180,
        phi_min: float = -180,
        phi_max: float = 180,
        max_travel_time: float = 150,
    ):
        """Constructor.

        :param ip_address: IP Address of positioner.
        :param logger: Logger object.
        :param port: Port to connect to.
        :param retry: Number of times to retry certain commands.
        :param theta_min: Minimum theta value.
        :param theta_max: Maximum theta value.
        :param phi_min: Minimum phi value.
        :param phi_max: Maximum phi value.
        :param max_travel_time: Maximum time that the positioner can spend moving.
        """
        self.logger: Optional[Logger] = logger
        self.ip_address = ip_address
        self.visa_connect_string = f"TCPIP0::{self.ip_address}::1206::SOCKET"
        self.retry: int = retry
        self.theta_min: float = (
            theta_min if 0 <= theta_min <= 180 else 0
        )  # TODO: Why do this and not raise ValueError
        self.theta_max: float = (
            theta_max if 0 <= theta_min <= 180 else 180
        )  # TODO: Why do this and not raise ValueError
        self.phi_min: float = phi_min
        self.phi_max: float = phi_max
        self.max_travel_time: float = max_travel_time
        self.rsinstrument = False

        super().__init__(None, None, None, False, False)

    def connect(self) -> None:
        """Overrided constructor."""
        resource_manager = pyvisa.ResourceManager()
        try:
            self.instrument = cast(
                TCPIPSocket, resource_manager.open_resource(self.visa_connect_string)
            )
            self.instrument.read_termination = "\n"  # type: ignore
            self.instrument.timeout = 5000
            self.connected = True
            self.identify()
        except pyvisa.VisaIOError as e:
            self.connected = False
            self.logger.error(  # type: ignore
                (
                    f"Failed to connect to ETS Positioner due to: {repr(e)}, "
                    f"{resource_manager.last_status}, {resource_manager.visalib.last_status}"
                )
            )
            self.connected = False

    def reset(self) -> None:
        """Overrided reset function."""
        super().reset()
        self.move_to_azimuth_elevation(0, 0)

    def get_motor_from_axis(self, axis: str) -> str:
        """Determines motor based on axis."""
        return "AXIS1" if axis == "Theta" else "AXIS2"

    @retry_on_failure
    def move_to_degrees(self, id_: int, angle: float) -> None:
        """Moves position to angle."""
        self.seek_position(id_, angle)

    @retry_on_failure
    def move_to_azimuth_elevation(self, azimuth_deg: float, elevation_deg: float) -> tuple:
        """Move the positioner to a specified angle defined in Azimuth-Elevation coordinate system.

        :param azimuth_deg: Angle in degrees azimuth to reposition.
        :param elevation_deg: Angle in degrees elevation to reposition.
        """
        theta_rad: float = 0
        phi_rad: float = 0
        theta_rad, phi_rad = self.azel_to_thetaphi(
            azimuth_deg * np.pi / 180, elevation_deg * np.pi / 180
        )

        theta_deg: float = theta_rad * 180 / np.pi
        phi_deg: float = phi_rad * 180 / np.pi

        if not (self.theta_min <= theta_deg <= self.theta_max):
            raise ValueError(f"Theta must be between {self.theta_max} and {self.theta_min}")

        if not (self.phi_min <= phi_deg <= self.phi_max):
            raise ValueError(f"Phi must be between {self.phi_max} and {self.phi_min}")

        self.seek_position("Theta", theta_deg)
        self.seek_position("Phi", phi_deg)
        return azimuth_deg, elevation_deg

    @retry_on_failure
    def move_to_theta_phi(self, theta_deg: float, phi_deg: float) -> tuple:
        """Move the positioner to a certain angle defined in Theta-Phi coordinate system.

        :param theta_deg: Angle in degrees azimuth to reposition.
        :param phi_deg: Angle in degrees elevation to reposition.
        """
        if (theta_deg < self.theta_min) or (theta_deg > self.theta_max):
            raise ValueError(f"Theta must be between {self.theta_max} and {self.theta_min}")

        if (phi_deg < self.phi_min) or (phi_deg > self.phi_max):
            raise ValueError(f"Phi must be between {self.phi_max} and {self.phi_min}")

        self.seek_position("Theta", theta_deg)
        self.seek_position("Phi", phi_deg)
        return theta_deg, phi_deg

    def which_axis(self, axis: str) -> str:
        """Calls get motor from axis."""
        return self.get_motor_from_axis(axis)

    def get_current_position_axis(self, axis: str) -> float:
        """Return the current position along a single axis."""
        if axis == "Theta":
            return self.get_current_position_theta()
        elif axis == "Phi":
            return self.get_current_position_phi()
        else:
            raise ValueError("Invalid axis provided.")

    def get_current_position(self) -> Tuple[float, float]:
        """Return the current position in Theta-Phi coordinate system."""
        return self.get_current_position_theta_phi()

    def get_current_position_theta_phi(self) -> Tuple[float, float]:
        """Return the current position in Theta-Phi coordinate system."""
        theta_deg: float = self.get_current_position_theta()
        phi_deg: float = self.get_current_position_phi()

        return theta_deg, phi_deg

    def get_current_position_azimuth_elevation(self) -> Tuple[float, float]:
        """Return the current position in Azimuth-Elevation coordinate system."""
        theta_deg: float = 0
        phi_deg: float = 0
        theta_deg, phi_deg = self.get_current_position_theta_phi()

        azimuth_rad: float = 0
        elevation_rad: float = 0
        azimuth_rad, elevation_rad = self.thetaphi_to_azel(
            theta_deg * np.pi / 180, phi_deg * np.pi / 180
        )
        return azimuth_rad * 180 / np.pi, elevation_rad * 180 / np.pi

    def get_current_position_theta(self) -> float:
        """Return the current Theta position (ie Elevation positione)."""
        return self.cmd_get_axis_position("Theta")

    def get_current_position_phi(self) -> float:
        """Return the current Phi position (ie Azimuth positioner)."""
        return self.cmd_get_axis_position("Phi")

    @retry_on_failure
    def get_positioner_id(self) -> str:
        """Queries the ID of the device. Returns string identifying the device.

        Can include company, positioner type, or IP address.
        """
        return self.cmd_get_device_id()

    @retry_on_failure
    def get_positioner_ip(self) -> str:
        """Queries the ID of the device. Returns string identifying the device.

        Can include company, positioner type, or IP address.
        """
        return self.cmd_get_device_ip_address()

    @retry_on_failure
    def move_to_home(self) -> None:
        """Every time the positioner is turned on, a home procedure must be performed.

        so the current position is known by the firmware.
        """
        t0 = time.time()
        self.cmd_home()
        done = False
        while not done:
            if (time.time() - t0) > self.max_travel_time:
                raise PositionerError
        complete: bool = self.cmd_get_operation_complete()
        if complete:
            return
        else:
            pass

    def check_angle_within_limits(self, axis: str, angle: float) -> bool:
        """Checks that the angle is within the limits set.

        during the creation of the positioner object.
        """
        if axis == "Theta":
            return self.theta_min <= angle <= self.theta_max
        elif axis == "Phi":
            return self.phi_min <= angle <= self.phi_max
        else:
            raise ValueError("Invalid axis provided.")

    @retry_on_failure
    def seek_position(self, axis: str, angle: float) -> None:
        """Instructs the device to begin seeking for a specified target position.

        In continuous rotation mode, the device will seek the target value
        by the shortest possible path.
        Thus, a seek from 350.00 to 10.00 will rotate clockwise, not counterclockwise.
        If the target is not located between the current upper/clockwise and
        lower/counterclockwise limits, motion will continue in the target direction
        until a limit is hit.
        """
        if self.check_angle_within_limits(axis, angle):
            t0: float = time.time()
            self.cmd_seek_position(axis, angle)

            done: bool = False
            while not done:
                if (time.time() - t0) > self.max_travel_time:
                    raise PositionerError

                response = self.cmd_get_motion_direction(axis)
                while (response != "0") and (time.time() - t0) < self.max_travel_time:
                    response = self.cmd_get_motion_direction(axis)

                if response == "0":
                    return
                else:
                    pass
        else:
            raise ValueError

    @retry_on_failure
    def seek_negative_position(self, axis: str, angle: float) -> None:
        """Instructs the device to begin seeking the specified.

        target value in the negative (counterclockwise) direction only.
        This command is provided primarily to support continuous rotation mode
        to force the seek of a position
        from a particular direction.
        Thus, a SKN from 180.33 to 181.02 will rotate counterclockwise to reach the target value.
        In non-continuous rotation mode, if the target is clockwise from the current position,
        then no motion occurs.
        The target must be located between the current clockwise and counterclockwise limits.
        """
        if self.check_angle_within_limits(axis, angle):
            t0: float = time.time()
            self.cmd_seek_negative_position(axis, angle)

            done: bool = False
            while not done:
                if (time.time() - t0) > self.max_travel_time:
                    raise PositionerError

                response = self.cmd_get_motion_direction(axis)
                while (response != "0") and (time.time() - t0) < self.max_travel_time:
                    response = self.cmd_get_motion_direction(axis)

                if response == "0":
                    return
                else:
                    pass
        else:
            raise ValueError

    @retry_on_failure
    def seek_positive_position(self, axis: str, angle: float) -> None:
        """Instructs the device to begin seeking the specified target value in the.

        positive (clockwise) direction only.
        This command is provided primarily to support continuous rotation
        mode to force the seek of a position from a particular direction.
        Thus, a SKP from 181.99 to 180.02 will rotate clockwise to reach the target value.
        In non-continuous rotation mode, if the target is counterclockwise from the current
        position, then no motion occurs.
        The target must be located between the current clockwise and counterclockwise limits.
        """
        if self.check_angle_within_limits(axis, angle):
            t0: float = time.time()
            self.cmd_seek_positive_position(axis, angle)

            done: bool = False
            while not done:
                if (time.time() - t0) > self.max_travel_time:
                    raise PositionerError

                response = self.cmd_get_motion_direction(axis)
                while (response != "0") and (time.time() - t0) < self.max_travel_time:
                    response = self.cmd_get_motion_direction(axis)

                if response == "0":
                    return
                else:
                    pass
        else:
            raise ValueError

    @retry_on_failure
    def stop(self) -> None:
        """Stops the positioner."""
        t0: float = time.time()
        done: bool = False
        self.cmd_stop()
        while not done:
            if (time.time() - t0) > 2:
                raise PositionerError
            response = self.cmd_get_operation_complete()
            if response == "1":
                return

    @retry_on_failure
    def cmd_seek_position(self, axis: str, angle: float) -> None:
        """Move the positioner motor "axis" to position "angle"."""
        motor: str = self.get_motor_from_axis(axis)
        self._write(f"{motor}:SK  {angle}")

    @retry_on_failure
    def cmd_seek_positive_position(self, axis: str, angle: float) -> None:
        """Move the positioner motor "axis" to position "angle"."""
        motor: str = self.get_motor_from_axis(axis)
        self._write(f"{motor}:SKP {angle}")

    @retry_on_failure
    def cmd_seek_negative_position(self, axis: str, angle: float) -> None:
        """Move the positioner motor "axis" to position "angle"."""
        motor: str = self.get_motor_from_axis(axis)
        self._write(f"{motor}:SKN {angle}")

    @retry_on_failure
    def cmd_stop(self) -> None:
        """Stops the positioner."""
        self._write("ST")

    @retry_on_failure
    def cmd_home(self, axis: str) -> None:
        """Send the positioner home."""
        motor: str = self.get_motor_from_axis(axis)
        self._write(f"{motor}:HOME")

    @retry_on_failure
    def cmd_get_is_home(self, axis: str) -> bool:
        """Returns whether the device is in the home position."""
        motor: str = self.get_motor_from_axis(axis)
        result: str = self._query(f"{motor}:HOME?")
        if result == "0":
            return False
        elif result == "1":
            return True
        else:
            raise ValueError()

    @retry_on_failure
    def cmd_reset_axis(self, axis: str) -> None:
        """Reset the axis."""
        motor: str = self.get_motor_from_axis(axis)
        self._write(f"{motor}:RESET")

    @retry_on_failure
    def cmd_set_axis_speed(self, axis: str, speed: float) -> None:
        """Changes the device speed setting (Speed between 1 and 8)."""
        speed = 1 + int(speed / 20)
        if 1 <= speed <= 8:
            motor: str = self.get_motor_from_axis(axis)
            self._write(f"{motor}:S{speed}")

    @retry_on_failure
    def cmd_get_axis_speed(self, axis: str) -> float:
        """Returns a value between 1 and 8 indicating the currently selected speed setting."""
        motor: str = self.get_motor_from_axis(axis)
        return float(self._query(f"{motor}:S?"))

    @retry_on_failure
    def cmd_set_speed_preset(self, axis: str, speed: float, percentage: float) -> None:
        """Changes the preset speed setting (Speed between 1 and 8).

        to a certain percentage of the maximum speed.
        """
        if 1 <= speed <= 8:
            motor: str = self.get_motor_from_axis(axis)
            self._write(f"{motor}:S {speed} {percentage}")

    @retry_on_failure
    def cmd_get_speed_preset(self, axis: str, speed: float) -> float:
        """Returns a value between 1 and 8 indicating the currently selected speed setting."""
        if 1 <= speed <= 8:
            motor: str = self.get_motor_from_axis(axis)
            return float(self._query(f"{motor}:SS{speed}?"))
        else:
            raise ValueError()

    @retry_on_failure
    def cmd_get_device_id(self) -> str:
        """Queries the ID of the device.

        Returns string identifying the device. Can include company, positioner type, or IP address.
        """
        return self._query("*IDN?")

    @retry_on_failure
    def cmd_get_device_ip_address(self) -> str:
        """Queries the ID of the device.

        Returns string identifying the device. Can include company, positioner type, or IP address.
        """
        return self._query("MOD:IPAD?")

    @retry_on_failure
    def cmd_clear_error(self) -> None:
        """Clears all errors."""
        self._write("*CLS")

    @retry_on_failure
    def cmd_get_operation_complete(self) -> str:
        """Queries if the last operation is complete."""
        return self._query("*OPC?")

    @retry_on_failure
    def cmd_set_axis_acceleration(self, axis: str, acceleration: float) -> None:
        """Sets the acceleration (in milliseconds) for the device to reach max speed.

        For high inertial loads, a longer acceleration time might be required.
        """
        motor: str = self.get_motor_from_axis(axis)
        if 100 <= acceleration <= 30000:
            self._write(f"{motor}:A {acceleration}")
        else:
            raise ValueError()

    @retry_on_failure
    def cmd_get_axis_acceleration(self, axis: str) -> float:
        """Returns the time in milliseconds for the positioner to reach max speed."""
        motor: str = self.get_motor_from_axis(axis)
        return float(self._query(f"{motor}:A?"))

    @retry_on_failure
    def cmd_move_counter_clockwise(self, axis: str) -> None:
        """Instructs the turntable to move in the counterclockwise direction.

        Stops at counterclockwise limit.
        """
        motor: str = self.get_motor_from_axis(axis)
        self._write(f"{motor}:CC")

    @retry_on_failure
    def cmd_move_clockwise(self, axis: str) -> None:
        """Instructs the turntable to move in the clockwise direction. Stops at clockwise limit."""
        motor: str = self.get_motor_from_axis(axis)
        self._write(f"{motor}:CW")

    @retry_on_failure
    def cmd_set_counter_clockwise_limit(self, axis: str, angle: float) -> None:
        """Sets the Counter clockwise limit of the device.

        The specified value xxx.xx is in degrees between -999.99 and 999.99,
        and must be less than the upper limit.
        """
        motor: str = self.get_motor_from_axis(axis)
        self._write(f"{motor}:CL {angle}")

    @retry_on_failure
    def cmd_get_counter_clockwise_limit(self, axis: str) -> float:  # type: ignore
        """Returns Counter Clockwise Limit value in degrees in XXX.XX format."""
        motor: str = self.get_motor_from_axis(axis)
        return float(self._query(f"{motor}:CL?"))

    @retry_on_failure
    def cmd_set_clockwise_limit(self, axis: str, angle: float) -> None:
        """Sets the Clockwise limit of the device.

        The specified value xxx.xx is in degrees between -999.99 and 999.99,
        and must be less than the upper limit
        """
        motor: str = self.get_motor_from_axis(axis)
        self._write(f"{motor}:WL {axis}")

    @retry_on_failure
    def cmd_get_clockwise_limit(self, axis: str) -> str:
        """Returns Counter Clockwise Limit value in degrees in XXX.XX format."""
        motor: str = self.get_motor_from_axis(axis)
        return self._query(f"{motor}:WL?")

    @retry_on_failure
    def cmd_set_current_position(self, axis: str, angle: float) -> None:
        """Sets the current position to the specified value in degrees."""
        motor: str = self.get_motor_from_axis(axis)
        self._write(f"{motor}:CP {angle}")

    @retry_on_failure
    def cmd_get_axis_position(self, axis: str) -> float:
        """Returns the current position of the turntable in degrees."""
        motor: str = self.get_motor_from_axis(axis)
        return float(self._query(f"{motor}:CP?"))

    @retry_on_failure
    def cmd_set_continuous_rotation_mode(self, axis: str) -> None:
        """Sets the positioner into continuous rotation mode.

        In the continuous mode of operation, the positioner is allowed infinite movement.
        The device travels from 0 â€“ 359.9 and the limits are ignored.
        In addition, while in continuous rotation mode the device will
        seek the target value by the shortest possible path.
        Thus, a seek from 350.22 to 10.10 will rotate clockwise, not counterclockwise.
        """
        motor: str = self.get_motor_from_axis(axis)
        self._write(f"{motor}:CR")

    @retry_on_failure
    def cmd_set_noncontinuous_rotation_mode(self, axis: str) -> None:
        """Changes the positioner into non-continuous rotation mode.

        In the non-continuous mode,
        the positioner motion is restricted between upper & lower limits.
        Thus, a seek from 350.0 to 10.05 will rotate Counterclockwises.
        """
        motor: str = self.get_motor_from_axis(axis)
        self._write(f"{motor}:NCR")

    @retry_on_failure
    def cmd_get_is_continuous_rotation_mode(self, axis: str) -> str:
        """Returns the continuous rotation mode. 1 = continuous rotation,  0 = not continuous."""
        motor: str = self.get_motor_from_axis(axis)
        return self._query(f"{motor}:CR?")

    @retry_on_failure
    def cmd_get_motion_direction(self, axis: str) -> str:
        """Returns the motion direction for the device.

        +1 = Device is moving clockwise
         0 = Device is stopped
        -1 = Device is moving counterclockwise
        """
        motor: str = self.get_motor_from_axis(axis)
        return self._query(f"{motor}:DIR?")

    @retry_on_failure
    def cmd_get_error_code(self) -> str:
        """Returns the last error encountered during the execution of a command.

        or an empty string if there is no error.
        """
        return self._query("ERROR?")

    def azel_to_thetaphi(self, azimuth: float, elevation: float) -> Tuple[float, float]:
        """Azimuth-elevation to theta-phi conversion.

        :param azimuth: azimuth angle, in radians
        :param elevation: elevation angle, in radians
        :returns: Tuple of (theta, phi) angles in radians
        """
        cos_theta: float = np.cos(elevation) * np.cos(azimuth)
        theta: float = np.arccos(cos_theta)

        phi: float = np.arctan2(np.tan(elevation), (np.sin((azimuth + 1 * (azimuth == 0))))) * (
            azimuth != 0
        ) + np.pi / 2 * (azimuth == 0) * np.sign(elevation)

        return theta, phi

    def thetaphi_to_azel(self, theta: float, phi: float) -> Tuple[float, float]:
        """Theta-phi to azimuth-elevation conversion.

        :param theta: theta angle, in radians
        :param phi: phi angle, in radians
        :returns: Tuple of (azimuth, elevation) angles in radians
        """
        sin_elevation: float = np.sin(phi) * np.sin(theta)
        elevation: float = np.arcsin(sin_elevation)
        azimuth: float = np.arctan2(np.cos(phi) * np.sin(theta), np.cos(theta))

        return azimuth, elevation

    @retry_on_failure
    def cmd_get_axis_trigger_enable(self, axis: str) -> str:
        """CONT:ELEV:TRIG:STAT.

        Queries the generation of a hardware trigger event at every given number
        of degrees of elevation-axis movement. The number of degrees is specified by the
        command CONT:ELEV:TRIG:STEP.
        Equivalent with "Trigger 1" in the user interface.
        The query command checks, if the trigger is enabled.
        Activating the elevation trigger deactivates the azimuth trigger.
        """
        motor = self.get_motor_from_axis(axis)
        return self._query("CONT:%s:TRIG:STAT?" % motor)

    @retry_on_failure
    def cmd_set_axis_trigger_enable(self, axis: str, flag: bool) -> None:
        """CONT:ELEV:TRIG:STAT <status>.

        Enables or disables the generation of a hardware trigger event at every given number
        of degrees of elevation-axis movement. The number of degrees is specified by the
        command CONT:ELEV:TRIG:STEP.
        Equivalent with "Trigger 1" in the user interface.
        The query command checks, if the trigger is enabled.
        Activating the elevation trigger deactivates the azimuth trigger.
        """
        flag_val: int = 1 if flag else 0
        motor = self.get_motor_from_axis(axis)
        self._write("CONT:%s:TRIG:STAT %d" % (motor, flag_val))

    @retry_on_failure
    def cmd_get_axis_trigger(self, axis: str) -> float:
        """CONT:ELEV:TRIG:STEP.

        Configures the elevation axis to generate a trigger event every given number of
        degrees, if enabled by the command CONT:ELEV:TRIG:STAT.
        The range of step sizes depends on several parameters, for example azimuth speed
        and measurement instrument speed. We recommend a minimum step size of 3Â° for
        20Â°/s azimuth speed and 5Â° for 50Â°/s azimuth speed.
        The query command returns the step size.
        """
        motor = self.get_motor_from_axis(axis)
        return float(self._query("CONT:%s:TRIG:STEP?" % motor))

    @retry_on_failure
    def cmd_set_axis_trigger(self, axis: str, step_size: float) -> None:
        """CONT:ELEV:TRIG:STEP <step>.

        Configures the elevation axis to generate a trigger event every given number of
        degrees, if enabled by the command CONT:ELEV:TRIG:STAT.
        The range of step sizes depends on several parameters, for example azimuth speed
        and measurement instrument speed. We recommend a minimum step size of 3Â° for
        20Â°/s azimuth speed and 5Â° for 50Â°/s azimuth speed.
        The query command returns the step size.
        """
        motor = self.get_motor_from_axis(axis)
        self._write("CONT:%s:TRIG:STEP %f" % (motor, step_size))


def transform_ptheta_pphi_to_px_py(
    phi_pos_deg: float,
    ptheta_mag_db: float,
    ptheta_pha_deg: float,
    pphi_mag_db: float,
    pphi_pha_deg: float,
    omt: bool,
) -> Tuple[float, float, float, float]:
    """Conversion between the axis of the fixed horn and the X- and Y- axis of the AUT.

    This implements the Ludwig III cross-pol definition.
    :param phi_pos_deg: Angle of Phi positioner in degrees
    :param ptheta_mag_dB: Magnitude of the power (or S21 parameter)
                        received in the horizontal port of the horn, in dB (or dBm)
                        [Theta-vector = Horn horizontal direction]
    :param ptheta_pha_deg: Phase of the power (or S21 parameter)
                        received in the horizontal port of the horn, in degrees
    :param pphi_mag_dB: Magnitude of the power (or S21 parameter) received in the vertical
                        port of the horn, in dB (or dBm)
                        [Phi-vector = Horn vertical direction]
    :param pphi_pha_deg: Phase of the power (or S21 parameter)
                        received in the vertical port of the horn, in degrees
    :param OMT: True if an OMT has been used in the receive horn
                (ie both ports are 90deg out of phase) and False if not (ie both ports in phase)
    :returns: 4-tuple of:
        px_mag_dB - Magnitude of the power (or S21 parameter)
                    of the horizontally-polarized signal (horizontal wrt AUT) in dBm (or dB)
        px_pha_deg - Phase of the power (or S21 parameter)
                    of the horizontally-polarized signal (horizontal wrt AUT), in degrees
        py_mag_dB - Magnitude of the power (or S21 parameter)
                    of the vertically-polarized signal (vertical wrt AUT)  in dBm (or dB)
        py_pha_deg - Phase of the power (or S21 parameter)
                    of the vertically-polarized signal (vertical wrt AUT), in degrees
    """
    phi: float = phi_pos_deg * np.pi / 180

    etheta_mag = 10 ** (ptheta_mag_db / 20)
    etheta_pha = ptheta_pha_deg * np.pi / 180
    ephi_mag = 10 ** (pphi_mag_db / 20)
    if omt:
        # OMT introduces an additional 90deg shift between both received polarizations
        ephi_pha = (pphi_pha_deg + 90) * np.pi / 180
    else:
        ephi_pha = (pphi_pha_deg) * np.pi / 180

    re_ex: float = np.cos(phi) * etheta_mag * np.cos(etheta_pha) - np.sin(phi) * ephi_mag * np.cos(
        ephi_pha
    )
    im_ex: float = np.cos(phi) * etheta_mag * np.sin(etheta_pha) - np.sin(phi) * ephi_mag * np.sin(
        ephi_pha
    )

    re_ey: float = np.sin(phi) * etheta_mag * np.cos(etheta_pha) + np.cos(phi) * ephi_mag * np.cos(
        ephi_pha
    )
    im_ey: float = np.sin(phi) * etheta_mag * np.sin(etheta_pha) + np.cos(phi) * ephi_mag * np.sin(
        ephi_pha
    )

    px_mag: float = re_ex**2 + im_ex**2
    py_mag: float = re_ey**2 + im_ey**2

    px_mag_db: float = 10 * np.log10(px_mag)
    py_mag_db: float = 10 * np.log10(py_mag)

    px_pha: float = np.arctan2(im_ex, re_ex)
    py_pha: float = np.arctan2(im_ey, re_ey)

    px_pha_deg: float = px_pha * 180 / np.pi
    py_pha_deg: float = py_pha * 180 / np.pi

    return px_mag_db, px_pha_deg, py_mag_db, py_pha_deg


def transform_ptheta_pphi_to_px_py_no_phase(
    phi_pos_deg: float, ptheta_mag_db: float, pphi_mag_db: float
) -> Tuple[float, float]:
    """Conversion between the axis of the fixed horn and the.

    X- and Y- axis of the AUT without using the received Phase.
    This implements the Ludwig III cross-pol definition.
    :param phi_pos_deg: Angle of Phi positioner in degrees
    :param ptheta_mag_db: Magnitude of the power (or S21 parameter)
                        received in the horizontal port of the horn, in dB (or dBm)
                        [Theta-vector = Horn horizontal direction]
    :param pphi_mag_db: Magnitude of the power (or S21 parameter)
                        received in the vertical port of the horn, in dB (or dBm)
                        [Phi-vector = Horn vertical direction]
    :returns: Tuple of:
        px_mag_db - Magnitude of the power (or S21 parameter)
                    of the horizontally-polarized signal (horizontal wrt AUT) in dBm (or dB)
        py_mag_db - Magnitude of the power (or S21 parameter)
                    of the vertically-polarized signal (vertical wrt AUT)  in dBm (or dB)
    """
    phi: float = phi_pos_deg * np.pi / 180

    etheta_mag: float = 10 ** (ptheta_mag_db / 20)
    ephi_mag: float = 10 ** (pphi_mag_db / 20)

    if ((phi_pos_deg > 0) * (phi_pos_deg <= 90)) + ((phi_pos_deg > -180) * (phi_pos_deg <= -90)):
        re_ex = np.cos(phi) * etheta_mag + np.sin(phi) * ephi_mag
        re_ey = np.sin(phi) * etheta_mag - np.cos(phi) * ephi_mag
    else:
        re_ex = np.cos(phi) * etheta_mag - np.sin(phi) * ephi_mag
        re_ey = np.sin(phi) * etheta_mag + np.cos(phi) * ephi_mag

    px_mag = re_ex**2
    py_mag = re_ey**2

    px_mag_db: float = 10 * np.log10(px_mag)
    py_mag_db: float = 10 * np.log10(py_mag)

    return px_mag_db, py_mag_db


def total_power(ptheta_mag_db: float, pphi_mag_db: float) -> float:
    """Computes the total power received by the horn (including co-pol and cross-pol).

    :param ptheta_mag_dB (float): Magnitude of the power (or S21 parameter)
                                received in the horizontal port of the horn, in dB (or dBm)
                                [Theta-vector = Horn horizontal direction]
    :param pphi_mag_dB (float): Magnitude of the power (or S21 parameter)
                                received in the vertical port of the horn, in dB (or dBm)
                                [Phi-vector = Horn vertical direction]
    :returns: total power received by the horn (including co-pol and cross-pol) in dBm
    """
    return 10 * np.log10(10 ** (ptheta_mag_db / 10) + 10 ** (pphi_mag_db / 10))
