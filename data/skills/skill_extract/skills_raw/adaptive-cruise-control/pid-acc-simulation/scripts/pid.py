#!/usr/bin/env python3
"""Generic PID controller with anti-windup and output clamping.

Usage:
  from scripts.pid import PIDController
  pid = PIDController(kp=1.0, ki=0.1, kd=0.2, output_min=-8.0, output_max=3.0, integral_limit=100.0)
  u = pid.compute(error, dt)
  pid.reset()  # on mode changes

Notes:
- Anti-windup: conditional integration + optional integral clamp.
- Derivative: based on error difference; first call derivative=0.
- If output limits are set, the returned control signal is clamped.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class PIDController:
    kp: float
    ki: float
    kd: float
    output_min: Optional[float] = None
    output_max: Optional[float] = None
    integral_limit: Optional[float] = None  # absolute limit for integral term (pre-scale)

    # Internal state
    _integral: float = 0.0
    _prev_error: float = 0.0
    _first: bool = True

    def reset(self) -> None:
        self._integral = 0.0
        self._prev_error = 0.0
        self._first = True

    def compute(self, error: float, dt: float, enable_integration: bool = True) -> float:
        if dt <= 0:
            # Degenerate dt: proportional only
            p = self.kp * error
            return self._clamp(p)

        # Proportional
        p = self.kp * error

        # Derivative
        if self._first:
            d = 0.0
            self._first = False
        else:
            d = self.kd * (error - self._prev_error) / dt

        # Integral with conditional accumulation
        if enable_integration and self.ki != 0.0:
            self._integral += error * dt
            if self.integral_limit is not None:
                if self._integral > self.integral_limit:
                    self._integral = self.integral_limit
                elif self._integral < -self.integral_limit:
                    self._integral = -self.integral_limit
            i = self.ki * self._integral
        else:
            i = self.ki * self._integral  # hold integral if disabled

        u = p + i + d
        u_clamped = self._clamp(u)

        # Simple back-calculation: if saturated and integration is on, undo the latest integral increment
        if enable_integration and u_clamped != u and self.ki != 0.0:
            # remove the last integral addition to prevent windup
            self._integral -= error * dt

        self._prev_error = error
        return u_clamped

    def _clamp(self, val: float) -> float:
        if self.output_min is not None and val < self.output_min:
            return self.output_min
        if self.output_max is not None and val > self.output_max:
            return self.output_max
        return val
