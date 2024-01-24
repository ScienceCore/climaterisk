# Getting Started with 2i2c Hub and NASA EarthData credentials

## Logging into the 2i2c Hub
Follow [this link ](https://showcase.2i2c.cloud/hub/login) to log into the 2i2c hub.

## Creating EarthData credentials
A good tutorial for creating EarthData credentials is provided at [this link](https://urs.earthdata.nasa.gov/documentation/for_users/how_to_register)

Once you have created an EarthData account and have login credentials, the last step is to create a file that can be read by Python and associated utilities.

Open the blank `.netrc` file that is included in this folder, and add the following line:

```
machine urs.earthdata.nasa.gov login {username} password {password}
```

where `{username}` and `{password}` are replaced by the login credentials you have created.