class TowerOfHanoi {
  constructor(canvas, moveLabel) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.moveLabel = moveLabel;

    this.canvasWidth = canvas.width;
    this.canvasHeight = canvas.height;
    this.pegCount = 3;
    this.pegWidth = 10;
    this.pegHeight = 200;
    this.diskHeight = 20;
    this.diskMinWidth = 40;
    this.diskMaxWidth = 160;

    this.pegs = [];
    this.diskItems = new Map();
    this.pegXPositions = [];
    this.selectedDisk = null;
    this.selectedPegIndex = null;
    this.moveCount = 0;

    // event bindings
    this.canvas.addEventListener("mousedown", e => this.onMouseDown(e));
    this.canvas.addEventListener("mousemove", e => this.onMouseMove(e));
    this.canvas.addEventListener("mouseup", e => this.onMouseUp(e));
  }

  startGame(n) {
    if (n < 1 || n > 10) {
      alert("Please enter a number between 1 and 10");
      return;
    }
    this.pegs = Array.from({length: this.pegCount}, () => []);
    this.diskItems.clear();
    this.selectedDisk = null;
    this.selectedPegIndex = null;
    this.moveCount = 0;
    this.updateMoveLabel();

    this.pegXPositions = [];
    const spacing = this.canvasWidth / (this.pegCount + 1);
    for (let i = 0; i < this.pegCount; i++) {
      this.pegXPositions.push((i + 1) * spacing);
    }

    // create disks on first peg
    const step = (this.diskMaxWidth - this.diskMinWidth) / Math.max(1, n - 1);
    for (let i = n - 1; i >= 0; i--) {
      const width = this.diskMinWidth + i * step;
      const disk = {size: i, width, x: 0, y: 0, dragging: false};
      this.pegs[0].push(disk);
      this.diskItems.set(disk, disk);
      this.snapDiskToPeg(disk, 0);
    }

    this.redraw();
  }

  updateMoveLabel() {
    this.moveLabel.textContent = `Moves: ${this.moveCount}`;
  }

  redraw() {
    this.ctx.clearRect(0, 0, this.canvasWidth, this.canvasHeight);

    // draw pegs
    for (let i = 0; i < this.pegCount; i++) {
      const x = this.pegXPositions[i];
      this.ctx.fillStyle = "black";
      this.ctx.fillRect(x - this.pegWidth/2, this.canvasHeight - this.pegHeight, this.pegWidth, this.pegHeight);
    }

    // draw disks
    for (let i = 0; i < this.pegCount; i++) {
      for (let j = 0; j < this.pegs[i].length; j++) {
        const disk = this.pegs[i][j];
        this.ctx.fillStyle = "skyblue";
        this.ctx.fillRect(disk.x - disk.width/2, disk.y - this.diskHeight, disk.width, this.diskHeight);
        this.ctx.strokeStyle = "black";
        this.ctx.strokeRect(disk.x - disk.width/2, disk.y - this.diskHeight, disk.width, this.diskHeight);
      }
    }
  }

  getPegIndexAt(x) {
    for (let i = 0; i < this.pegXPositions.length; i++) {
      if (Math.abs(x - this.pegXPositions[i]) < 50) return i;
    }
    return null;
  }

  snapDiskToPeg(disk, pegIndex) {
    const peg = this.pegs[pegIndex];
    const x = this.pegXPositions[pegIndex];
    const y = this.canvasHeight - peg.length * this.diskHeight;
    disk.x = x;
    disk.y = y;
  }

  validateMove(disk, targetPeg) {
    const peg = this.pegs[targetPeg];
    if (peg.length === 0) return true;
    const topDisk = peg[peg.length - 1];
    return disk.size < topDisk.size;
  }

  onMouseDown(e) {
    const rect = this.canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    // find top disk under cursor
    for (let i = 0; i < this.pegs.length; i++) {
      const peg = this.pegs[i];
      if (peg.length === 0) continue;
      const disk = peg[peg.length - 1];
      if (mx >= disk.x - disk.width/2 && mx <= disk.x + disk.width/2 &&
          my >= disk.y - this.diskHeight && my <= disk.y) {
        this.selectedDisk = disk;
        this.selectedPegIndex = i;
        disk.dragging = true;
        break;
      }
    }
  }

  onMouseMove(e) {
    if (this.selectedDisk && this.selectedDisk.dragging) {
      const rect = this.canvas.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;
      this.selectedDisk.x = mx;
      this.selectedDisk.y = my;
      this.redraw();
      this.ctx.fillStyle = "rgba(0,0,0,0.2)";
      this.ctx.fillRect(0,0,this.canvasWidth,this.canvasHeight);
      // redraw dragged disk
      this.ctx.fillStyle = "orange";
      this.ctx.fillRect(this.selectedDisk.x - this.selectedDisk.width/2,
                        this.selectedDisk.y - this.diskHeight,
                        this.selectedDisk.width, this.diskHeight);
    }
  }

  onMouseUp(e) {
    if (this.selectedDisk && this.selectedDisk.dragging) {
      const rect = this.canvas.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const targetPeg = this.getPegIndexAt(mx);
      if (targetPeg !== null && this.validateMove(this.selectedDisk, targetPeg)) {
        this.pegs[this.selectedPegIndex].pop();
        this.pegs[targetPeg].push(this.selectedDisk);
        this.moveCount++;
        this.updateMoveLabel();
        if (this.checkWin()) {
          setTimeout(() => alert(`You solved the puzzle in ${this.moveCount} moves!`), 100);
        }
      }
      this.selectedDisk.dragging = false;
      this.snapDiskToPeg(this.selectedDisk, targetPeg !== null ? targetPeg : this.selectedPegIndex);
      this.selectedDisk = null;
      this.selectedPegIndex = null;
      this.redraw();
    }
  }

  checkWin() {
    return this.pegs[0].length === 0 && this.pegs[2].length > 0 &&
           this.pegs[2].every((d, i, arr) => i === 0 || arr[i-1].size < d.size);
  }

  moveDisk(source, target) {
    const disk = this.pegs[source].pop();
    this.pegs[target].push(disk);
    this.moveCount++;
    this.updateMoveLabel();
    this.snapDiskToPeg(disk, target);
    this.redraw();
  }

  async solveHanoi(n, source, target, auxiliary) {
    if (n === 1) {
      this.moveDisk(source, target);
      await new Promise(r => setTimeout(r, 500));
    } else {
      await this.solveHanoi(n-1, source, auxiliary, target);
      this.moveDisk(source, target);
      await new Promise(r => setTimeout(r, 500));
      await this.solveHanoi(n-1, auxiliary, target, source);
    }
  }

  async autoSolve() {
    const n = this.pegs[0].length;
    await this.solveHanoi(n, 0, 2, 1);
    alert(`Tower solved by auto-solver in ${this.moveCount} moves!`);
  }
}

// setup
const canvas = document.getElementById("gameCanvas");
const moveLabel = document.getElementById("moveLabel");
const hanoi = new TowerOfHanoi(canvas, moveLabel);

document.getElementById("startBtn").addEventListener("click", () => {
  const n = parseInt(document.getElementById("diskCount").value);
  hanoi.startGame(n);
});
document.getElementById("autoBtn").addEventListener("click", () => hanoi.autoSolve());
