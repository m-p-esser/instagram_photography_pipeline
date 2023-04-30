""" Create Pydantic Configuration models """

from prefect.blocks.system import Secret
from pydantic import BaseModel


class InstagramRequestParams(BaseModel):
    """Parameters for requesting the Instagram API"""

    user_names: list[str] = ["hannes_becker", "daniel_ernst"]
