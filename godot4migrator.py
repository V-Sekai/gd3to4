import os
import sys
import re

replacements = [
    ('Transform', 'Transform3D'),
    ('Reference', 'RefCounted'),
    ('Quat', 'Quaternion'),
    ('Spatial', 'Node3D'),
    ('Sprite', 'Sprite2D'),
    ('Camera', 'Camera3D'),
    ('Skeleton', 'Skeleton3D'),
    ('Texture', 'Texture2D'),
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
    ('is_valid_integer', 'is_valid_int'),
    ('SpringArm', 'SpringArm3D'),
    ('Shape', 'Shape3D'),
    ('Particles', 'Particles3D'),
    ('World', 'World3D'),
    ('linear_interpolate', 'lerp'),
    ('empty', 'is_empty'),
    ('get_rotation_quat', 'get_rotation_quaternion'),
    ('PoolByteArray', 'PackedByteArray'),
    ('PoolIntArray', 'PackedInt64Array'), # FIXME: 64?
    ('PoolRealArray', 'PackedFloat32Array'), # FIXME: 64?
    ('PoolStringArray', 'PackedStringArray'),
    ('PoolVector2Array', 'PackedVector2Array'),
    ('PoolVector3Array', 'PackedVector3Array'),
    ('PoolColorArray', 'PackedColorArray'),
    (re.compile(r'([\w.]+)\s*\.\s*xform_inv\s*([^)]*)'), r'((\2) * (\1))'),
    ('\\.xform', '*'),
    ('SpatialMaterial', 'StandardMaterial3D'),
    ('Node3DMaterial', 'StandardMaterial3D'), # Due to previous runs of the conversion tool.
    ('instance', 'instantiate'),
    ('BoneAttachment', 'BoneAttachment3D'),
    ('MODE_SAVE_FILE', 'FILE_MODE_SAVE_FILE'),
    ('MODE_OPEN_FILE', 'FILE_MODE_OPEN_FILE'),
    ('MODE_OPEN_FILES', 'FILE_MODE_OPEN_FILE'),
    ('MODE_OPEN_DIR', 'FILE_MODE_OPEN_DIR'),
    ('MODE_OPEN_ANY', 'FILE_MODE_OPEN_ANY'),
    ('get_editor_viewport', 'get_viewport'),
    ('get_icon', 'get_theme_icon'),
    ('popup_centered_minsize', 'popup_centered_clamped'),
    (re.compile(r'\bfunc(\s+)_init(\s*)\((\s*)\)[^:]*:'), r'func\1_init\2(\3):'),
    (re.compile(r'\bfunc(\s+)handles\b'), r'func\1_handles', ['EditorPlugin']),
    (re.compile(r'\bfunc(\s+)get_name\b'), r'func\1_get_plugin_name', ['EditorPlugin']),
    (re.compile(r'\bfunc(\s+)edit\b'), r'func\1_edit', ['EditorPlugin']),
    (re.compile(r'\bfunc(\s+)make_visible\b'), r'func\1_make_visible', ['EditorPlugin']),
    ]


re_type = type(re.compile('_'))
replacement_re = [
    (re.compile("\\b" + replacements[i][0] + "\\b") if type(replacements[i][0]) != re_type else replacements[i][0], replacements[i][1], replacements[i][2] if len(replacements[i]) > 2 else [], type(replacements[i][0]) == re_type)
    for i in range(len(replacements))]

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

OUTPUT_DIR = "../gd4out"

def process_lines(flines, addlines):
    extendsidx = -1
    extends_class = ''
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
            # print(repr(defl) + "==========", file=sys.stderr)
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
            extends_class = fline[fline.find('extends') + 7:].strip()
        elif fline.startswith('class_name'):
            flines[extendsidx] = fline.strip() + ' ' + flines[extendsidx]
            fline = ''
        for k, v, classes, is_special in replacement_re:
            if not classes or extends_class in classes:
                fline = k.sub(v, fline)
        flines[linenum] = fline + endline


def process_file(fname):
    if not fname.endswith('.gd'):
        return
    try:
        os.makedirs(OUTPUT_DIR + '/' + os.path.dirname(fname))
    except:
        pass
    print ('PROCESSING %s' % fname)
    flines = open(fname, 'rt', newline='').readlines()
    addlines = []
    print ('actually doing %s' % fname)
    process_lines(flines, addlines)
    wf = open(OUTPUT_DIR + "/" + fname, 'wt', newline='')
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
    if len(sys.argv) <= 1:
        flines = sys.stdin.readlines()
        addlines = []
        process_lines(flines, addlines)
        sys.stdout.writelines(addlines)
        sys.stdout.writelines(flines)
