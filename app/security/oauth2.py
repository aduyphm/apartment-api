from typing import Any, Dict, List, Optional, Union

from fastapi.exceptions import HTTPException
from fastapi.openapi.models import OAuth2 as OAuth2Model
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.param_functions import Form
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN


class OAuth2ClientCredentialsRequestForm:
    """
    This is a dependency class, use it like:

        @app.post("/login")
        def login(form_data: OAuth2ClientCredentialsRequestForm = Depends()):
            data = form_data.parse()
            print(data.client_id)
            print(data.client_secret)
            for scope in data.scopes:
                print(scope)
            return data


    It creates the following Form request parameters in your endpoint:

    grant_type: the OAuth2 spec says it is required and MUST be the fixed string "client_credentials".
        Nevertheless, this dependency class is permissive and allows not passing it. If you want to enforce it,
        use instead the OAuth2ClientCredentialsRequestFormStrict dependency.
    client_id: client_id string. OAuth2 recommends sending the client_id and client_secret (if any)
        using HTTP Basic auth, as: client_id:client_secret
    client_secret: client_secret string. OAuth2 recommends sending the client_id and client_secret (if any)
        using HTTP Basic auth, as: client_id:client_secret
    scope: Optional string. Several scopes (each one a string) separated by spaces. E.g.
        "items:read items:write users:read profile openid"

    """

    def __init__(
        self,
        grant_type: str = Form(default=None, regex="client_credentials"),
        client_id: str = Form(default=""),
        client_secret: str = Form(default=""),
        scope: str = Form(default=""),
    ):
        self.grant_type = grant_type
        self.client_id = client_id
        self.client_secret = client_secret
        self.scopes = scope.split()


class OAuth2ClientCredentialsRequestFormStrict(OAuth2ClientCredentialsRequestForm):
    """
    This is a dependency class, use it like:

        @app.post("/login")
        def login(form_data: OAuth2ClientCredentialsRequestFormStrict = Depends()):
            data = form_data.parse()
            print(data.client_id)
            print(data.client_secret)
            for scope in data.scopes:
                print(scope)
            return data


    It creates the following Form request parameters in your endpoint:

    grant_type: the OAuth2 spec says it is required and MUST be the fixed string "client_credentials".
        This dependency is strict about it. If you want to be permissive, use instead the
        OAuth2ClientCredentialsRequestForm dependency class.
    client_id: client_id string. OAuth2 recommends sending the client_id and client_secret (if any)
        using HTTP Basic auth, as: client_id:client_secret
    client_secret: client_secret string. OAuth2 recommends sending the client_id and client_secret (if any)
        using HTTP Basic auth, as: client_id:client_secret
    scope: Optional string. Several scopes (each one a string) separated by spaces. E.g.
        "items:read items:write users:read profile openid"

    """

    def __init__(
        self,
        grant_type: str = Form(regex="client_credentials"),
        client_id: str = Form(),
        client_secret: str = Form(),
        scope: str = Form(default=""),
    ):
        super().__init__(
            grant_type=grant_type,
            client_id=client_id,
            client_secret=client_secret,
            scope=scope,
        )


class OAuth2(SecurityBase):
    def __init__(
        self,
        *,
        flows: Union[OAuthFlowsModel, Dict[str, Dict[str, Any]]] = OAuthFlowsModel(),
        scheme_name: Optional[str] = None,
        description: Optional[str] = None,
        auto_error: Optional[bool] = True
    ):
        self.model = OAuth2Model(flows=flows, description=description)
        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization")
        if not authorization:
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
                )
            else:
                return None
        return authorization


class OAuth2ClientCredentials(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        description: Optional[str] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(clientCredentials={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(
            flows=flows,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


class SecurityScopes:
    def __init__(self, scopes: Optional[List[str]] = None):
        self.scopes = scopes or []
        self.scope_str = " ".join(self.scopes)
