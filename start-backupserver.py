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
    #main_func_res = main_func( tagkey=instance_tag_key, tagvalue=instance_tag_value_1 )
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
            #PROD_SERVER_IP = ipresult1
            #BACKUP_SERVER_IP = ipresult2
            PROD_INSTANCE_ID = idresult1
            BACKUP_INSTANCE_ID = idresult2
            return {"code":0, "message":BACKUP_INSTANCE_ID}
        elif ipresult2 == EIP:
            #PROD_SERVER_IP = ipresult2
            #BACKUP_SERVER_IP = ipresult1
            PROD_INSTANCE_ID = idresult2
            BACKUP_INSTANCE_ID = idresult1
            return {"code":0, "message":BACKUP_INSTANCE_ID}
        else:
            return {"code":1, "message":"Some error when analysing IP"}

    #print ("PROD_SERVER_IP:", PROD_SERVER_IP)
    #print ("BACKUP_SERVER_IP:", BACKUP_SERVER_IP)
    print ("PROD_INSTANCE_ID:", PROD_INSTANCE_ID)
    print ("BACKUP_INSTANCE_ID:", BACKUP_INSTANCE_ID)
    #return {"code":0, "message":BACKUP_INSTANCE_ID}



def start_server(BACKUP_INSTANCE_ID):
    print BACKUP_INSTANCE_ID
    filters = [{}]
    ec2instance = ec2.Instance(BACKUP_INSTANCE_ID)
    instance_state = (ec2instance.state['Name'])
    print instance_state
    if instance_state == 'running':
        print ("Backup Server is already running")
        return {"code":2, "message":"Backup Server is already running"}
    elif instance_state == 'stopped':
        print ("Starting Backup Server")
        startingUp = ec2.instances.filter(InstanceIds=[BACKUP_INSTANCE_ID]).start()
        return {"code":0, "message":"Starting Backup Server"}
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
    backup_id_find_res_code = backup_id_find_res['code']
    backup_id_find_res_message = backup_id_find_res['message']
    if backup_id_find_res_code == 0:
        print ("Starting BACKUP_INSTANCE_ID:", backup_id_find_res_message)
        start_server_res = start_server( BACKUP_INSTANCE_ID=backup_id_find_res_message )
        return start_server_res
    elif backup_id_find_res_code == 1:
        return backup_id_find_res
    else:
        return backup_id_find_res
