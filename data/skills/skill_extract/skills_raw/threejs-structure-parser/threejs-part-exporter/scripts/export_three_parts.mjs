import * as fs from 'fs';
import * as path from 'path';
import { pathToFileURL, fileURLToPath } from 'url';
import * as THREE from 'three';
import { OBJExporter } from 'three/examples/jsm/exporters/OBJExporter.js';

function parseArgs(argv) {
  const args = { scene: null, fn: 'createScene', out: './output', includeRoot: false };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    const n = argv[i + 1];
    if (a === '--scene') { args.scene = n; i++; }
    else if (a === '--fn') { args.fn = n; i++; }
    else if (a === '--out') { args.out = n; i++; }
    else if (a === '--include-root') { args.includeRoot = (n === 'true'); i++; }
    else if (a === '--help' || a === '-h') { args.help = true; }
  }
  return args;
}

function ensureDir(p) {
  if (!fs.existsSync(p)) fs.mkdirSync(p, { recursive: true });
}

function sanitizeName(name) {
  const base = (name && String(name).trim()) ? String(name).trim() : 'unnamed';
  return base.replace(/[\\/:*?"<>|\s]+/g, '_');
}

function bakeMeshWorld(mesh) {
  // Returns a new Mesh with geometry transformed to world space
  mesh.updateWorldMatrix(true, false);
  const geom = mesh.geometry.clone();
  geom.applyMatrix4(mesh.matrixWorld);
  const baked = new THREE.Mesh(geom, mesh.material);
  baked.name = mesh.name;
  return baked;
}

function isMesh(obj) {
  return (obj instanceof THREE.Mesh) || (obj && obj.isMesh === true);
}

async function loadSceneFactory(modulePath, fnName) {
  const url = pathToFileURL(path.resolve(modulePath)).href;
  const mod = await import(url);
  const factory = (typeof mod[fnName] === 'function') ? mod[fnName] : (typeof mod.default === 'function' ? mod.default : null);
  if (!factory) throw new Error(`No factory function '${fnName}' (or default export) found in ${modulePath}`);
  return factory;
}

function collectPartsAndAssignments(root, includeRoot) {
  // Find all named groups as parts
  const parts = new Map(); // name -> { group, meshes: Set<Mesh> }
  const namedGroups = new Set();

  root.traverse(obj => {
    if (obj instanceof THREE.Group && obj.name && obj.name.trim() !== '') {
      const pname = sanitizeName(obj.name);
      namedGroups.add(obj);
      if (!parts.has(pname)) parts.set(pname, { group: obj, meshes: new Set() });
    }
  });

  // Helper to find nearest named ancestor group
  function nearestNamedGroup(obj) {
    let cur = obj.parent;
    while (cur) {
      if (cur instanceof THREE.Group && cur.name && cur.name.trim() !== '') return cur;
      cur = cur.parent;
    }
    return null;
  }

  const unassigned = [];

  root.traverse(obj => {
    if (isMesh(obj) && obj.visible !== false) {
      const parentGroup = nearestNamedGroup(obj);
      if (parentGroup) {
        const pname = sanitizeName(parentGroup.name);
        const entry = parts.get(pname) || { group: parentGroup, meshes: new Set() };
        entry.meshes.add(obj);
        parts.set(pname, entry);
      } else {
        unassigned.push(obj);
      }
    }
  });

  if (includeRoot && unassigned.length > 0) {
    parts.set('root_unassigned', { group: root, meshes: new Set(unassigned) });
  }

  return parts;
}

function exportMeshOBJ(exporter, mesh, outPath) {
  const objText = exporter.parse(mesh);
  fs.writeFileSync(outPath, objText);
}

function exportPartMeshes(parts, outDir) {
  const exporter = new OBJExporter();
  const partsDir = path.join(outDir, 'part_meshes');
  const linksDir = path.join(outDir, 'links');
  ensureDir(partsDir);
  ensureDir(linksDir);

  // Track filenames to avoid overwrites
  const usedNames = new Map(); // key: dir -> Set(filenames)

  function uniqueFileName(dir, base) {
    const set = usedNames.get(dir) || new Set();
    let candidate = base;
    let i = 1;
    while (set.has(candidate)) {
      candidate = `${base}_${i++}`;
    }
    set.add(candidate);
    usedNames.set(dir, set);
    return candidate;
  }

  // Export individual meshes per part
  for (const [partName, { group, meshes }] of parts.entries()) {
    const partPath = path.join(partsDir, partName);
    ensureDir(partPath);

    let count = 0;
    for (const m of meshes) {
      const baked = bakeMeshWorld(m);
      const mname = sanitizeName(baked.name) || 'mesh';
      const fname = uniqueFileName(partPath, mname) + '.obj';
      exportMeshOBJ(exporter, baked, path.join(partPath, fname));
      count++;
    }

    // Export merged link for this part
    const linkGroup = new THREE.Group();
    group.traverse(child => {
      if (isMesh(child) && child.visible !== false) {
        linkGroup.add(bakeMeshWorld(child));
      }
    });
    const linkFile = path.join(linksDir, `${partName}.obj`);
    exportMeshOBJ(exporter, linkGroup, linkFile);

    console.log(`Exported part '${partName}': ${count} mesh(es), link OBJ written.`);
  }
}

async function main() {
  const args = parseArgs(process.argv);
  if (args.help || !args.scene) {
    console.log(`Usage: node export_three_parts.mjs --scene <modulePath> [--fn createScene] [--out ./output] [--include-root true|false]`);
    process.exit(args.scene ? 0 : 1);
  }

  ensureDir(args.out);

  const factory = await loadSceneFactory(args.scene, args.fn);
  const root = factory();
  if (!(root && root.isObject3D)) {
    throw new Error('Factory did not return a THREE.Object3D or Scene.');
  }

  // Normalize to a Scene for consistent traversal
  const scene = root.isScene ? root : new THREE.Scene();
  if (!root.isScene) scene.add(root);

  scene.updateWorldMatrix(true, true);

  const parts = collectPartsAndAssignments(scene, args.includeRoot);
  if (parts.size === 0) {
    console.warn('No named THREE.Group parts found. Consider enabling --include-root to capture unassigned meshes.');
  }
  exportPartMeshes(parts, args.out);

  console.log('Export complete.');
}

main().catch(err => {
  console.error(err?.stack || err?.message || String(err));
  process.exit(1);
});
