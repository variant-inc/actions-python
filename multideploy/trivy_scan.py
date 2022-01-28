import asyncio

from multideploy.utils import multiline_log_printer
from multideploy.exceptions import TrivyException

async def run_trivy_scan(lambda_name: str, image_name: str):
    # TODO pull trivy ignore
    trivy_low = asyncio.create_subprocess_shell(
        f"trivy image --severity=HIGH,MEDIUM,LOW,UNKNOWN {image_name}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    trivy_critical = asyncio.create_subprocess_shell(
        f"trivy image --exit-code 1 --severity=CRITICAL {image_name}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, _ = await (await trivy_low).communicate()
    multiline_log_printer(lambda_name, "trivy_low", "INFO", stdout)

    proc = await trivy_critical
    stdout, stderr = await proc.communicate()

    if proc.returncode == 1:
        status = "ERROR"
    else:
        status = "INFO"

    multiline_log_printer(lambda_name, "trivy_critical", status, stdout)

    if proc.returncode == 1:
        raise TrivyException

    if stderr:
        multiline_log_printer(lambda_name, "trivy_critical", "CRITICAL", stderr)
        raise TrivyException
