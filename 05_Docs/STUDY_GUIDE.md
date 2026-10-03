# Study guide: know this project well enough to explain it

## 1. The design in one minute
A floor-standing kiosk for marking attendance. Student scans a QR code, the camera can capture a photo, and the Raspberry Pi sends the record to the AttendEase backend. The mechanical design has 5 groups: base, column, head, QR scanner, electronics enclosure.

## 2. Why these dimensions
- **Height about 1175 mm**: the screen sits around 1000 to 1150 mm, comfortable for most adults standing.
- **Tilt 40 deg (30 to 45 range)**: tilting the screen back reduces glare and suits both tall and short users. Design range is in the variants.
- **Base 620 x 520 mm, four lobes**: a wide footprint keeps the centre of gravity inside the base so the kiosk doesn't tip. The head overhangs the front, and the electronics box at the back balances it.
- **Column 300 x 200 mm, 2 mm steel panels**: enough room for cables; sheet metal is cheap to laser-cut and bend.
- **4 internal rails**: give the thin panels stiffness.
- **Flange bolted with 4 x M8**: the column can be removed for transport.
- **Electronics box at the rear**: serviceable from behind, away from users, cables pass through a 60 x 30 mm slot.

## 3. SolidWorks concepts you must know
- **Part vs assembly**: part = one solid; assembly = parts + mates.
- **Mates**: coincident (faces touch), concentric (shared axis), distance, angle. Fixed vs floating components.
- **Sheet metal**: thickness, bend radius, edge flange, bend relief, flat pattern.
- **Configurations / design tables**: one model, several versions (tilt 30/35/40).
- **Interference detection**: finds parts that overlap.
- **Exploded view, BOM, drawings**: how a design is communicated for manufacturing.
- **Import from STEP**: a neutral format for moving CAD between programs.

## 4. Software side
`kiosk_app.py` reads a scan, sends a JSON POST with a JWT token, shows the result, and if the backend is unreachable stores the record in SQLite and retries every 10 s. The test in `test_flow.py` proves: valid scan, duplicate (409), unknown QR (404), offline queueing, auto-sync.

## 5. Likely interview questions (practise your own answers)
1. Why did you tilt the display, and how would you change the angle? (angle mate / design table)
2. How would this be manufactured? (laser-cut 2 mm steel, bend, powder coat; flat patterns)
3. How do you stop it tipping over? (wide base, rear box counterweight; could add ballast)
4. What happens if the network drops? (SQLite queue + sync)
5. How is the kiosk authenticated to the backend? (JWT login, token refresh on 401)
6. What would you improve? (real sheet-metal bends, cooling analysis, cable routing, ADA reach height check, anti-tamper locks)

## 6. Be upfront about
The first model geometry was generated with a script (`source_scripts/`), then you completed the SolidWorks work (mates, sheet metal, drawings). Only claim what you have done yourself.
