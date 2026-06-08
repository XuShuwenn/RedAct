#!/usr/bin/env node
// Three.js part-level OBJ exporter
// - Identifies parts as named THREE.Group nodes
// - Buckets meshes by nearest named-group ancestor (fallback: 'root')
// - Exports one merged OBJ per part (links)
// - Exports one OBJ per individual mesh per part (part_meshes)

import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import * as THREE from 'three';
import { OBJExporter } from 'three/examples/jsm/exporters/OBJExporter.js';

function parseArgs(argv) {
  const args = {
    input: null,
    func: 'createScene',
    linksOut: './output/links',
    meshesOut: './output/part_meshes',
    includeRoot: false,
  };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--input') args.input = argv[++i];
    else if (a === '--func') args.func = argv[++i];
    else if (a === '--linksOut') args.linksOut = argv[++i];
    else if (a === '--meshesOut') args.meshesOut = argv[++i];
    else if (a === '--includeRoot') {
      const v = argv[++i];
      args.includeRoot = String(v).toLowerCase() === 'true';
    }
  }
  if (!args.input) throw new Error('Missing --input <scene_module_path>');
  return args;
}

function sanitizeName(name, fallbackBase = 'unnamed') {
  const base = (name && String(name).trim()) ? String(name).trim() : fallbackBase;
  // Replace anything not alphanumeric, dash, underscore, or dot
  return base.replace(/[^A-Za-z0-9._-]+/g, '_');
}

async function ensureDir(dir) {
  await fs.mkdir(dir, { recursive: true });
}

function updateWorld(scene) {
  if (scene && scene.updateMatrixWorld) scene.updateMatrixWorld(true);
}

function getNearestNamedGroupAncestor(obj) {
  let p = obj.parent;
  while (p) {
    if (p.isGroup && p.name && p.name.trim()) return p;
    p = p.parent;
  }
  return null;
}

function collectMeshes(scene) {
  const meshes = [];
  scene.traverse((node) => {
    if (node.isMesh && node.geometry) meshes.push(node);
  });
  return meshes;
}

function bakeMesh(mesh) {
  const geom = mesh.geometry.clone();
  geom.applyMatrix4(mesh.matrixWorld);
  const baked = new THREE.Mesh(geom);
  baked.name = mesh.name || '';
  // Identity transform on baked mesh
  baked.position.set(0, 0, 0);
  baked.rotation.set(0, 0, 0);
  baked.scale.set(1, 1, 1);
  baked.updateMatrixWorld(true);
  return baked;
}

function buildPartBuckets(scene, includeRoot) {
  // Map: partKey -> { partName, groupRef (may be null), meshes: [originalMesh] }
  const buckets = new Map();
  const allMeshes = collectMeshes(scene);
  for (const m of allMeshes) {
    const grp = getNearestNamedGroupAncestor(m);
    let partName;
    let groupRef = null;
    if (grp) {
      partName = grp.name;
      groupRef = grp;
    } else {
      partName = 'root';
    }
    // Optionally drop a pure container root group if it shouldn't be a part
    if (!includeRoot && groupRef && groupRef.parent && groupRef.parent.type === 'Scene') {
      // Keep it; decision to exclude only applies to the topmost container group itself, not its children
    }
    if (!buckets.has(partName)) {
      buckets.set(partName, { partName, groupRef, meshes: [] });
    }
    buckets.get(partName).meshes.push(m);
  }

  // Optionally remove a container root group from parts if it has no direct meshes and only child groups
  if (!includeRoot) {
    // Detect a single top-level named group that has no direct meshes, only named groups under it,
    // and whose meshes were categorized under those child groups (i.e., no meshes directly in its bucket)
    // This heuristic avoids exporting a duplicate container link.
    for (const [key, bucket] of buckets) {
      const g = bucket.groupRef;
      if (!g) continue;
      if (g.parent && g.parent.type === 'Scene') {
        const hasDirectMesh = g.children.some((c) => c.isMesh);
        const hasNamedGroupChild = g.children.some((c) => c.isGroup && c.name && c.name.trim());
        if (!hasDirectMesh && hasNamedGroupChild && bucket.meshes.length === 0) {
          buckets.delete(key);
        }
      }
    }
  }

  return buckets;
}

function makeUniqueNamer() {
  const used = new Map(); // key: name -> count
  return (name) => {
    const base = sanitizeName(name || 'mesh');
    const count = used.get(base) || 0;
    used.set(base, count + 1);
    if (count === 0) return base;
    return `${base}_${count + 1}`;
  };
}

async function exportOBJ(object3D, outPath, exporter) {
  const objText = exporter.parse(object3D);
  await fs.writeFile(outPath, objText, 'utf8');
}

async function run() {
  const args = parseArgs(process.argv);
  const inputUrl = pathToFileURL(path.resolve(args.input)).href;

  // Dynamically import the scene module
  const mod = await import(inputUrl);
  let createFn = null;
  if (mod && typeof mod[args.func] === 'function') {
    createFn = mod[args.func];
  } else if (mod && typeof mod.default === 'function' && (args.func === 'default' || args.func === 'createScene')) {
    createFn = mod.default;
  }
  if (!createFn) {
    throw new Error(`Could not find a scene factory function '${args.func}' or default export in ${args.input}`);
  }

  // Build the scene/root
  const result = await createFn();
  let scene;
  if (result && result.isScene) {
    scene = result;
  } else if (result && result.scene && result.scene.isScene) {
    scene = result.scene;
  } else if (result && result.isObject3D) {
    scene = new THREE.Scene();
    scene.add(result);
  } else {
    throw new Error('Scene factory did not return a THREE.Scene or Object3D');
  }

  updateWorld(scene);

  // Build part buckets
  const buckets = buildPartBuckets(scene, args.includeRoot);

  // Prepare output directories
  await ensureDir(args.linksOut);
  await ensureDir(args.meshesOut);

  const exporter = new OBJExporter();

  // Export per part
  for (const { partName, meshes } of buckets.values()) {
    const partSafe = sanitizeName(partName || 'root', 'root');
    const partMeshDir = path.join(args.meshesOut, partSafe);
    await ensureDir(partMeshDir);

    // Per-mesh exports with baked transforms
    const uniqueName = makeUniqueNamer();
    for (const m of meshes) {
      const baked = bakeMesh(m);
      const meshName = m.name && m.name.trim() ? m.name : 'mesh';
      const outName = uniqueName(meshName) + '.obj';
      const outPath = path.join(partMeshDir, outName);
      await exportOBJ(baked, outPath, exporter);
    }

    // Per-part (link) export: aggregate baked meshes into a temporary group
    const tempGroup = new THREE.Group();
    tempGroup.name = partSafe;
    for (const m of meshes) {
      tempGroup.add(bakeMesh(m));
    }
    const linkPath = path.join(args.linksOut, partSafe + '.obj');
    await exportOBJ(tempGroup, linkPath, exporter);
  }

  // Simple summary
  console.log(`Exported ${buckets.size} parts to:`);
  console.log(`  links: ${path.resolve(args.linksOut)}`);
  console.log(`  part_meshes: ${path.resolve(args.meshesOut)}`);
}

run().catch((err) => {
  console.error('Export failed:', err);
  process.exit(1);
});
