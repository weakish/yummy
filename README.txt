Yummy - an anonymous fictional review database for hex numbers

Usage:

Request: GET /ping
Response: "pong"

Request: GET /hex/<hexadecimal_number_of_64_digits>
Response:
    {
        id: {
            rating: Optional[Literal[1, 2, 3, 4, 5]]
            comment: Optional[str]
            more_key: Optional[JsonValue]
        }
        # more
    }

Request: PATCH /hex/<hexadecimal_number_of_64_digits>
    {
        rating: Optional[Literal[1, 2, 3, 4, 5]]
        comment: Optional[str]
        more_key: Optional[JsonValue]
    }
Response:
    Content-Location: /hex/<hexadecimal_number_of_64_digits>/<id>
    {
        rating
        comment
        meta: {
            more_key
        }
    }

Request: GET /hex/<hexadecimal_number_of_64_digits>/<id>
Response:
    {
        rating
        comment
        meta: {
            more_key
        }
    }
  
