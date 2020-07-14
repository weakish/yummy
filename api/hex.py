import base64
import hashlib
import json
import os
from typing import Optional, Dict, Union, Tuple, Any, Literal, TypedDict

import firebase_admin
from firebase_admin import firestore, credentials
from flask import Flask, request



class Review(TypedDict):
    rating: Optional[Literal[1, 2, 3, 4, 5]]
    comment: Optional[str]
    meta: Dict[str, Any]


class ErrorMessage(TypedDict):
    error: str


HttpError = Tuple[ErrorMessage, int]
HttpHeaders = Dict[str, str]

cert = json.loads(base64.b64decode(os.environ["GCLOUD_CREDENTIALS"]))
cred = credentials.Certificate(cert)
firebase_admin.initialize_app(cred)
db = firestore.client()

app: Flask = Flask(__name__)


def ensure_hex64(hex64) -> Union[str, HttpError]:
    try:
        int(hex64, 16)
    except ValueError:
        return {"error": f"{hex64} is not hexadecimal"}, 400
    else:
        if len(hex64) == 64:
            return hex64
        else:
            return {"error": "hexadecimal number should have 64 digits"}, 400


def ensure_document(document: Dict[str, Any]) -> Union[Dict[str, Any], HttpError]:
    if document is None:
        return {"error": "not found"}, 404
    else:
        return document


@app.route("/hex/<hex_64>", methods=["GET", "PATCH"])
def yummy_hex(
    hex_64: str,
) -> Union[Dict[str, Review], Tuple[Review, HttpHeaders], HttpError]:
    hex64: Union[str, HttpError] = ensure_hex64(hex_64)
    if type(hex64) is str:
        if request.method == "GET":
            return {
                r.id: r.to_dict()
                for r in db.collection("hex")
                .document(hex64)
                .collection("review")
                .stream()
            }
        elif request.method == "PATCH":
            sha256: str = hashlib.sha256(request.get_data()).hexdigest()
            data: Dict[str, Any] = request.get_json(force=True)
            rating: Optional[Literal[1, 2, 3, 4, 5]] = data.pop("rating", None)
            if rating in [None, 1, 2, 3, 4, 5]:
                comment: str = data.pop("comment", None)
                review: Review = {"rating": rating, "comment": comment, "meta": data}
                db.collection("hex").document(hex64).collection("review").document(
                    sha256
                ).set(review)
                return review, {"Content-Location": f"/api/hex/{hex64}/{sha256}"}
            else:
                return (
                    {"error": "rating (if specified) should be 1, 2, 3, 4, or 5"},
                    400,
                )
    else:
        return hex64


@app.route("/hex/<hex_64>/<sha_256>")
def yummy_review(hex_64: str, sha_256: str) -> Union[Review, HttpError]:
    hex64: Union[str, HttpError] = ensure_hex64(hex_64)
    if type(hex64) is str:
        sha256: Union[str, HttpError] = ensure_hex64(sha_256)
        if type(sha256) is str:
            return ensure_document(
                db.collection("hex")
                .document(hex64)
                .collection("review")
                .document(sha256)
                .get()
                .to_dict()
            )
        else:
            return sha256
    else:
        return hex64
