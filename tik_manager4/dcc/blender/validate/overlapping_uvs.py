import bpy

class OverlappingUvs:
    """Example validation for Blender"""

    nice_name = "Overlapping UVs"

    def __init__(self):
        self.autofixable = False
        self.ignorable = True
        self.selectable = True

        self.failed_meshes = []
        self.overlaps = []

    def collect(self):
        """Collect all meshes in the scene."""
        self.collection = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']

    def validate(self):
        """Validate."""
        self.failed_meshes = []
        self.overlaps = []
        self.collect()
        for obj in self.collection:
            if obj.data.uv_layers.active:
                overlaps = self.get_overlapping_uvs(obj)
                if overlaps:
                    self.failed_meshes.append(obj)
                    self.overlaps.extend(overlaps)
        if self.failed_meshes:
            self.failed(msg=f"Overlapping UVs found on meshes: {self.failed_meshes}")
        else:
            self.passed()

    def select(self):
        """Selects objects with overlapping UVs."""
        bpy.ops.object.mode_set(mode='OBJECT')  # Ensure we're in Object Mode
        bpy.ops.object.select_all(action='DESELECT')  # Deselect all objects
        for obj in self.failed_meshes:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = self.failed_meshes[0] if self.failed_meshes else None

    def get_overlapping_uvs(self, obj):
        """Checks the mesh for overlapping UVs and returns the count."""
        overlaps = []
        uv_data = obj.data.uv_layers.active.data
        if uv_data:
            for poly in obj.data.polygons:
                for loop_index in poly.loop_indices:
                    if loop_index != poly.loop_indices[0] and (uv_data[loop_index].uv == uv_data[loop_index - 1].uv):
                        overlaps.append(loop_index)
        return overlaps

    def failed(self, msg):
        """Handle validation failure."""
        print("Validation failed:", msg)

    def passed(self):
        """Handle validation success."""
        print("Validation passed.")

# Example usage:
overlapping_uv_validator = OverlappingUvs()
overlapping_uv_validator.validate()
overlapping_uv_validator.select()
