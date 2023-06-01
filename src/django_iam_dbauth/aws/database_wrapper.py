import getpass
import boto3
from os import environ
from django_iam_dbauth.utils import resolve_cname


def get_aws_connection_params(params, region=environ.get('AWS_REGION')):
    enabled = params.pop("use_iam_auth", None)
    if enabled:
        region_name = params.pop("region_name", None)
        session = boto3.session.Session()
        rds_client = session.client(service_name="rds", region_name=region)

        hostname = params.get("host")
        if hostname:
            hostname = (
                resolve_cname(hostname)
                if params.pop("resolve_cname_enabled", True)
                else hostname
            )
        else:
            hostname = "localhost"

        params["password"] = rds_client.generate_db_auth_token(
            DBHostname=hostname,
            Port=params.get("port", 5432),
            DBUsername=params.get("user") or getpass.getuser(),
            Region=region
        )
        print(f'Requested RDS Auth Token: host={hostname} port={params.get("port")} dbuser={params.get("user")} region={region}')

    return params
