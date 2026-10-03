# Backend integration notes (AttendEase)

**Decision:** the kiosk is tested against the included mock server (`04_Software/mock_backend`). The real AttendEase backend was not modified.

## What the real backend does today (from reading its code)
- Login: `POST /api/auth/login` with `{email, password}` -> returns `{_id, name, email, role, token}`. Login is rate limited to 5 requests per minute.
- Faculty creates a class QR: `POST /api/attendance/generate-qr` (QR lasts 30 s; contains sessionId, qrCode, classId).
- Student marks attendance: `POST /api/attendance/mark` with `{sessionId, qrCode, biometricAssertion?}`, using the **student's own JWT**. Role must be `student`.
- Rules enforced: QR valid and unexpired, class schedule window, student enrolled, one record per class per day.

## Why the kiosk cannot call it directly yet
The kiosk scans a student's code, but the real endpoint identifies the student by their own JWT, not by a scanned code. There is no kiosk route.

## Differences between the mock and the real API
| | Mock | Real |
|---|---|---|
| Login body | `username`, `password` | `email`, `password` |
| Token field | `access_token` | `token` |
| Mark route | `POST /api/attendance` | `POST /api/attendance/mark` |
| Identifies student by | scanned QR value | student JWT |

## If you integrate later (not done)
Add a kiosk-only route (for example `POST /api/attendance/kiosk-mark`) that accepts a kiosk account's JWT plus a scanned `studentId` and `classId`, reuses the existing checks (enrolment, schedule window, duplicate per day), and records `markedBy: 'kiosk'`. This needs a new role value and a new `markedBy` value in the schemas. Then change `kiosk_app/config.py` and `api_client.py` to match the field names above.

## How to describe it honestly
"Kiosk client tested against a mock AttendEase-style REST API (JWT auth, offline queue and sync)." Do not say it is integrated with the live AttendEase system.
