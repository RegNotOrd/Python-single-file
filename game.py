# game.py - PyScript version of your Tower of Hanoi
from js import document, window
from pyodide.ffi import create_proxy
import asyncio, math

# Canvas & layout
canvas = document.getElementById("gameCanvas")
ctx = canvas.getContext("2d")

CANVAS_W = int(canvas.width)
CANVAS_H = int(canvas.height)

# UI elements
disk_input = document.getElementById("diskCount")
start_btn = document.getElementById("startBtn")
auto_btn = document.getElementById("autoBtn")
move_label = document.getElementById("moveLabel")

# Game params (matching your original choices)
peg_count = 3
peg_width = 10
peg_height = 240
disk_height = 22
disk_min_width = 60
disk_max_width = 240

peg_x = []
pegs = [[] for _ in range(peg_count)]  # each peg: list of disk dicts from bottom->top
dragging = None  # dict: {'disk':..., 'orig_peg':..., 'offset_x':...}
move_count = 0

# Helper to compute peg positions
def compute_pegs():
    global peg_x
    spacing = CANVAS_W // (peg_count + 1)
    peg_x = [ (i+1) * spacing for i in range(peg_count) ]

# Drawing
def clear():
    ctx.fillStyle = "#ffffff"
    ctx.fillRect(0,0,CANVAS_W,CANVAS_H)

def draw():
    clear()
    # draw pegs
    ctx.fillStyle = "#111"
    for x in peg_x:
        ctx.fillRect(x - peg_width//2, CANVAS_H - peg_height, peg_width, peg_height)
    # draw disks
    for pi, peg in enumerate(pegs):
        for depth, d in enumerate(peg):
            # position computed from top/bottom
            # disk dict has fields: size, width, x, y
            x = d['x']
            y = d['y']
            w = d['width']
            h = disk_height - 2
            ctx.fillStyle = "#87cefa"
            ctx.fillRect(x - w/2, y - h, w, h)
            # rim
            ctx.strokeStyle = "#0b3a66"
            ctx.strokeRect(x - w/2, y - h, w, h)
    # draw overlay instructions
    ctx.fillStyle = "#23324a"
    ctx.font = "12px sans-serif"
    ctx.fillText("Drag the top disk of any peg. Click 'Auto Solve' to auto-run.", 10, 18)

# Build disks on peg 0 (bottom-up)
def layout_disks(n):
    global pegs
    pegs = [[] for _ in range(peg_count)]
    spacing = 1 if n<=1 else (disk_max_width - disk_min_width) / max(1, (n - 1))
    for i in reversed(range(n)):
        width = int(disk_min_width + i * spacing)
        x = peg_x[0]
        y = CANVAS_H - (n - i) * disk_height
        disk = {
            'size': i,
            'width': width,
            'x': x,
            'y': y
        }
        pegs[0].append(disk)
    update_move_label(0)
    draw()

def update_disk_positions(peg_index):
    # recompute y positions for disks on peg
    for idx, d in enumerate(pegs[peg_index]):
        # bottom disk index 0 => y = CANVAS_H - disk_height
        stack_height = len(pegs[peg_index])
        # d at position idx (0-bottom)
        y = CANVAS_H - (stack_height - idx) * disk_height
        d['y'] = y
        d['x'] = peg_x[peg_index]

def get_top_disk_at_pos(x, y):
    # return (peg_index, disk) only if the position is inside top disk
    threshold = 30
    for pi, peg in enumerate(pegs):
        if not peg: 
            continue
        top = peg[-1]
        w = top['width']
        left = top['x'] - w/2
        right = top['x'] + w/2
        top_y = top['y'] - disk_height
        bottom_y = top['y']
        if left - threshold <= x <= right + threshold and top_y <= y <= bottom_y + threshold:
            return pi, top
    return None, None

# Move label update
def update_move_label(count):
    move_label.innerText = f"Moves: {count}"

# Mouse handlers
def on_mousedown(evt):
    global dragging
    rect = canvas.getBoundingClientRect()
    mx = evt.clientX - rect.left
    my = evt.clientY - rect.top
    peg_idx, disk = get_top_disk_at_pos(mx, my)
    if disk is not None:
        dragging = {'disk': disk, 'orig_peg': peg_idx, 'offset_x': mx - disk['x'], 'offset_y': my - disk['y']}
        # remove disk from peg while dragging
        if pegs[peg_idx] and pegs[peg_idx][-1] == disk:
            pegs[peg_idx].pop()
        draw()

def on_mousemove(evt):
    global dragging
    if not dragging:
        return
    rect = canvas.getBoundingClientRect()
    mx = evt.clientX - rect.left
    my = evt.clientY - rect.top
    drag_disk = dragging['disk']
    drag_disk['x'] = mx - dragging['offset_x']
    drag_disk['y'] = my - dragging['offset_y']
    draw()

def is_valid_move(disk, target_peg_index):
    if not pegs[target_peg_index]:
        return True
    top = pegs[target_peg_index][-1]
    return disk['size'] < top['size']

def snap_and_place(disk, target_peg_index, revert=False):
    global move_count
    if revert:
        # put back on original peg
        pegs[dragging['orig_peg']].append(disk)
        update_disk_positions(dragging['orig_peg'])
        draw()
    else:
        # add to target
        pegs[target_peg_index].append(disk)
        update_disk_positions(target_peg_index)
        move_count += 1
        update_move_label(move_count)
        draw()
        # check win
        n = int(disk_input.value)
        if len(pegs[0]) == 0 and len(pegs[2]) == n:
            window.alert(f"Congratulations! You solved the puzzle in {move_count} moves!")

def on_mouseup(evt):
    global dragging
    if not dragging:
        return
    rect = canvas.getBoundingClientRect()
    mx = evt.clientX - rect.left
    my = evt.clientY - rect.top
    # find closest peg index
    closest = min(range(len(peg_x)), key=lambda i: abs(mx - peg_x[i]))
    disk = dragging['disk']
    if is_valid_move(disk, closest):
        snap_and_place(disk, closest, revert=False)
    else:
        snap_and_place(disk, dragging['orig_peg'], revert=True)
    dragging = None

# Async move + animation for auto-solver
async def move_disk_animated(source, target):
    global move_count
    if not pegs[source]:
        return
    disk = pegs[source].pop()
    # animate from source x to target x (linear)
    start_x = disk['x']
    target_x = peg_x[target]
    steps = 12
    for i in range(steps):
        disk['x'] = start_x + (target_x - start_x) * (i+1)/steps
        draw()
        await asyncio.sleep(0.03)
    # place on target
    pegs[target].append(disk)
    update_disk_positions(target)
    move_count += 1
    update_move_label(move_count)
    draw()
    await asyncio.sleep(0.08)

async def solve_hanoi_async(n, source, target, aux):
    if n == 0:
        return
    if n == 1:
        await move_disk_animated(source, target)
    else:
        await solve_hanoi_async(n-1, source, aux, target)
        await move_disk_animated(source, target)
        await solve_hanoi_async(n-1, aux, target, source)

# Start / Auto-solve handlers
def start_game(_evt=None):
    global move_count, dragging
    try:
        n = int(disk_input.value)
        if n < 1 or n > 10:
            raise ValueError
    except:
        window.alert("Please enter a number between 1 and 10")
        return
    dragging = None
    compute_pegs()
    layout_disks(n)
    move_count = 0
    update_move_label(move_count)

def auto_solve_handler(_evt=None):
    # run solver in background task
    n = int(disk_input.value)
    async def run():
        await solve_hanoi_async(n, 0, 2, 1)
        window.alert(f"Tower solved by auto-solver in {move_count} moves!")
    # schedule
    asyncio.ensure_future(run())

# Set up events using create_proxy
m_down = create_proxy(on_mousedown)
m_move = create_proxy(on_mousemove)
m_up = create_proxy(on_mouseup)
start_proxy = create_proxy(start_game)
auto_proxy = create_proxy(auto_solve_handler)

canvas.addEventListener("mousedown", m_down)
canvas.addEventListener("mousemove", m_move)
window.addEventListener("mouseup", m_up)

start_btn.addEventListener("click", start_proxy)
auto_btn.addEventListener("click", auto_proxy)

# initial layout
compute_pegs()
layout_disks(3)
