# Getting Started with 2i2c Hub and NASA EarthData credentials

## Logging into the 2i2c Hub
Follow [this link](https://showcase.2i2c.cloud/hub/login) to log into the 2i2c hub.

## Creating EarthData credentials

NASA's Earth Science Data Systems program oversees the life cycle of NASA’s Earth science data from all of its Earth Observation missions — from acquisition through processing and distribution. 

For our purposes, the NASA Earthdata website is the starting point for full and open access to NASA's Earth science data collections, which is provided free of cost towards accelerating scientific advancement for societal benefit. To access data through this portal, users are required to first set up log in credentials.

A good tutorial for creating EarthData credentials is provided at [this link](https://urs.earthdata.nasa.gov/documentation/for_users/how_to_register). Be sure to remember the username and password you set up in this step, you will need it in the next step!

To successfully access NASA data through Python programs and Jupyter notebooks, we need to store the login credentials in a file. A template `.netrc` file is provided in this repository where users can enter their credentials.

Open the `.netrc` file that is included in this folder, and edit the following line:

```
machine urs.earthdata.nasa.gov login {username} password {password}
```

where `{username}` and `{password}` are replaced by your username and password created in the previous step. Save and close the file - you are now ready to access to Earth Observation data through the Earthdata portal! 

Open and step through the Jupyter notebook titled `1_Getting_Started.ipynb` to ensure that your credentials are correctly set up and working.