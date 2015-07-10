#AWS Setup Notes
This is just a bunch of notes on the AWS setup.
Currently we are using the Amazon image, we may change to ubuntu later for consistency with our preferred dev environment.

Note: df -k

The key is available from nigel if you need root.

##Configure security groups

##Time:
https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/set-time.html

Set `/etc/sysconfig/clock` to:

`ZONE="Australia/Canberra"`
`UTC=true`

Which actually points to `/usr/share/zoneinfo/Australia/Canberra`

sudo ln -sf /usr/share/zoneinfo/Australia/Canberra /etc/localtime

##Users:

Talk to nigel if you need a user on this box
https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/managing-users.html

>Getting public key: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html#retrieving-the-public-key
>>ssh-keygen -y


##Install Tools
###Git
    sudo apt-get install git
    check git `git --version
    //Output like: git version 1.9.1
>Note: You may also possibly need to configure git ssh-keygen

###Docker
    wget -qO- https://get.docker.com/ | sh
    docker --version
    //Output like: Docker version 1.7.0, build 0baf609
###Docker-compose
    curl -L https://github.com/docker/compose/releases/download/1.3.1/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    docker-compose --version
    //Output like: docker-compose version: 1.3.1
    //             CPython version: 2.7.9
    //             OpenSSL version: OpenSSL 1.0.1e 11 Feb 2013
    exit
Docker also has an issue with /var/lib/docker/devicemapper so to fix  rename to /var/lib/docker/devicemapper.old

###Emacs
sudo apt-get install emacs24-nox

##Attach Storage
-- Ensure that the ephemeral storage is setup when defining the instance.
-- Need to go back and check that the ephemeral storage is used for swap.

In the aws EC2 console select the volumes and select the discoData volume:
1. Volumes
2. Actions
3. Attach Volume
4. Select Instance

Mount the filesystem

    mkdir /data
    mkdir /data/disco
    mount /dev/xvdf/ /data/disco/
    cd /data/disco/

THESE STEPS WILL DESTROY EXISTING DATA
Inspect the volume and ONLY IF REQUIRED create a filesystem `sudo mkfs -t ext4 /dev/xvdf`
Create a crawler directory so that you have /data/disco/crawler

Now make sure it gets mounted on boot...

    sudo cp /etc/fstab /etc/fstab.orig //Copy the fstab
    vi /etc/fstab
        // Add: /dev/xvdf   /data/disco ext4    defaults,nofail 0   2
    mount -a

##Setup Deployment User
Create the deployment user deploy `sudo adduser deploy`
As deploy, create our deployment folder `mkdir /opt/ausDTO`
Clone appropriate projects into the folder
sudo usermod -aG docker deploy
