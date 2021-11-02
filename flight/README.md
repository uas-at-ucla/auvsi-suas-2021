# Flight software


## Running the Simulator

Follow the PX4 install instructions on the Notion. Make sure you are on the Ubuntu virtual machine.

In whatever folder you have PX4 installed in, run
```
make px4_sitl gazebo
```
to start PX4 with Gazebo and GUI.

To run without a GUI,
```
make px4_sitl gazebo HEADLESS=1
```

## Virtual Environment

We use a virtual environment to keep track of the different libraries we use.

To create a virtual environment, run
```
python3 -m venv env
```

To activate,

```
source env/bin/activate
```

## Libraries

To install the required libraries, run
```
pip install -r requirements.txt
```

## Running 

```
python3 main.py
```

Run examples
```
python3 examples/takeoff_and_land.py
```