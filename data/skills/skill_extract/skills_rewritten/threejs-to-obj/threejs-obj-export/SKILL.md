---
name: threejs-obj-export
description: "Export Three.js scenes to Blender-ready OBJ with baked transforms, instanced mesh expansion, and Z-up conversion."
---

# Three.js to OBJ (Blender Z-up) Export

Reusable workflow to convert a Three.js scene/object into a Blender-importable OBJ file while preserving original world-space positions. Handles instanced meshes, nested transforms, and applies the required -90° X rotation to switch from Three.js (Y-up) to Blender (Z-up).

## When to Use

Use this skill when you need to:
- Export a Three.js scene or object to OBJ for import into Blender or other DCC tools
- Preserve world-space positions across nested transforms
- Expand InstancedMesh so repeated geometry is included in the OBJ
- Convert coordinate systems to Blender Z-up by applying a -90° X rotation

## Core Workflow

1. Inspect the source object
   - Identify how the scene/object is provided (exported Object3D, factory function, or module that builds the scene).
   - Confirm any required dependencies (e.g., three) and module format (ESM vs CJS).

2. Prepare the environment
   - Ensure Node.js is available.
   - Install three (npm i three).
   - Use ES modules to import the Three.js OBJExporter (add "type": "module" to package.json or use .mjs files).

3. Load or construct the scene
   - Import the source module and obtain the root THREE.Object3D (a Scene or group/object).
   - Call updateMatrixWorld(true) after the scene is fully constructed.

4. Expand InstancedMesh
   - OBJExporter does not export InstancedMesh directly. Replace each InstancedMesh with per-instance Mesh clones.
   - For each instance, multiply the instance matrix by the mesh's matrixWorld to get the correct world transform.

5. Bake world transforms into geometry
   - For each mesh:
     - Clone its BufferGeometry.
     - Apply the mesh.matrixWorld to the geometry so vertex positions reflect world space.
     - If the world matrix has a negative determinant (mirror), flip triangle winding for indexed geometry to preserve face orientation.
     - Recompute normals if absent or after heavy transforms.
   - Build a new group of baked meshes with identity transforms.

6. Convert to Blender Z-up
   - Apply a -90° rotation around X to all baked geometries.
   - This maps (x, y, z) in Three.js to (x, z, -y) in Blender.

7. Export to OBJ
   - Use OBJExporter from three/examples/jsm/exporters/OBJExporter.js to generate the OBJ text from the baked, Z-up-converted group.
   - Write the OBJ text to the desired output path. Ensure the output directory exists.

8. Validate the result
   - Confirm the file exists and is non-empty.
   - Check that vertex (v) and face (f) lines are present.
   - Optionally list object groups (lines starting with "o ").
   - Spot-check coordinates or orientation if you have a known reference direction.

## Verification

Perform these checks after export:
- File presence and size
  - Ensure the OBJ file exists and is larger than a minimal threshold (e.g., >1 KB).
- Structural checks
  - Count lines beginning with "v " (vertices) and "f " (faces). Both should be non-zero.
  - Optionally, list object declarations with lines beginning with "o ".
- Orientation sanity check
  - If a part was originally aligned with +Y in Three.js, verify it now aligns with +Z in Blender coordinates. The -90° X rotation implies (x, y, z) → (x, z, -y).
- Visual import check
  - Import into Blender and confirm expected orientation and positions.

## Common Pitfalls

- Missing InstancedMesh expansion
  - Symptom: Repeated geometry (instances) is absent in the OBJ.
  - Fix: Expand InstancedMesh into individual Mesh objects by cloning geometry per instance and applying each instance's world transform.

- Not calling updateMatrixWorld
  - Symptom: Baked vertices do not reflect nested transforms.
  - Fix: Always call root.updateMatrixWorld(true) before baking or reading matrices.

- Wrong axis conversion or double rotation
  - Symptom: Model appears tilted incorrectly in Blender.
  - Fix: Apply exactly one -90° X rotation to the baked geometry (or to a wrapper group before baking, but not both). Validate with a known axis reference.

- ESM vs CJS import errors
  - Symptom: Import of OBJExporter fails in Node.
  - Fix: Use ES modules (set package.json { "type": "module" } or .mjs extensions) and import OBJExporter from 'three/examples/jsm/exporters/OBJExporter.js'.

- Mirrored transforms flipping normals
  - Symptom: Surfaces appear inside-out or lighting is inverted.
  - Fix: If matrixWorld.determinant() < 0, flip triangle winding for indexed geometry after applying the world matrix.

- Output path issues
  - Symptom: Export silently fails or writes to an unexpected location.
  - Fix: Ensure the output directory exists and handle filesystem errors.

## Optional Script Usage

This skill includes a helper module to streamline instanced expansion, baking, Z-up rotation, and OBJ export. You can import it into your export script.

Example usage outline:
- Import the scene/object you want to export.
- Use the helper to export an OBJ string and write it to disk.

Example (pseudocode outline):
- import * as THREE from 'three'
- import { exportSceneToOBJFile } from './scripts/three_obj_exporter.mjs'
- const root = await loadOrBuildYourScene()
- await exportSceneToOBJFile(root, './output/object.obj')

Success criteria:
- The OBJ contains all expected mesh parts with correct vertex/face counts.
- The model imports into Blender upright (Z-up) and matches original world-space arrangement.
