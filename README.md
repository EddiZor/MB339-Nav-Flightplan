# MB339-Nav-Flightplan

An open-source Python utility designed for Microsoft Flight Simulator to read flight plans directly from SimBrief and automatically navigate the IndiaFoxtEcho Aermacchi MB-339 via SimConnect by controlling the autopilot heading in real-time.

## Features
* **SimBrief Integration:** Automatically fetches and parses the latest operational flight plan (OFP) using your SimBrief Pilot ID.
* **SimConnect Bridge:** Interacts directly with MSFS in real-time to monitor aircraft position and manage autopilot states.
* **Heading Hold Navigation:** Automatically calculates the bearing to active waypoints and steers the aircraft sequentially along the route.

## Prerequisites
* Microsoft Flight Simulator (MSFS)
* IndiaFoxtEcho MB-339
* Python 3.9+

## Installation & Setup

1. Clone or download this repository into your local workspace.
2. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt

   Open main.py and ensure your SimBrief Pilot ID is correctly configured.