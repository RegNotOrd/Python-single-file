import tkinter as tk
from tkinter import messagebox
import time

class TowerOfHanoi:
    def __init__(self, root):
        self.root = root
        self.root.title("Tower of Hanoi")

        self.disk_count = tk.IntVar(value=3)
        self.canvas_width = 600
        self.canvas_height = 400
        self.peg_count = 3
        self.peg_width = 10
        self.peg_height = 200
        self.disk_height = 20
        self.disk_min_width = 40
        self.disk_max_width = 160

        self.pegs = [[] for _ in range(self.peg_count)]
        self.disk_items = {}
        self.selected_disk = None
        self.selected_peg_index = None
        self.move_count = 0

        self.setup_ui()

    def setup_ui(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        tk.Label(control_frame, text="Number of Disks:").pack(side=tk.LEFT)
        tk.Entry(control_frame, textvariable=self.disk_count, width=5).pack(side=tk.LEFT)
        tk.Button(control_frame, text="Start Game", command=self.start_game).pack(side=tk.LEFT, padx=10)
        tk.Button(control_frame, text="Auto Solve", command=self.auto_solve).pack(side=tk.LEFT)
        self.move_label = tk.Label(control_frame, text="Moves: 0")
        self.move_label.pack(side=tk.LEFT, padx=20)

        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg='white')
        self.canvas.pack()
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<B1-Motion>', self.on_canvas_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_canvas_release)

    def start_game(self):
        try:
            n = self.disk_count.get()
            if n < 1 or n > 10:
                raise ValueError
        except:
            messagebox.showerror("Invalid Input", "Please enter a number between 1 and 10")
            return

        self.pegs = [[] for _ in range(self.peg_count)]
        self.disk_items.clear()
        self.selected_disk = None
        self.selected_peg_index = None
        self.move_count = 0
        self.move_label.config(text="Moves: 0")
        self.canvas.delete("all")
        self.draw_pegs()
        self.draw_disks(n)

    def draw_pegs(self):
        spacing = self.canvas_width // (self.peg_count + 1)
        self.peg_x_positions = []

        for i in range(self.peg_count):
            x = (i + 1) * spacing
            self.peg_x_positions.append(x)
            self.canvas.create_rectangle(x - self.peg_width//2, self.canvas_height - self.peg_height,
                                         x + self.peg_width//2, self.canvas_height, fill="black")

    def draw_disks(self, n):
        spacing = (self.disk_max_width - self.disk_min_width) // max(1, (n - 1))

        for i in reversed(range(n)):
            width = self.disk_min_width + i * spacing
            x = self.peg_x_positions[0]
            y = self.canvas_height - (n - i) * self.disk_height
            disk = self.canvas.create_rectangle(x - width//2, y, x + width//2, y + self.disk_height, fill="skyblue")
            self.pegs[0].append(disk)
            self.disk_items[disk] = {
                'size': i,
                'width': width,
                'drag': False
            }

    def get_peg_index(self, x):
        for i, peg_x in enumerate(self.peg_x_positions):
            if abs(x - peg_x) < 50:
                return i
        return None

    def on_canvas_click(self, event):
        item = self.canvas.find_closest(event.x, event.y)[0]
        for i, peg in enumerate(self.pegs):
            if peg and peg[-1] == item:
                self.selected_disk = item
                self.selected_peg_index = i
                self.disk_items[item]['drag'] = True
                break

    def on_canvas_drag(self, event):
        if self.selected_disk and self.disk_items[self.selected_disk]['drag']:
            width = self.disk_items[self.selected_disk]['width']
            self.canvas.coords(self.selected_disk,
                               event.x - width//2,
                               event.y - self.disk_height//2,
                               event.x + width//2,
                               event.y + self.disk_height//2)

    def on_canvas_release(self, event):
        if self.selected_disk and self.disk_items[self.selected_disk]['drag']:
            target_peg_index = self.get_peg_index(event.x)
            if target_peg_index is not None and self.validate_move(self.selected_disk, target_peg_index):
                self.pegs[self.selected_peg_index].pop()
                self.pegs[target_peg_index].append(self.selected_disk)
                self.snap_disk_to_peg(self.selected_disk, target_peg_index)
                self.move_count += 1
                self.move_label.config(text=f"Moves: {self.move_count}")
                if self.check_win():
                    messagebox.showinfo("Congratulations!", f"You solved the puzzle in {self.move_count} moves!")
            else:
                self.snap_disk_to_peg(self.selected_disk, self.selected_peg_index)

            self.disk_items[self.selected_disk]['drag'] = False
            self.selected_disk = None
            self.selected_peg_index = None

    def validate_move(self, disk, target_peg):
        if not self.pegs[target_peg]:
            return True
        top_disk = self.pegs[target_peg][-1]
        return self.disk_items[disk]['size'] < self.disk_items[top_disk]['size']

    def snap_disk_to_peg(self, disk, peg_index):
        x = self.peg_x_positions[peg_index]
        y = self.canvas_height - len(self.pegs[peg_index]) * self.disk_height
        width = self.disk_items[disk]['width']
        self.canvas.coords(disk, x - width//2, y - self.disk_height, x + width//2, y)

    def check_win(self):
        return len(self.pegs[0]) == 0 and len(self.pegs[2]) == self.disk_count.get()

    def move_disk(self, source, target):
        disk = self.pegs[source].pop()
        self.pegs[target].append(disk)
        self.snap_disk_to_peg(disk, target)
        self.move_count += 1
        self.move_label.config(text=f"Moves: {self.move_count}")
        self.root.update()
        time.sleep(0.5)

    def solve_hanoi(self, n, source, target, auxiliary):
        if n == 1:
            self.move_disk(source, target)
        else:
            self.solve_hanoi(n-1, source, auxiliary, target)
            self.move_disk(source, target)
            self.solve_hanoi(n-1, auxiliary, target, source)

    def auto_solve(self):
        n = self.disk_count.get()
        self.solve_hanoi(n, 0, 2, 1)
        messagebox.showinfo("Solved", f"Tower solved by auto-solver in {self.move_count} moves!")

if __name__ == "__main__":
    root = tk.Tk()
    game = TowerOfHanoi(root)
    root.mainloop()
