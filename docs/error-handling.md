# Error Handling

This service enforces a predictable JSON error contract so clients can handle failures safely and consistently.

## Goals

- Return machine-readable errors for all common failure classes.
- Avoid leaking internal stack traces.
- Keep error shapes stable across endpoints.

## Error Contract

| Status | Source | Body Shape | Typical Trigger |
|---|---|---|---|
| 400 | Route-level check | `{"detail": "..."}` | Invalid file type for CSV upload |
| 404 | FastAPI/router | `{"detail": "..."}` | Unknown route or missing resource |
| 422 | FastAPI validation | `{"detail": [...]}` | Invalid request body fields |
| 500 | Global exception handler | `{"detail": "Internal Server Error"}` | Unexpected server exception |

## 422 Validation Errors

- FastAPI and Pydantic validate request payloads before route logic runs.
- Invalid payloads return `422 Unprocessable Entity` with `detail` as an array describing validation problems.

Example (`POST /users` with invalid email):

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error"
    }
  ]
}
```

## 404 Not Found Errors

- Unknown paths return FastAPI default:

```json
{"detail": "Not Found"}
```

- Known-resource misses return explicit route-level messages:
  - `GET /users/{id}`, `PUT /users/{id}` -> `{"detail": "User not found"}`
  - `GET /urls/{id}`, `PUT /urls/{id}` -> `{"detail": "URL not found"}`
  - `POST /urls` when `user_id` does not exist -> `{"detail": "User not found"}`

## 400 Client Errors

- `POST /users/bulk` accepts CSV only.
- Non-CSV uploads are rejected with:

```json
{"detail": "Only CSV files allowed"}
```

## 500 Internal Server Errors

- A global exception handler catches unhandled exceptions and normalizes response output.
- API response shape for internal failures:

```json
{"detail": "Internal Server Error"}
```

This behavior is intentionally generic to avoid exposing implementation details.

## Test Coverage

The following cases are covered in the test suite:

- Invalid email returns `422`
- Wrong upload type returns `400`
- Missing owner/resource returns `404`
- Unknown route returns JSON `404`
- Simulated unhandled exception returns normalized `500`

See tests in `tests/test_error_handling.py`.
