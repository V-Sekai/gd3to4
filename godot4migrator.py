import os
import sys
import re

replacements = [
    ('Spatial', 'Node3D'),
    ('Sprite', 'Sprite2D'),
    ('Camera', 'Camera3D'),
    ('Skeleton', 'Skeleton3D'),
    ('VisualInstance', 'VisualInstance3D'),
    ('GeometryInstance', 'GeometryInstance3D'),
    ('Skeleton3DIK', 'SkeletonIK3D'),
    ('PhysicalBone', 'PhysicalBone3D'),
    ('SkeletonIK', 'SkeletonIK3D'),
    ('MeshInstance', 'MeshInstance3D'),
    ('KinematicBody', 'KinematicBody3D'),
    ('Listener', 'Listener3D'),
    ('RigidBody', 'RigidBody3D'),
    ('RayCast', 'RayCast3D'),
    ('RayShape', 'RayShape3D'),
    ('Joint', 'Joint3D'),
    ('Light', 'Light3D'),
    ('SpringArm', 'SpringArm3D'),
    ('Shape', 'Shape3D'),
    ('Particles', 'Particles3D'),
    ('linear_interpolate', 'lerp'),
    ('PoolByteArray', 'PackedByteArray'),
    ('PoolIntArray', 'PackedInt32Array'), # FIXME: 64?
    ('PoolRealArray', 'PackedFloat32Array'), # FIXME: 64?
    ('PoolStringArray', 'PackedStringArray'),
    ('PoolVector2Array', 'PackedVector2Array'),
    ('PoolVector3Array', 'PackedVector3Array'),
    ('PoolColorArray', 'PackedColorArray'),
    ('Node3DMaterial', 'StandardMaterial3D'),
    #('World', 'World3D'),
    ]

def findcomment(fline):
    ll = len(fline)
    i = 0
    nonwsi = 0
    strtype = 0
    esc = False
    for ch in fline:
        if esc:
            esc = False
        elif strtype > 0:
            if ch == '\\':
                esc = True
            elif ch == "'" and strtype == 1:
                strtype = 0
            elif ch == '"' and strtype == 2:
                strtype = 0
        elif ch == "'":
            strtype = 1
        elif ch == '"':
            strtype = 2
        elif ch == '#':
            return nonwsi
        elif ch.isspace():
            nonwsi = i
        i += 1
    return nonwsi

EXPORT_PAREN = re.compile(r"^( *)(\bexport *)?(?:\(([^)]*)\))?( *var *[^=:]*)(: [^ =]*)?( *=.*)?")
SETGET_PATTERN = re.compile(r"(.*)\bsetget *([^,]*)(?:, *(.*))?$")
YIELD_PATTERN = re.compile(r"\byield *\((.*?)(, *[\"'].*[\"'])?\)$|\byield (.*)$")
'''
OLD:
export(Color) var bottom_left_color = Color() setget _set_bottom_left_color
NEW:
@export var bottom_left_color : Color = Color():
	set = _set_bottom_left_color
'''


# FIXME: We need to find `extends "res://....gd"` bits and convert those to be the class_name from the extended file instead of the filename!!

def process_file(fname):
    if not fname.endswith('.gd'):
        return
    print ('PROCESSING %s' % fname)
    save_backup = False
    try:
        flines = open('../groupxbak/' + fname + '.bak', 'rt', newline='').readlines()
    except:
        flines = open(fname, 'rt', newline='').readlines()
        save_backup = True
    addlines = []
    extendsidx = -1
    if True:
        print ('actually doing %s' % fname)
        for linenum in range(len(flines)):
            fline = flines[linenum]
            nl = fline[len(fline.rstrip()):]
            endlineidx = findcomment(fline)
            endline = fline[endlineidx:]
            fline = fline[:endlineidx]
            if fline.strip() == 'tool':
                addlines.append('@' + fline + endline)
                fline = ''
                endline = ''
            fline = YIELD_PATTERN.sub("await \\1", fline)
            setter = getter = None
            exportfline = fline
            matchres = SETGET_PATTERN.match(fline)
            if matchres:
                exportfline = matchres[1]
                setter = matchres[2]
                getter = matchres[3]
            matchres = EXPORT_PAREN.match(exportfline)
            if matchres:
                whitespace = matchres[1]
                exportstatement = matchres[2]
                typ = matchres[3]
                vardecl = matchres[4]
                typdecl = matchres[5]
                defl = matchres[6]
                print(repr(defl) + "==========")
                fline = whitespace
                if exportstatement:
                    fline += "@" + exportstatement
                fline += vardecl
                if typdecl:
                    fline += typdecl
                    if typ:
                        endline += " # (" + typ + ")"
                elif typ:
                    # What to do if both??
                    fline += ": " + typ + " "
                if defl:
                    fline += defl
                if setter or getter:
                    fline += ":" + nl
                    if setter:
                        fline += "    set = " + setter
                        if getter:
                            fline += "," + nl
                        else:
                            fline += nl
                    if getter:
                        fline += "    get = " + getter + nl
            if 'extends' in fline and extendsidx == -1:
                extendsidx = linenum
            elif fline.startswith('class_name'):
                flines[extendsidx] = fline.strip() + ' ' + flines[extendsidx]
                fline = ''
            for k, v in replacements:
                if k in fline:
                    fline = fline.replace(k, v)
            flines[linenum] = fline + endline
    if save_backup:
        try:
            os.makedirs('../groupxbak/' + os.path.dirname(fname))
        except:
            pass
        os.rename(fname, '../groupxbak/' + fname + '.bak')
    wf = open(fname, 'wt', newline='')
    wf.writelines(addlines)
    wf.writelines(flines)
    wf.close()
        

def process_path(path):
    if not os.path.isdir(path):
        process_file(path)
        return
    for root,d_names,f_names in os.walk(path):
        for f in f_names:
            process_file(root + '/' + f)

if __name__=='__main__':
    for dr in sys.argv[1:]:
        process_path(dr)
