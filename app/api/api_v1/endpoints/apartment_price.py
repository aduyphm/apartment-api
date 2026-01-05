import uuid
import requests
import datetime
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.api import deps
from app.models.apartment_price import ApartmentPrice
from app.schemas.apartment_price import ApartmentPriceInput, ApartmentPriceOutput
from app.schemas.token import TokenInspectOutput
from app.core.config import settings
from app.utils.uuid import is_valid_uuid
from app.ml.apartment_price import ApartmentPriceModelling
from app.security import OAuth2ClientCredentials

router = APIRouter()

oauth2_scheme = OAuth2ClientCredentials(
    tokenUrl=settings.OAUTH2_TOKEN_URL,
    scheme_name="OAuth2ClientCredentials",
)

file_path = settings.ML_MODELS_DIRECTORY + settings.APARTMENT_PRICE_MODEL_FILENAME
apartment_price_model = ApartmentPriceModelling(model_path=file_path)


def inspect_token(token: str = Depends(oauth2_scheme)):
    headers = {"Content-type": "application/json",
               "Accept": "application/json"}

    data = {
        "token": token,
        "scopes": ["apartment-price/prediction"]
    }

    try:
        response = requests.post(settings.OAUTH2_TOKEN_INSPECT_URL, json=data, headers=headers,
                                 timeout=settings.CALL_OAUTH2_SERVICE_TIMEOUT)
        if response.status_code != 200:
            print(response.text)
            return TokenInspectOutput(
                valid=False,
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="unauthorized",
            )
        return response.json()
    except Exception as e:
        print(e)
        return TokenInspectOutput(
            valid=False,
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="unauthorized",
        )


@router.post("/prediction", status_code=200, response_model=ApartmentPriceOutput)
async def prediction(*, apartment_price_input: ApartmentPriceInput, db: Session = Depends(deps.get_db),
                     client_message_id: str = Header(...),
                     token_inspect_output: TokenInspectOutput = Depends(inspect_token)):
    if not is_valid_uuid(client_message_id):
        raise HTTPException(status_code=400, detail="client-message-id must be uuid4 string")
    if not token_inspect_output["valid"]:
        raise HTTPException(status_code=token_inspect_output["status_code"], detail=token_inspect_output["detail"])
    input_params = {
        "area": apartment_price_input.area,
        "pn": apartment_price_input.n_bedrooms,
        "duong": apartment_price_input.street,
        "ref_tinh_code": int(apartment_price_input.province_code),
        "ref_huyen_code": int(apartment_price_input.district_code),
        "ref_xa_code": int(apartment_price_input.ward_code),
        "prj_name": apartment_price_input.project_name
    }

    pred_price = apartment_price_model.predict(**input_params)
    if pred_price == settings.APARTMENT_PRICE_MODEL_DEFAULT_INVALID_VALUE_RETURN:
        result = 0
        price = -1
        price_min = -1
        price_max = -1
        price_range = [price_min, price_max]
    else:
        result = 1
        price = pred_price
        price_min = -1
        price_max = -1
        price_range = [price_min, price_max]
    apartment_price = ApartmentPrice(
        id=str(uuid.uuid4()),
        client_id=token_inspect_output["client_id"],
        client_message_id=client_message_id,
        province_code=apartment_price_input.province_code,
        district_code=apartment_price_input.district_code,
        ward_code=apartment_price_input.ward_code,
        street=apartment_price_input.street,
        project_name=apartment_price_input.project_name,
        apartment_name=apartment_price_input.apartment_name,
        n_bedrooms=apartment_price_input.n_bedrooms,
        area=apartment_price_input.area,
        result=result,
        price=price,
        price_min=price_min,
        price_max=price_max,
        created_at=datetime.datetime.utcnow()
    )
    db.add(apartment_price)
    db.commit()
    db.refresh(apartment_price)
    return ApartmentPriceOutput(result=result, price=price, price_range=price_range)
