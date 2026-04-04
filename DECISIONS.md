# Architectural Decisions

This file documents key technical decisions and explanations made throughout the project.

---

## What is a Kalman Filter?
*Author: David Gleason*

A Kalman filter is a  mathematical algorithm that estimates the position and velocity of a moving object when direct measurements are noisy or incomplete. It works in two steps: first it predicts where the object will be next based on its current state and a motion model, then it corrects that prediction when a new measurement arrives by blending the prediction and the measurement according to how much it trusts each one. The more uncertain the prediction, the more weight it gives the new measurement, and vice versa. In the context of vehicle tracking, the Kalman filter allows DeepSORT to maintain a smooth estimated trajectory for each vehicle even when the detector misses it for a few frames keeping the same vehicle ID alive rather than losing track and starting over.
---

## What is mAP, Precision, and Recall?
*Author: Dylan de Verteuil*

<!-- Dylan fills this in during Week 2 -->

---
