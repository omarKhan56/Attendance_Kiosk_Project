# SolidWorks guide: turning the imported model into your own assembly
Time needed: about 1 to 2 weeks part-time. Do the steps in order.

## 1. Mates (hold the parts together)
All parts are already in the right place, so mates just lock that position. Keep `Base_Plate` **Fixed**; right-click every other part and choose **Float**. Add mates in this order (Mate tool, pick faces, confirm):

| Part | Mates |
|---|---|
| Column_Flange | Coincident: flange bottom face to base plate top face. Concentric: its 4 holes to the base plate holes (do 2 holes, the rest follow). |
| Bolt_M8 x4 | Concentric: bolt shank to hole. Coincident: bolt head underside to flange top face. |
| Rubber_Foot x4 | Coincident: foot top to base plate bottom. Distance: position at each lobe end. |
| Frame_Rail x4 | Coincident: rail bottom to flange top. Distance: 130 mm in X and 80 mm in Y from the centre planes. |
| Column panels | Front/Rear: Coincident to flange top, Distance 99 mm from Front plane (2 mm thick). Left/Right: same idea in X (149 mm). Top plate: Coincident on top of the panels. |
| QR_Scanner_Module / Bracket | Module: Coincident to front panel inner face, Concentric/centred on the slot. Bracket: Coincident to module back. |
| Electronics_Box | Coincident: open face to rear cover outer face. Width mate to centre it on the column. |
| Mounting_Plate, Pi, PSU | Coincident each to the face behind it; Distance to position. |
| Cable_Gland x3 | Coincident to box bottom face, Distance in X (-60, 0, 60). |
| Tilt_Bracket | Coincident: base plate to top plate of column. |
| Head_Rear_Housing | **Angle mate** between housing bottom face and column top plate = **40 deg** (limit 30 to 45). This is your adjustable tilt. |
| Display_Bezel, Display_15in_Panel | Coincident to housing front rim / bezel back. |
| Camera_Mount_Plate, Camera_Module | Coincident to bezel back; lens Concentric with the bezel hole. |
| Vent_Grille | Concentric with the housing hole, Coincident to the side wall. |

Check: drag the head. If it moves freely only around the tilt axis, the mates are correct. Run **Evaluate > Interference Detection**; expected result is none.

## 2. Sheet metal
Open each panel part (e.g. `Column_Front_Panel`): Insert > Sheet Metal > Convert to Sheet Metal (thickness 2 mm). Then add edge flanges (Sheet Metal tab > Edge Flange, 15 mm) and bend reliefs, and Flatten to get the flat pattern. Compare with `flat_patterns_DXF/`.

## 3. Tilt configurations / design table
Use Insert > Tables > Design Table, or simply make 3 configurations (Tilt30, Tilt35, Tilt40) that set the angle mate value. Compare with the variants in `01_CAD/tilt_variants/`.

## 4. Exploded view
Assembly tab > Exploded View. Drag parts along their axis (head parts along the screen normal, panels outward, bolts up). Add explode lines. Use `02_Renders/exploded_view.png` as a layout reference.

## 5. Motion study
New Motion Study > Animation. Drive the angle mate from 30 to 45 deg for the tilt animation; use Animate Collapse/Explode for the exploded one. Reference: the two GIFs.

## 6. Drawings
File > Make Drawing from Assembly. Sheet 1: 3 views + iso, balloons, BOM table. Then base plate drawing and the flat pattern drawing of a panel. Reference: `03_Drawings/Attendance_Kiosk_Drawings.pdf`.

## 7. Appearance and render
Apply materials: powder-coated steel, black glass (display), brushed aluminium (bezel). Render with SolidWorks Visualize (hero, exploded, and internal view with panels hidden).

## Note on orientation
SolidWorks treats **Y as up**. The main STEP file was built with Z as up, so it opens lying on its side. Use `01_CAD/SolidWorks_upright/Attendance_Kiosk_Assembly_upright.step` instead: it is the same model rotated so it opens standing up, with the front facing the Front view. Use this file for your SolidWorks work so that Front / Top / Right drawing views come out correctly.
