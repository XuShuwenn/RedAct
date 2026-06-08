import * as THREE from 'three';
import { OBJExporter } from 'three/examples/jsm/exporters/OBJExporter.js';
import fs from 'node:fs';
import path from 'node:path';

// Expand InstancedMesh into independent Mesh objects so exporters handle them.
export function expandInstancedMeshes(root) {
  const toAdd = [];
  const toRemove = [];
  const tmpInstance = new THREE.Matrix4();
  const tmpWorld = new THREE.Matrix4();

  root.updateMatrixWorld(true);

  root.traverse((obj) => {
    if (obj.isInstancedMesh) {
      const parent = obj.parent;
      if (!parent) return;
      for (let i = 0; i < obj.count; i++) {
        obj.getMatrixAt(i, tmpInstance);
        tmpWorld.multiplyMatrices(obj.matrixWorld, tmpInstance);
        const geom = obj.geometry.clone();
        const mat = obj.material;
        const mesh = new THREE.Mesh(geom, mat);
        mesh.matrixAutoUpdate = false;
        mesh.matrix.copy(tmpWorld);
        toAdd.push({ parent, mesh });
      }
      toRemove.push(obj);
    }
  });

  // Apply queued changes outside traversal
  for (const { parent, mesh } of toAdd) parent.add(mesh);
  for (const obj of toRemove) obj.removeFromParent();

  root.updateMatrixWorld(true);
}

// Flip triangle winding for indexed geometry (for mirrored transforms)
function flipIndexedWinding(geometry) {
  const index = geometry.index;
  if (!index) return;
  const arr = index.array;
  for (let i = 0; i < arr.length; i += 3) {
    const tmp = arr[i + 1];
    arr[i + 1] = arr[i + 2];
    arr[i + 2] = tmp;
  }
  index.needsUpdate = true;
}

// Bake world transforms into geometry and return a new group of baked meshes
export function bakeWorldTransforms(root) {
  root.updateMatrixWorld(true);
  const bakedRoot = new THREE.Group();
  const world = new THREE.Matrix4();

  root.traverse((obj) => {
    if (obj.isMesh && obj.geometry) {
      const srcGeom = obj.geometry;
      const geom = srcGeom.clone();
      world.copy(obj.matrixWorld);
      const det = world.determinant();
      geom.applyMatrix4(world);
      if (det < 0 && geom.index) flipIndexedWinding(geom);
      if (!geom.attributes.normal) {
        geom.computeVertexNormals();
      }
      const baked = new THREE.Mesh(geom, obj.material);
      baked.name = obj.name || '';
      bakedRoot.add(baked);
    }
  });

  bakedRoot.updateMatrixWorld(true);
  return bakedRoot;
}

// Apply -90 degrees rotation around X to convert to Blender Z-up
export function applyZUpRotationToGeometry(root) {
  const rot = new THREE.Matrix4().makeRotationX(-Math.PI / 2);
  root.traverse((obj) => {
    if (obj.isMesh && obj.geometry) {
      obj.geometry.applyMatrix4(rot);
      // Normals rotate correctly under linear transform; recompute if needed
      if (!obj.geometry.attributes.normal) obj.geometry.computeVertexNormals();
    }
  });
  root.updateMatrixWorld(true);
}

export function exportOBJText(root) {
  const exporter = new OBJExporter();
  // OBJExporter.parse returns a string
  return exporter.parse(root);
}

function ensureDirSync(dirPath) {
  if (!fs.existsSync(dirPath)) fs.mkdirSync(dirPath, { recursive: true });
}

export async function writeOBJToFile(objText, outPath) {
  ensureDirSync(path.dirname(outPath));
  await fs.promises.writeFile(outPath, objText, 'utf8');
}

// Convenience: full pipeline to export any Object3D to an OBJ file
export async function exportSceneToOBJFile(root, outPath) {
  // 1) Expand instanced meshes
  expandInstancedMeshes(root);
  // 2) Bake world transforms
  const baked = bakeWorldTransforms(root);
  // 3) Apply Z-up conversion
  applyZUpRotationToGeometry(baked);
  // 4) Export to OBJ
  const objText = exportOBJText(baked);
  // 5) Write to file
  await writeOBJToFile(objText, outPath);
  return outPath;
}
