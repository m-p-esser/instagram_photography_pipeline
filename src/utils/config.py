""" Create Pydantic Configuration models """

from prefect.blocks.system import Secret
from pydantic import BaseModel


class InstagramRequestParams(BaseModel):
    """Parameters for requesting the Instagram API"""

    user_names: list[str] = [
        "hannes_becker",
        "daniel_ernst",
        "martin_walter",
        "heatonthomas",
        "fabian.huebner",
        "germanroamers",
        "manuela_palmberger",
        "steven.t.luong",
        "_vincentefont_",
        "jacobnordin",
        "robinxbenjamin",
        "_marcelsiebert",
        "carlo_wiewaswo",
        "marinas.journey",
        "patricksvisuals",
        "_talfahrt",
        "benedikt.hoehny",
    ]


class DataProcessingParams(BaseModel):
    is_initial_data_ingestion: bool = True


class SourceToTargetKeyMapping(BaseModel):
    """Raw Data Keys to Database Table columns mapping"""

    user_keys: list[str] = [
        "pk",
        "username",
        "full_name",
        "is_verified",
        "account_type",
        "is_business",
        "business_category_name",
        "category_name",
        "category",
    ]
    user_profile_setting_keys: list[str] = [
        "pk",
        "profile_pic_url",
        "profile_pic_url_hd",
        "has_profile_pic",
        "is_private",
        "has_bio",
        "biography",
        "external_url",
    ]
    user_contact_details_keys: list[str] = [
        "pk",
        "public_email",
        "contact_phone_number",
        "public_phone_country_code",
        "public_phone_number",
        "business_contact_method",
    ]
    user_adresses_keys: list[str] = [
        "pk",
        "address_street",
        "city_id",
        "city_name",
        "latitude",
        "longitude",
        "zip",
        "instagram_location_id",
    ]
    # account_type_keys: list[str] = ["pk"]
