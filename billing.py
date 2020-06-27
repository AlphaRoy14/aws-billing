import boto3
import datetime
import re

def lambda_handler(event, context):
    # Create a Cost Explorer client
    client = boto3.client('ce')
    s3_client = boto3.client('s3')
    # client = boto3.client('resourcegroupstaggingapi')
    # response = client.get_tag_keys()
    # print(f"response is {response}")
    

    # Set time range to cover the last full calendar month
    # Note that the end date is EXCLUSIVE (e.g., not counted)
    now = datetime.datetime.utcnow()
    # Set the end of the range to start of the current month
    end = datetime.datetime(year=now.year, month=now.month, day=1)
    # Subtract a day and then "truncate" to the start of previous month
    start = end - datetime.timedelta(days=1)
    start = datetime.datetime(year=start.year, month=start.month, day=1)
    # Get the month as string for email purposes
    month = start.strftime('%Y-%m')

    # Convert them to strings
    start = start.strftime('%Y-%m-%d')
    end = end.strftime('%Y-%m-%d')
    
    yesterday = now - datetime.timedelta(days = 5)
    yesterday = yesterday.strftime("%Y-%m-%d")
    now = now.strftime("%Y-%m-%d")


    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': yesterday,
            'End': now
        },
        Granularity='MONTHLY',
        Metrics=['BlendedCost'],
        GroupBy=[
            {
                'Type': 'TAG',
                'Key': 'Project'
            },
           
        ]
    )


    tsv_lines = ["start_time, end_time, tag, amount, unit"]
    print(f"RESPONSEE IS {response}")
    start_time = response["ResultsByTime"][0]["TimePeriod"]["Start"]
    end_time = response["ResultsByTime"][0]["TimePeriod"]["End"]
    for project in response["ResultsByTime"][0]["Groups"]:
        namestring = project['Keys'][0]
        # print(f"THE NAME STRING IS {namestring}")
        name = re.search("\$(.*)", namestring).group(1)
        if name is None or name == "":
            name = "Other"
        amount = project['Metrics']['BlendedCost']['Amount']
        amount = float(amount)
        unit = project['Metrics']['BlendedCost']['Unit']
        line = "{}, {},{},{:,.2f},{}".format(start_time, end_time, name, amount, unit)
        tsv_lines.append(line)
        
    filename = f"{start_time}.csv"
    s3_client.put_object(Bucket = "icici-billing-data", Key = filename, Body = "\n".join(tsv_lines))

    print("\n".join(tsv_lines))



if __name__ == "__main__":
    lambda_handler({}, {})
