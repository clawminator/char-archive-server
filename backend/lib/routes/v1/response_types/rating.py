from typing import List

from pydantic import BaseModel

from lib.routes.v1.response_types.node import NodeRating


class RatingResponse(BaseModel):
    ratings: List[NodeRating]
