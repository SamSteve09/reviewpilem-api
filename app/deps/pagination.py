from fastapi import Depends, Query
def pagination_params(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    return {"offset": offset, "limit": limit}