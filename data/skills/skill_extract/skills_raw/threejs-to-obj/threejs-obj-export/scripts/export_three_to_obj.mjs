#!/usr/bin/env node
/**
 * Three.js -> OBJ exporter (Blender Z-up ready)
 *
 * Usage examples:
 *   node scripts/export_three_to_obj.mjs --entry ./data/object.js --factory createScene --out ./output/object.obj
 *   node scripts/export_three_to_obj.mjs --entry ./scene-module.mjs --out ./model.obj
 *   node scripts/export_three_to_obj.mjs --entry ./object.js --out ./model.obj --no-z-up
 *
 * Notes:
 * - Requires: three, three/examples/jsm/exporters/OBJExporter.js
 * - This script runs headless in Node (no renderer needed).
 */

import * as fs from 'fs';
import * as path from 'path';
import { pathToFileURL } from 'url';
import * as THREE from 'three';
import { OBJExporter } from 'three/examples/jsm/exporters/OBJExporter.js';

function parseArgs(argv) {
  const args = {};
  let key = null;
  for (const token of argv) {
    if (token.startsWith('--')) {
      key = token.replace(/^--/, '');
      if (key === 'no-z-up') {
        args['z-up'] = false;
        key = null;
      } else {
        args[key] = true; // provisional; may be overwritten by next token
      }
    } else if (key) {
      args[key] = token;
      key = null;
    }
  }
  if (!('z-up' in args)) args['z-up'] = true;
  return args;
}

async function loadRootObject(entryPath, factoryName) {
  const absPath = path.resolve(entryPath);
  const mod = await import(pathToFileURL(absPath).href);

  // Candidate strategies to obtain the root Object3D
  const candidates = [];
  if (factoryName && typeof mod[factoryName] === 'function') {
    candidates.push(() => mod[factoryName]());
  }
  const commonFactories = ['createScene', 'buildScene', 'makeScene', 'getScene'];
  for (const name of commonFactories) {
    if (!factoryName && typeof mod[name] === 'function') {
      candidates.push(() => mod[name]());
    }
  }
  if (mod.scene) candidates.push(() => mod.scene);
  if (typeof mod.default === 'function') candidates.push(() => mod.default());
  if (mod.default && typeof mod.default === 'object') candidates.push(() => mod.default);

  for (const get of candidates) {
    try {
      const v = await get();
      if (v && v instanceof THREE.Object3D) return v;
    } catch (_) {
      // try next candidate
    }
  }
  throw new Error('Could not obtain a THREE.Object3D from the module. Provide a --factory that returns an Object3D or export a `scene`.');
}

function bakeMeshGeometry(mesh, worldMatrix) {
  const srcGeom = mesh.geometry;
  if (!srcGeom || !srcGeom.isBufferGeometry) return null;
  const geom = srcGeom.clone();
  geom.applyMatrix4(worldMatrix);
  // Ensure normals exist (or are corrected after transforms)
  const hasNormals = !!geom.getAttribute('normal');
  if (!hasNormals) {
    geom.computeVertexNormals();
  }
  return geom;
}

function buildExportGroup(root, applyZUpRotation = true) {
  // Compute Blender conversion matrix: -90° rotation around X
  const blenderRot = new THREE.Matrix4();
  if (applyZUpRotation) {
    blenderRot.makeRotationX(-Math.PI / 2);
  } else {
    blenderRot.identity();
  }

  root.updateMatrixWorld(true);

  const exportGroup = new THREE.Group();
  const tmp = new THREE.Matrix4();
  const instanceMatrix = new THREE.Matrix4();

  root.traverse((obj) => {
    if (obj instanceof THREE.InstancedMesh) {
      const baseWorld = obj.matrixWorld.clone();
      for (let i = 0; i < obj.count; i++) {
        obj.getMatrixAt(i, instanceMatrix);
        // combined = blenderRot * baseWorld * instanceMatrix
        tmp.copy(baseWorld).multiply(instanceMatrix);
        tmp.premultiply(blenderRot);

        const geom = bakeMeshGeometry(obj, tmp);
        if (!geom) continue;

        const m = new THREE.Mesh(geom, obj.material);
        m.name = obj.name ? `${obj.name}_${i}` : `instance_${i}`;
        // geometry is already in world (and Z-up) space; keep identity transform
        exportGroup.add(m);
      }
    } else if (obj instanceof THREE.Mesh) {
      const world = obj.matrixWorld.clone();
      // combined = blenderRot * world
      world.premultiply(blenderRot);

      const geom = bakeMeshGeometry(obj, world);
      if (!geom) return;

      const m = new THREE.Mesh(geom, obj.material);
      m.name = obj.name || 'mesh';
      exportGroup.add(m);
    }
  });

  return exportGroup;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!args.entry || !args.out) {
    console.error('Usage: node export_three_to_obj.mjs --entry <module> [--factory <name>] --out <file.obj> [--no-z-up]');
    process.exit(1);
  }

  try {
    const root = await loadRootObject(args.entry, args.factory);
    const exportRoot = buildExportGroup(root, args['z-up']);

    const exporter = new OBJExporter();
    const objData = exporter.parse(exportRoot);

    const outPath = path.resolve(args.out);
    fs.mkdirSync(path.dirname(outPath), { recursive: true });
    fs.writeFileSync(outPath, objData, 'utf8');

    const vCount = (objData.match(/^v\s/gm) || []).length;
    const fCount = (objData.match(/^f\s/gm) || []).length;
    const oCount = (objData.match(/^o\s/gm) || []).length;

    console.log(`✓ Exported OBJ: ${outPath}`);
    console.log(`  Z-up conversion: ${args['z-up'] ? 'applied (-90° X)' : 'skipped'}`);
    console.log(`  Objects: ${oCount}, Vertices: ${vCount}, Faces: ${fCount}`);
  } catch (err) {
    console.error('Export failed:', err.message || err);
    process.exit(1);
  }
}

main();
