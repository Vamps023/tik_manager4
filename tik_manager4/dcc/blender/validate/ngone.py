import bpy

class NgonsValidator:
    """Example validation for Blender"""

    nice_name = "Ngons"

    def __init__(self):
        self.bad_meshes = []

    def collect(self):
        """Collect all meshes in the scene."""
        self.collection = [obj for obj in bpy.data.objects if obj.type == 'MESH']

    def validate(self):
        """Identify the ngons in the scene."""
        self.bad_meshes = []
        self.collect()
        for obj in self.collection:
            if self.has_ngons(obj):
                self.bad_meshes.append(obj)
        if self.bad_meshes:
            self.failed(msg="Ngons found in the following meshes: {}".format(self.bad_meshes))
        else:
            self.passed()

    def select_ngon_faces(self, obj):
        """Select the ngon faces of the given mesh object."""
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        mesh = obj.data
        for poly in mesh.polygons:
            if len(poly.vertices) > 4:  # If polygon has more than 4 vertices, it's an ngon
                for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
                    vert_index = mesh.loops[loop_index].vertex_index
                    mesh.vertices[vert_index].select = True

    def select_other_faces(self, obj):
        """Deselect ngon faces and select other faces of the given mesh object."""
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        self.select_ngon_faces(obj)
        bpy.ops.object.mode_set(mode='EDIT')

    def select(self):
        """Select the bad meshes with ngons."""
        for obj in self.bad_meshes:
            obj.select_set(True)

    def has_ngons(self, obj):
        """Check if the mesh has ngons and returns True if it does."""
        mesh = obj.data
        for poly in mesh.polygons:
            if len(poly.vertices) > 4:  # If polygon has more than 4 vertices, it's an ngon
                return True
        return False

    def failed(self, msg):
        """Print error message to console."""
        super().failed(msg)

    def passed(self):
        """Print success message to console."""
        super().passed()

# Usage
validator = NgonsValidator()
validator.validate()
validator.select()

# Select ngon faces and deselect other faces
for obj in validator.bad_meshes:
    validator.select_other_faces(obj)
