# Datacats Vagrant Base Box

This directory contains the build instructions to build a Datacats (developmentseed [fork](http://github.com/developmentseed/datacats)) base box for development.
The base box will contain:

- `datacats` command 
- docker-engine and datacats docker containers
- Nginx server forwarding http://localhost:5102 to the VM host ip at port 80

To build the box:

```
vagrant up
vagrant package --output devseed-datacats.box
```

For convenience, @developmentseed uploads boxes to [S3](https://s3.amazonaws.com/offgrid-vbox/devseed-datacats.box)
