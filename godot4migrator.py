import os
import sys
import re

replacements = [
    ('addons/gdutil/', 'addons/gd_util/'),
    (re.compile(r'\bget_node(\s+)\((\s+)\@'), r'get_node\1(\2^'),
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
    ('Particles', 'GPUParticles3D'),
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
    (re.compile(r'\bfunc(\s+)_init(\s*)\(([^)]*)\)[^:]*:'), r'func\1_init\2(\3):'),
    (re.compile(r'\bfunc(\s+)handles\b'), r'func\1_handles', ['EditorPlugin']),
    (re.compile(r'\bfunc(\s+)get_name\b'), r'func\1_get_plugin_name', ['EditorPlugin']),
    (re.compile(r'\bfunc(\s+)edit\b'), r'func\1_edit', ['EditorPlugin']),
    (re.compile(r'\bfunc(\s+)make_visible\b'), r'func\1_make_visible', ['EditorPlugin']),
    (re.compile(r"\byield *\((.*?)(\s*,\s*)*[\"'](.*)[\"']\)\s*$"), "await \\1.\\3"),
    (re.compile(r"\byield *\((.*?)\)\s*$|\byield (.*)$"), "await \\1\\2"),
    (re.compile(r"\b(connect|disconnect|is_connected)(\s*)\((\s*)([^,]*),(\s*)([^,]*),([^,]*)([,)])"), r"\1\2(\3\4,\5Callable(\6,\7)\8"),
    ('FuncRef\\.new', 'Callable'),
    ('FuncRef', 'Callable'),
    ('funcref', 'Callable'),
    ('call_func', 'call'),
    ('TYPE_REAL', 'TYPE_FLOAT'),
    ('TYPE_QUAT', 'TYPE_QUATERNION'),
	('NavigationServer', 'NavigationServer3D'),
	('Navigation2DServer', 'NavigationServer2D'),
	('Path', 'Path3D'),
	('PhysicsServer', 'PhysicsServer3D'),
	('PhysicsDirectBodyState', 'PhysicsDirectBodyState3D'),
	('PhysicsDirectSpaceState', 'PhysicsDirectSpaceState3D'),
	('PhysicsShapeQueryParameters', 'PhysicsShapeQueryParameters3D'),
	('PhysicsShapeQueryResult', 'PhysicsShapeQueryResult3D'),
	(re.compile(r'\bARVR'), 'XR'),
    (re.compile('(\s+)\.'), '\\1super.'), ## Questionable.
    ('make_convex_from_brothers', 'make_convex_from_siblings'),
    ('rand_range', 'randf_range'),
    ('stepify', 'snapped'),
    ('track_remove_key_at_position', 'track_remove_key_at_time'),
    ('translation', 'position'),
	('onready', '@onready'),
	('AnimatedTexture2D', 'AnimatedTexture'),
	('AnimationTreePlayer', 'AnimationTree'),
	('Area', 'Area3D'),
	('AtlasTexture2D', 'AtlasTexture'),
	('BakedLightmap', 'LightmapGI'),
	('BitmapFont', 'Font'),
	('Bone', 'Bone3D'),
	('BoxShape', 'BoxShape3D'),
	('BulletPhysicsDirectBodyState', 'BulletPhysicsDirectBodyState3D'),
	('BulletPhysicsServer', 'BulletPhysicsServer3D'),
	('ButtonList', 'MouseButton'),
	('CSGBox', 'CSGBox3D'),
	('CSGCombiner', 'CSGCombiner3D'),
	('CSGCylinder', 'CSGCylinder3D'),
	('CSGMesh', 'CSGMesh3D'),
	('CSGPolygon', 'CSGPolygon3D'),
	('CSGSphere', 'CSGSphere3D'),
	('CSGTorus', 'CSGTorus3D'),
	('CollisionObject', 'CollisionObject3D'),
	('CollisionPolygon', 'CollisionPolygon3D'),
	('CollisionShape', 'CollisionShape3D'),
	('ConcavePolygonShape', 'ConcavePolygonShape3D'),
	('ConvexPolygonShape', 'ConvexPolygonShape3D'),
	('CubeMesh', 'BoxMesh'),
	('CylinderShape', 'CylinderShape3D'),
	('DynamicFont', 'Font'),
	('EditorSpatialGizmo', 'EditorNode3DGizmo'),
	('GIProbe', 'VoxelGI'),
	('HeightMapShape', 'HeightMapShape3D'),
	('ImmediateGeometry', 'ImmediateGeometry3D'),
	('IP_Unix', 'IPUnix'),
	('Joint', 'Joint3D'),
	('KinematicCollision', 'KinematicCollision3D'),
	('Navigation2D', 'Node2D'),
	('Navigation3D', 'Node3D'),
	('NavigationAgent', 'NavigationAgent3D'),
	('NavigationMeshInstance3D', 'NavigationRegion3D'),
	('NavigationObstacle', 'NavigationObstacle3D'),
	('NavigationPolygonInstance', 'NavigationRegion3D'),
	('NoiseTexture2D', 'NoiseTexture'),
	('PathFollow', 'PathFollow3D'),
	('PAUSE_MODE_INHERIT', 'PROCESS_MODE_INHERIT'),
	('PAUSE_MODE_STOP', 'PROCESS_MODE_PAUSABLE'),
	('PAUSE_MODE_PROCESS', 'PROCESS_MODE_ALWAYS'),
	('Physics2DDirectBodyStateSW', 'PhysicsDirectBodyState2DSW'),
	('Physics2DDirectBodyState', 'PhysicsDirectBodyState2D'),
	('Physics2DDirectSpaceState', 'PhysicsDirectSpaceState2D'),
	('Physics2DServer', 'PhysicsServer2D'),
	('Physics2DShapeQueryParameters', 'PhysicsShapeQueryParameters2D'),
	('Physics2DShapeQueryResult', 'PhysicsShapeQueryResult2D'),
	('Physics2DTestMotionResult', 'PhysicsTestMotionResult2D'),
	('PhysicsBody', 'PhysicsBody3D'),
	('ProceduralSky', 'Sky'),
	('ProximityGroup', 'ProximityGroup3D'),
	('RemoteTransform', 'RemoteTransform3D'),
	('ShortCut', 'Shortcut'),
	('SoftBody', 'SoftBody3D'),
	('SpatialVelocityTracker', 'VelocityTracker3D'),
	('SphereShape', 'SphereShape3D'),
	('StaticBody', 'StaticBody3D'),
	('TCP_Server', 'TCPServer'),
	('ToolButton', 'Button'),
	('VehicleBody', 'VehicleBody3D'),
	('VehicleWheel', 'VehicleWheel3D'),
	('Viewport', 'SubViewport'),
	('SubViewportTexture2D', 'ViewportTexture'),
	('VisibilityEnabler', 'VisibilityEnabler3D'),
	('VisibilityNotifier', 'VisibilityNotifier3D'),
	('VisualServer', 'RenderingServer'),
	('XRAnchor', 'XRAnchor3D'),
	('XRController', 'XRController3D'),
	('XROrigin', 'XROrigin3D'),
	('YSort', 'Node2D'),
	('as_normalmap', 'as_normal_map'),
	('button_release', 'button_released'),
	('doubleclick', 'double_click'),
	('pause_mode = 2', 'process_mode = 3'),
	('pause_mode', 'process_mode'),
	('tab_close', 'tab_closed'),
	('tab_hover', 'tab_hovered'),
	('toplevel', 'top_level'),
	('zfar', 'far'),
	('znear', 'near'),
    ('invert', 'reverse'), # PackedByteArray and so on
    (re.compile(r'\b(master|remote|remotesync|puppet)(\s*)func\b'), '@\\1\\2func'),
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

SPECIAL_PATTERN = re.compile("[\'\"\\\\\\[\\]\\(\\)\\{\\}#]")

EXPORT_PAREN = re.compile(r"^( *)(\bexport *)?(?:\(([^)]*)\))?( *var *[^=:]*)(: [^ =]*)?( *=[\s\S]*)?")
SETGET_PATTERN = re.compile(r"([\s\S]*)\bsetget\s*([^,]*)(?:,\s*)?([\s\S]*)")
EXTENDS_REGEX = re.compile(r"^(\bextends\b)(\s+)")


ENUM_PATTERN = re.compile(r"(\s*)\benum([^{]+){\s+([^}]*)\s+}")
DOCSTRING_PATTERN1 = re.compile(r'(\s*)"""([\s\S]*)"""')
DOCSTRING_PATTERN2 = re.compile(r"(\s*)'''([\s\S]*)'''")

'''
OLD:
export(Color) var bottom_left_color = Color() setget _set_bottom_left_color
NEW:
@export var bottom_left_color : Color = Color():
\tset = _set_bottom_left_color
'''


# FIXME: We need to find `extends "res://....gd"` bits and convert those to be the class_name from the extended file instead of the filename!!

OUTPUT_DIR = "../gd4out"

def string_enc(s):
    return SPECIAL_PATTERN.sub(lambda m: (chr(0xef00 | ord(m.group())) if ord(m.group()) <= 0xff else m.group()), s)
    #print("Do %s to %s" % (s, SPECIAL_PATTERN.sub('X', s)))
    #return SPECIAL_PATTERN.sub('X', s)

def comment_enc(s):
    return ''.join((chr(0xef00 + ord(c)) if ord(c) <= 0xff else c) for c in s)

def special_dec(s):
    return ''.join((chr(0xff & ord(c)) if 0xef00 <= ord(c) <= 0xefff else c) for c in s)

def group_lines(flines):
    outlines = []
    cur_line = ''
    nesting_levels = []
    idx = 0
    for xxline in flines:
        #print(nesting_levels)
        line = xxline
        do_continue = False
        qpos = 0
        if nesting_levels and (nesting_levels[-1] == '"' or nesting_levels[-1] == "'"):
            while True:
                endq = line.find(nesting_levels[-1], qpos)
                if endq == -1:
                    line = string_enc(line)
                    do_continue = True
                    break
                qpos = endq + 1
                bslashcnt = 0
                while endq > 0 and line[endq - 1] == '\\':
                    bslashcnt += 1
                    endq -= 1
                if bslashcnt % 2 == 0:
                    line = string_enc(line[:qpos - 1]) + line[qpos - 1:]
                    nesting_levels.pop()
                    break

        while not do_continue:
            next_sym_res = SPECIAL_PATTERN.search(line[idx:], qpos)
            if next_sym_res == None:
                break
            next_sym = next_sym_res[0]
            qpos = next_sym_res.end()
            #print("Found next_sym=" + str(next_sym))
            if next_sym == '#':
                line = line[:qpos] + comment_enc(line[qpos:-1]) + line[-1:]
                break
            if next_sym == '"' or next_sym == "'":
                while True:
                    endq = line.find(next_sym, qpos)
                    if endq == -1:
                        nesting_levels.append(next_sym)
                        line = line[:next_sym_res.end()] + string_enc(line[next_sym_res.end():])
                        #print("Continue: " + str(line))
                        do_continue = True
                        break
                    qpos = endq + 1
                    bslashcnt = 0
                    while endq > 0 and line[endq - 1] == '\\':
                        bslashcnt += 1
                        endq -= 1
                    if bslashcnt % 2 == 0:
                        line = line[:next_sym_res.end()] + string_enc(line[next_sym_res.end():qpos - 1]) + line[qpos - 1:]
                        #print("Break: %s %d %d %d" % (line, next_sym_res.end() + 1, qpos - 1, len(line)))
                        break
                if do_continue:
                    break
            if next_sym == '[' or next_sym == '(' or next_sym == '{':
                nesting_levels.append(next_sym)
            if next_sym == ']':
                assert nesting_levels[-1] == '['
                nesting_levels.pop()
            if next_sym == ')':
                assert nesting_levels[-1] == '('
                nesting_levels.pop()
            if next_sym == '}':
                assert nesting_levels[-1] == '{'
                nesting_levels.pop()
            if next_sym == '\\' and next_sym_res.end() == len(line) - idx - 1:
                # print("%d %d" % (next_sym_res.end(), len(line) - idx))
                do_continue = True
                break
        if do_continue or nesting_levels:
            cur_line += line
        else:
            outlines.append(cur_line + line)
            cur_line = ''
    #print(outlines)
    if cur_line or nesting_levels:
        print(repr(cur_line))
        print(nesting_levels)
    if cur_line:
        outlines.append(cur_line)
    return outlines

def process_lines(fname, flines):
    flines = group_lines(flines)
    addlines = []
    extendsidx = -1
    docstringid = 0
    extends_class = ''
    for linenum in range(len(flines)):
        fline = flines[linenum]
        nl = fline[len(fline.rstrip()):]
        endlineidx = findcomment(fline)
        endline = fline[endlineidx:]
        fline = fline[:endlineidx]
        if fline.strip().startswith('tool'):
            addlines.append('@' + fline + endline)
            fline = ''
            endline = ''
        setter = getter = None
        exportfline = fline
        matchres = SETGET_PATTERN.match(fline)
        if matchres:
            exportfline = matchres[1]
            setter = matchres[2].strip()
            getter = matchres[3].strip()
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
                    fline += " # (" + typ + ")"
            elif typ:
                # What to do if both??
                fline += ": " + typ + " "
            if defl:
                fline += defl
            if setter or getter:
                fline += ":" + nl
                if setter:
                    fline += "\tset = " + setter
                    if getter:
                        fline += "," + nl
                    else:
                        fline += nl
                if getter:
                    fline += "\tget = " + getter + nl
        dstringres = DOCSTRING_PATTERN1.match(fline)
        if dstringres == None:
            dstringres = DOCSTRING_PATTERN2.match(fline)
        if dstringres != None:
            fline = fline[:dstringres.end(1)] + ("const DOCSTRING%d = " % (docstringid)) + fline[dstringres.end(1):]
            docstringid += 1
            fline = ("\n" + dstringres[2]).replace("\n", "\n" + dstringres[1] + "## ")[1:]
        enumres = ENUM_PATTERN.search(fline)
        #print(fline + "************" )
        if enumres != None:
            enumstart = enumres.start(3)
            enumend = enumres.end(3) - 1
            enum_contents = enumres[3].split(',')
            lastval = -1
            new_enum_values = enumres[1] + "class " + enumres[2].replace('\\', '').replace('\n', '') + ":\n"
            extraindent = '\t'
            #print("res 2: "+  enumres[2])
            if not enumres[2].strip():
                new_enum_values = ''
                extraindent = ''
            for enumitem in enum_contents:
                #commentidx = enumitem.find("#")
                #endcommentidx = enumitem.find("\n", commentidx)
                #enumcommentbegin = ''
                #if commentidx != -1:
                #    enumcommentbegin = enumitem[commentidx:endcommentidx]
                #enumcommentend = ''
                enumval = 0
                enumline = ''
                if not enumitem.strip():
                    continue
                if '=' in enumitem:
                    enumitem, enumvalstr = enumitem.split('=', 1)
                    commentidx = enumvalstr.find("#")
                    if commentidx != -1:
                        enumval = int(enumvalstr[:commentidx])
                        extracomment = enumvalstr[commentidx:]
                    else:
                        enumval = int(enumvalstr)
                    firstnl = enumitem.rfind("\n")
                    if firstnl == -1:
                        firstnl = 0
                    beginidx = firstnl + (len(enumitem) - len(enumitem.lstrip()))
                    #print(enumitem[beginidx:])
                    enumline = enumitem[:firstnl] + enumres[1] + extraindent + "const " + enumitem[beginidx:] + "=" + enumvalstr + nl
                    #print("%s %s %s %s %s %s" % (enumitem[:firstnl + 1], enumres[1], extraindent, "const ", enumitem[beginidx:],  enumvalstr + nl))
                    #print(enumitem)
                else:
                    firstnl = enumitem.rfind("\n")
                    if firstnl == -1:
                        firstnl = 0
                    enumval = lastval + 1
                    beginidx = firstnl + (len(enumitem) - len(enumitem.lstrip()))
                    #print("nohas= %d" % beginidx)
                    #print(enumitem[beginidx:])
                    enumline = enumres[1] + extraindent + "const " + enumitem[beginidx:] + "=" + str(enumval) + nl
                lastval = enumval
                new_enum_values += enumline
            #new_enum_values += fline[enumend + 2:]
            #print("replacing enum %s with %s" % (fline, new_enum_values))
            fline = new_enum_values
        extendsmatch = EXTENDS_REGEX.match(fline)
        if extendsmatch != None and extendsidx == -1:
            extends_off = extendsmatch.start(1)
            if fname:
                qoff = fline.find('"', extends_off)
                if qoff == -1:
                    qoff = fline.find("\'", extends_off)
                if qoff != -1:
                    qend = fline.find(fline[qoff], qoff + 1)
                    includefn = special_dec(fline[qoff + 1: qend])
                    if not includefn.startswith("res:"):
                        includefn = "res://" + os.path.dirname(fname).replace("\\", "/") + "/" + includefn
                        print("Changing %s to %s" % (fline, fline[:qoff + 1] + includefn + fline[qend:]))
                        fline = fline[:qoff + 1] + includefn + fline[qend:] + " # " + fline[qoff + 1: qend]
            extendsidx = linenum
            extends_class = fline[fline.find('extends') + 7:].strip()
        elif fline.startswith('class_name'):
            flines[extendsidx] = fline.strip() + ' ' + flines[extendsidx]
            fline = ''
        for k, v, classes, is_special in replacement_re:
            if not classes or extends_class in classes:
                fline = k.sub(v, fline)
        flines[linenum] = fline + endline
    for i in range(len(addlines)):
        addlines[i] = special_dec(addlines[i])
    for i in range(len(flines)):
        flines[i] = special_dec(flines[i])
    return addlines + flines

def process_file(fname):
    if not fname.endswith('.gd'):
        return
    try:
        os.makedirs(OUTPUT_DIR + '/' + os.path.dirname(fname))
    except:
        pass
    print ('PROCESSING %s' % fname)
    flines = [l for l in open(fname, 'rt', newline='').readlines()]
    print ('actually doing %s' % fname)
    flines = process_lines(fname, flines)
    wf = open(OUTPUT_DIR + "/" + fname, 'wt', newline='')
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
        flines = process_lines('', flines)
        sys.stdout.writelines(flines)
