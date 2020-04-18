import boto3
import logging
import json

instance_tag_key="env"
instance_tag_value_1="tag_wp_1"
instance_tag_value_2="tag_wp_2"
instance_tag_value_loop = [instance_tag_value_1, instance_tag_value_2]
EIP = "1.1.1.X"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ec2 = boto3.resource('ec2')

def get_instance_details(tagkey, tagvalue):
    filters = [{
            'Name': 'tag:'+tagkey,
            'Values': [tagvalue]
        }
    ]
    instances = ec2.instances.filter(Filters=filters)
    taggedinstanceid = [instance.id for instance in instances]
    if len(taggedinstanceid) == 1:
        for instance in instances:
            INSTANCEIP = instance.public_ip_address
            thisdict =	{
               "code": 0,
               "Instance_ID": instance.id,
               "Instance_IP": INSTANCEIP,
            }
        return thisdict
    elif len(taggedinstanceid) < 1:
        print ("No Instance found with"+" "+tagvalue+" " + "tag"+" "+"exiting")
        return {"code":1, "message":"No Instance found with"+" "+tagvalue+" " + "tag"+" "+"exiting"}
    elif len(taggedinstanceid) > 1:
        print ("More than one instance with tag"+" "+tagvalue+" " + "tag"+" "+"exiting")
        return {"code":1, "message":"More than one instance with"+" "+tagvalue+" " + "tag"+" "+"exiting"}
    else:
        return {"code":1, "message":"Some issue with"+" "+tagvalue+" " + "tag"}

def backup_id_find():
    results = {}
    for x in instance_tag_value_loop:
        get_instance_details_res = get_instance_details( tagkey=instance_tag_key, tagvalue=x )
        get_instance_details_res_code = get_instance_details_res['code']
        if get_instance_details_res_code == 0:
            results[x] = get_instance_details_res
        elif get_instance_details_res_code == 1:
            return get_instance_details_res
    print results


    ipresult1 = results[instance_tag_value_1]["Instance_IP"]
    ipresult2 = results[instance_tag_value_2]["Instance_IP"]
    idresult1 = results[instance_tag_value_1]["Instance_ID"]
    idresult2 = results[instance_tag_value_2]["Instance_ID"]

    if ipresult1 != EIP and ipresult2 != EIP:
        print ("EIP not found attached with any instance")
        return {"code":1, "message":"EIP not found attached with any instance"}
    else:
        if ipresult1 == EIP:
            PROD_SERVER_IP = ipresult1
            BACKUP_SERVER_IP = ipresult2
            PROD_INSTANCE_ID = idresult1
            BACKUP_INSTANCE_ID = idresult2
            check_server_status_res = check_server_status( BACKUP_INSTANCE_ID=BACKUP_INSTANCE_ID )
            check_server_status_res_code = check_server_status_res['code']
            if check_server_status_res_code == 0:
                return {"code":0, "message":BACKUP_SERVER_IP}
            elif check_server_status_res_code == 1:
                return check_server_status_res
            else:
                return {"code":1, "message":"Some Issue with getting Backup IP"}
        elif ipresult2 == EIP:
            PROD_SERVER_IP = ipresult2
            BACKUP_SERVER_IP = ipresult1
            PROD_INSTANCE_ID = idresult2
            BACKUP_INSTANCE_ID = idresult1
            check_server_status_res = check_server_status( BACKUP_INSTANCE_ID=BACKUP_INSTANCE_ID )
            check_server_status_res_code = check_server_status_res['code']
            if check_server_status_res_code == 0:
                print BACKUP_SERVER_IP
                return {"code":0, "message":BACKUP_SERVER_IP}
            elif check_server_status_res_code == 1:
                return check_server_status_res
            else:
                return {"code":1, "message":"Some Issue with getting Backup IP"}
        else:
            return {"code":1, "message":"Some error when analysing IP"}


def check_server_status(BACKUP_INSTANCE_ID):
    print BACKUP_INSTANCE_ID
    filters = [{}]
    ec2instance = ec2.Instance(BACKUP_INSTANCE_ID)
    instance_state = (ec2instance.state['Name'])
    print instance_state
    if instance_state == 'running':
        print ("Backup Server is running")
        return {"code":0, "message":"Backup Server is running"}
    elif instance_state == 'stopped':
        print ("Backup Server is stopped")
        return {"code":1, "message":"Backup Server is stopped"}
    elif instance_state == 'pending':
        print ("Backup Server Status is pending")
        return {"code":1, "message":"Backup Server Status is pending"}
    elif instance_state == 'stopping':
        print ("Backup Server Status is stopping")
        return {"code":1, "message":"Backup Server Status is stopping"}
    else:
        print instance_state
        return {"code":1, "message":"Some Issue"}

def lambda_handler(event, context):
    backup_id_find_res = backup_id_find()
    return backup_id_find_res

