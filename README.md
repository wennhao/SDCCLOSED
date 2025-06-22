# SDCCLOSED

## Get Started
This project requires Python installed

[OpenCV](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)


## How to run the project for TESTING locally using venv
> [!IMPORTANT]
> This project requires python 3.12 installed
> Open up your **terminal** and run the following commands

```
pip install --upgrade pip
```

```
pip install --upgrade pip setuptools wheel
```


Create a new virtual environment
```
python3.12 -m venv .venv
```
```
Set-ExecutionPolicy Unrestricted -Scope Process
```
On Windows
 ```
.venv\Scripts\activate
```

Mac / Linux users
```
source .venv/bin/activate
```

download the needed libraries
```
pip install -r requirements.txt
```

Now you are ready to test the code
To test the kart brain with a video, first navigate to the right folder
```
cd kart     (depending on your current folder)
```

Run the main controller code with a video:
```
python main.py <video_path>
```
for example
```
python main.py videos\output_video.mp4
```
(or 'python3' instead of 'python'. this depends on what you have installed)

Or run the main controller code with a camera:
```
python main.py true
```
(Adding the argument 'true' will make the code use the standard camera configuration for the kart instead of a video.
If you want to test with your own camera which is not on the kart, change the camera config in kart/configs/kart1.json)

Success! The dashboard is now running on [localhost]([localhost:](http://127.0.0.1:7890/))

#### When you're done
```
deactivate
```

## Important tips!
To view all ports run 
```
python3 -m serial.tools.list_ports
```
List all available camera's
```
ls /dev/video*
```

LiDAR requires you to install rplidar-roboticia
if you installed rplidar, please uninstall as it would break the LiDAR sensor

## Running on the kart
When running on the NUC on the kart, you will not need to activate a venv like you would when testing locally

1. Setup Tailscale between your device and the kart. (This can only be done on one laptop at a time)
2. Copy the IP address of the NUC given to you by Tailscale.
3. Connect to this IP address using ssh in VSCode.
4. Enter the password which you use to enter the NUC.
6. pull this SDCCLOSED folder from GitHub.
5. Locate the folder.
6. Run the command: 'python3 main.py true'
The kart should now be functioning as the final product of SDC 2025

> [!IMPORTANT]
> Make sure your code is tested thoroughly!
> Add a way to stop the kart with a button.


## Credits

[Peter](https://github.com/Draqy)  
[Jordy](https://github.com/PoleLord)  
[Wen](https://github.com/wennhao)  
[Long](https://github.com/dimsumtime)