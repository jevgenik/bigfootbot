# Project Folder Structure

## docker/
In this folder, you can find the Dockerfiles for the different components of the robot.

### camera_d435i/
This folder contains the Dockerfiles for the camera component (Intel RealSense D435i).

- [Dockerfile.bfb_camera_d435i](https://github.com/jevgenik/bigfootbot/blob/master/docker/camera_d435i/Dockerfile.bfb_camera_d435i)
- [docker-compose_camera_d435i.yml](https://github.com/jevgenik/bigfootbot/blob/master/docker/camera_d435i/docker-compose_camera_d435i.yml)

To start the camera component, run the following command:
```bash
docker-compose -f docker-compose_camera_d435i.yml up
```