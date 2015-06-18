#AWS Setup Notes
This is just a bunch of notes on the AWS setup

Note: df -k

The key is available from nigel if you need root.

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

##OrientDb Install
Download using wget (remember to quote the link)
Update the config

##Git Install


##Node Install
`sudo yum install nodejs --enablerepo=epel`
`sudo yum install npm --enablerepo=epel`

##Attach Storage
-- Ensure that the ephemeral storage is setup when defining the instance.
-- Need to go back and check that the ephemeral storage is used for swap.

IF NEW a new filesystem make the filesystem `sudo mkfs -t ext4 /dev/xvdf` then `mount /dev/xvdf/ /data/vol1/`
IF NEW create a database directory `/data/vol1/database`

Now make sure it gets mounted on boot...
Copy the fstab `sudo cp /etc/fstab /etc/fstab.orig`
Add this line `/dev/xvdf   /data/vol1  ext4    defaults,nofail 0   2`
Create symbolic link to the OrientDb databases directory `sudo ln -s /data/vol1/database/ databases`




