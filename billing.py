import boto3
import datetime
import re

def lambda_handler(event, context):
    client = boto3.client("ce")
    response = client.get_cost_and_usage(
        TimePeriod={
            'start': start,
            'end': end
        },
        Granularity='MONTHLY'
        Metrics=['BlendedCost']
        GroupBy=[
            {
                'Type': 'TAG'
                'Key': 'web app'
            }
        ]
    )
    for app in response["ResultsByTime"][0]["Groups"]:
        namestr = app['Keys'][0]
        name = re.search("\$(.*)", namestr).group(1)
        if not name or name == "":
            name = "other"

        amount = app['Metrics']['BlendedCost']['Amount']
        line = f"{name}\t${:,.2f}"
        print(line)