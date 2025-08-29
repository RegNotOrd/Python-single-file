// game.js - JavaScript version of the Tower of Hanoi
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const CANVAS_W = parseInt(canvas.width);
const CANVAS_H = parseInt(canvas.height);

const diskInput = document.getElementById("diskCount");
const startBtn = document.getElementById("startBtn");
const autoBtn = document.getElementById("autoBtn");
const moveLabel = document.getElementById("moveLabel");

const peg_count = 3;
const peg_width = 10;
const peg_height = 240;
const disk_height = 22;
const disk_min_width = 60;
const disk_max_width = 240;

let peg_x = [];
let pegs = [
  [],
  [],
  []
];
let dragging = null;
let move_count = 0;
let isSolving = false;

// Helper to compute peg positions
function compute_pegs() {
  const spacing = CANVAS_W / (peg_count + 1);
  peg_x = Array.from({
    length: peg_count
  }, (_, i) => (i + 1) * spacing);
}

// Drawing
function clear() {
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, CANVAS_W, CANVAS_H);
}

function draw() {
  clear();
  // draw pegs
  ctx.fillStyle = "#111";
  for (const x of peg_x) {
    ctx.fillRect(x - peg_width / 2, CANVAS_H - peg_height, peg_width, peg_height);
  }
  // draw disks
  for (let pi = 0; pi < pegs.length; pi++) {
    const peg = pegs[pi];
    for (let depth = 0; depth < peg.length; depth++) {
      const d = peg[depth];
      const x = d.x;
      const y = d.y;
      const w = d.width;
      const h = disk_height - 2;
      ctx.fillStyle = "#87cefa";
      // This is the correct drawing position for the disk
      ctx.fillRect(x - w / 2, y - h, w, h);
      // rim
      ctx.strokeStyle = "#0b3a66";
      ctx.strokeRect(x - w / 2, y - h, w, h);
    }
  }
  // draw overlay instructions
  ctx.fillStyle = "#23324a";
  ctx.font = "12px sans-serif";
  ctx.fillText("Drag the top disk of any peg. Click 'Auto Solve' to auto-run.", 10, 18);
}

// Build disks on peg 0 (bottom-up)
function layout_disks(n) {
  pegs = Array.from({
    length: peg_count
  }, () => []);
  const spacing = n <= 1 ? 1 : (disk_max_width - disk_min_width) / Math.max(1, (n - 1));
  for (let i = n - 1; i >= 0; i--) {
    const width = parseInt(disk_min_width + i * spacing);
    const x = peg_x[0];
    const y = CANVAS_H - (n - i) * disk_height;
    const disk = {
      size: i,
      width: width,
      x: x,
      y: y
    };
    pegs[0].push(disk);
  }
  update_move_label(0);
  draw();
}

function update_disk_positions(peg_index) {
  for (let idx = 0; idx < pegs[peg_index].length; idx++) {
    const d = pegs[peg_index][idx];
    const stack_height = pegs[peg_index].length;
    // Corrected y-position calculation
    const y = CANVAS_H - (stack_height - idx) * disk_height;
    d.y = y;
    d.x = peg_x[peg_index];
  }
}

function get_top_disk_at_pos(x, y) {
  const threshold = 30;
  for (let pi = 0; pi < pegs.length; pi++) {
    const peg = pegs[pi];
    if (peg.length === 0) {
      continue;
    }
    const top = peg[peg.length - 1];
    const w = top.width;
    const left = top.x - w / 2;
    const right = top.x + w / 2;
    // Corrected y-position check for collision
    const top_y = top.y - disk_height;
    const bottom_y = top.y;
    if (x >= left - threshold && x <= right + threshold && y >= top_y && y <= bottom_y + threshold) {
      return [pi, top];
    }
  }
  return [null, null];
}

// Move label update
function update_move_label(count) {
  moveLabel.innerText = `Moves: ${count}`;
}

// Mouse handlers
function on_mousedown(evt) {
  if (isSolving) return;
  const rect = canvas.getBoundingClientRect();
  const mx = evt.clientX - rect.left;
  const my = evt.clientY - rect.top;
  const [peg_idx, disk] = get_top_disk_at_pos(mx, my);
  if (disk !== null) {
    dragging = {
      disk: disk,
      orig_peg: peg_idx,
      offset_x: mx - disk.x,
      offset_y: my - disk.y
    };
    if (pegs[peg_idx] && pegs[peg_idx][pegs[peg_idx].length - 1] === disk) {
      pegs[peg_idx].pop();
    }
    draw();
  }
}

function on_mousemove(evt) {
  if (!dragging) {
    return;
  }
  const rect = canvas.getBoundingClientRect();
  const mx = evt.clientX - rect.left;
  const my = evt.clientY - rect.top;
  const drag_disk = dragging.disk;
  drag_disk.x = mx - dragging.offset_x;
  drag_disk.y = my - dragging.offset_y;
  draw();
}

function is_valid_move(disk, target_peg_index) {
  if (pegs[target_peg_index].length === 0) {
    return true;
  }
  const top = pegs[target_peg_index][pegs[target_peg_index].length - 1];
  return disk.size < top.size;
}

function snap_and_place(disk, target_peg_index, revert = false) {
  if (revert) {
    pegs[dragging.orig_peg].push(disk);
    update_disk_positions(dragging.orig_peg);
  } else {
    pegs[target_peg_index].push(disk);
    update_disk_positions(target_peg_index);
    move_count += 1;
    update_move_label(move_count);
    const n = parseInt(diskInput.value);
    if (pegs[0].length === 0 && pegs[2].length === n) {
      setTimeout(() => {
        window.alert(`Congratulations! You solved the puzzle in ${move_count} moves!`);
      }, 100);
    }
  }
  draw();
}

function on_mouseup(evt) {
  if (!dragging) {
    return;
  }
  const rect = canvas.getBoundingClientRect();
  const mx = evt.clientX - rect.left;
  const my = evt.clientY - rect.top;
  const closest = peg_x.reduce((prev, curr, i) => {
    return Math.abs(mx - curr) < Math.abs(mx - peg_x[prev]) ? i : prev;
  }, 0);
  const disk = dragging.disk;
  if (is_valid_move(disk, closest)) {
    snap_and_place(disk, closest, false);
  } else {
    snap_and_place(disk, dragging.orig_peg, true);
  }
  dragging = null;
}

// Async move + animation for auto-solver
async function move_disk_animated(source, target) {
  if (pegs[source].length === 0) {
    return;
  }
  const disk = pegs[source].pop();
  const start_x = disk.x;
  const target_x = peg_x[target];
  const steps = 12;

  for (let i = 0; i < steps; i++) {
    disk.x = start_x + (target_x - start_x) * (i + 1) / steps;
    draw();
    await new Promise(resolve => setTimeout(resolve, 30));
  }

  pegs[target].push(disk);
  update_disk_positions(target);
  move_count += 1;
  update_move_label(move_count);
  draw();
  await new Promise(resolve => setTimeout(resolve, 80));
}

async function solve_hanoi_async(n, source, target, aux) {
  if (n === 0) {
    return;
  }
  if (n === 1) {
    await move_disk_animated(source, target);
  } else {
    await solve_hanoi_async(n - 1, source, aux, target);
    await move_disk_animated(source, target);
    await solve_hanoi_async(n - 1, aux, target, source);
  }
}

// Start / Auto-solve handlers
function start_game() {
  const n = parseInt(diskInput.value);
  if (isNaN(n) || n < 1 || n > 10) {
    window.alert("Please enter a number between 1 and 10");
    return;
  }
  dragging = null;
  compute_pegs();
  layout_disks(n);
  move_count = 0;
  update_move_label(move_count);
}

async function auto_solve_handler() {
  const n = parseInt(diskInput.value);
  if (isNaN(n) || n < 1 || n > 10) {
    window.alert("Please enter a number between 1 and 10");
    return;
  }
  isSolving = true;
  await solve_hanoi_async(n, 0, 2, 1);
  window.alert(`Tower solved by auto-solver in ${move_count} moves!`);
  isSolving = false;
}

// Set up event listeners
canvas.addEventListener("mousedown", on_mousedown);
canvas.addEventListener("mousemove", on_mousemove);
window.addEventListener("mouseup", on_mouseup);

startBtn.addEventListener("click", start_game);
autoBtn.addEventListener("click", auto_solve_handler);

// Initial layout
compute_pegs();
layout_disks(3);
