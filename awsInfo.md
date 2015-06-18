#AWS Setup Notes
This is just a bunch of notes on the AWS setup


The key is available from nigel if you need root.

##Time:
https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/set-time.html
Set to:
/usr/share/zoneinfo/Australia/Canberra

/etc/sysconfig/clock
>ZONE="Australia/Canberra"

>UTC=true

sudo ln -sf /usr/share/zoneinfo/America/Los_Angeles /etc/localtime

##Users:
First need a aws user account with ausdto with Mark Mc, then you can get an account for this box.
Currently just Nigel with an accout.

Talk to nigel if you need a user on this box
https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/managing-users.html

>Getting public key: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html#retrieving-the-public-key
>>ssh-keygen -y

##Attach Storage
-- Ensure that the ephemeral storage is setup when defining the instance.

-- Need to go back and check that the ephemeral storage is used for swap.


