#AWS Setup Notes
This is just a bunch of notes on the AWS setup.
Currently we are using the Amazon image, we may change to ubuntu later for consistency with our preferred dev environment.


Note: df -k

The key is available from nigel if you need root.

##Configure security groups
- OrietDb
- SSH
TBA

##Time:
https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/set-time.html

Set `/etc/sysconfig/clock` to:

`ZONE="Australia/Canberra"`
`UTC=true`

Which actually points to `/usr/share/zoneinfo/Australia/Canberra`

sudo ln -sf /usr/share/zoneinfo/Australia/Canberra /etc/localtime

##Users:
First need a aws user account with ausdto with Mark Mc, then you can get an account for this box.
Currently just Nigel with an accout.

Talk to nigel if you need a user on this box
https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/managing-users.html

>Getting public key: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html#retrieving-the-public-key
>>ssh-keygen -y

Setup password based logon for crawler
in: `/etc/ssh/ssh_config`, uncomment: `PasswordAuthentication yes`
*Note: This is becuase I could not get the script to run with key based auth, there may be a way to do this though, will talk to mark.*

##OrientDb Install
- Download using wget (remember to quote the link)
- Extract to /opt/orientdb
- Update the config
- Make scripts executable `sudo chmod 755 bin/*.sh`
- ???Make config executable???? `sudo chmod -R 777 config/`
- I chown'ed the oriendb folder to be owned be crawler too.
- *TODO: Confirm above is appropriate - it comes from the orientdb guide. Has also caused logon problems with the nokout user* 
- Set script params by editing the bin/orientdb.sh file: `ORIENTDB_DIR="/opt/orientdb"` and `ORIENTDB_USER="crawler"`
- change log folder permissions to 555



##Git Install
- `sudo yum install git`
- git version 2.1.0

##Node Install
NOTE: The current version in amazon is v0.10.36 some dev has been based on 0.12\* npm version is 1.3.6.
- `sudo yum install nodejs --enablerepo=epel`
- `sudo yum install npm --enablerepo=epel`

##Clone Discovery Layer Repo
TBA
Should we just clone crawler - might be a lot more in there in the future.

##Attach Storage
-- Ensure that the ephemeral storage is setup when defining the instance.
-- Need to go back and check that the ephemeral storage is used for swap.

IF NEW a new filesystem make the filesystem `sudo mkfs -t ext4 /dev/xvdf` then `mount /dev/xvdf/ /data/vol1/`
IF NEW create a database directory `/data/vol1/database`

Now make sure it gets mounted on boot...
Copy the fstab `sudo cp /etc/fstab /etc/fstab.orig`
Add this line `/dev/xvdf   /data/vol1  ext4    defaults,nofail 0   2`
Check config with mount -a
Create symbolic link to the OrientDb databases directory `sudo ln -s /data/vol1/database/ databases`

##Create Database
TBA but should be able to import db setup from `discoveryLayer/crawler/dbBckup`

##

