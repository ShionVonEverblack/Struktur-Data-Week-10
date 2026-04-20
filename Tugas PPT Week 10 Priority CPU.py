class Job:
    def __init__(self, name, length, priority, arrival_order):
        self.name = name
        self.length = length
        self.priority = priority
        self.arrival_order = arrival_order
        self.remaining = length

    def __lt__(self, other):
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.arrival_order < other.arrival_order

    def __repr__(self):
        return (f"Job('{self.name}', priority={self.priority}, "
                f"length={self.length}, remaining={self.remaining})")

class BinaryHeap:
    def __init__(self):
        self.heap = []

    def __len__(self):
        return len(self.heap)

    def is_empty(self):
        return len(self.heap) == 0

    def _parent(self, i):
        return (i - 1) // 2

    def _left_child(self, i):
        return 2 * i + 1

    def _right_child(self, i):
        return 2 * i + 2

    def _has_left(self, i):
        return self._left_child(i) < len(self.heap)

    def _has_right(self, i):
        return self._right_child(i) < len(self.heap)

    def _swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def _upheap(self, i):
        while i > 0:
            parent = self._parent(i)
            if self.heap[i] < self.heap[parent]:
                self._swap(i, parent)
                i = parent
            else:
                break

    def _downheap(self, i):
        while self._has_left(i):
            left = self._left_child(i)
            smallest = left

            if self._has_right(i):
                right = self._right_child(i)
                if self.heap[right] < self.heap[left]:
                    smallest = right

            if self.heap[smallest] < self.heap[i]:
                self._swap(i, smallest)
                i = smallest
            else:
                break

    def insert(self, item):
        self.heap.append(item)
        self._upheap(len(self.heap) - 1)

    def peek_min(self):
        if self.is_empty():
            raise IndexError("Heap kosong, tidak ada elemen minimum.")
        return self.heap[0]

    def extract_min(self):
        if self.is_empty():
            raise IndexError("Heap kosong, tidak bisa extract.")

        self._swap(0, len(self.heap) - 1)
        min_item = self.heap.pop()

        if not self.is_empty():
            self._downheap(0)

        return min_item

    def display(self):
        if self.is_empty():
            return "[kosong]"
        items = []
        for job in self.heap:
            items.append(f"{job.name}(p={job.priority}, rem={job.remaining})")
        return ", ".join(items)


class CPUScheduler:
    def __init__(self):
        self.ready_queue = BinaryHeap()
        self.current_job = None
        self.time_slice = 0
        self.arrival_counter = 0
        self.history = []
        self.completed_jobs = []

    def add_job(self, name, length, priority):
        if not (-20 <= priority <= 19):
            raise ValueError(f"Priority harus antara -20 dan 19, diterima: {priority}")
        if not (1 <= length <= 100):
            raise ValueError(f"Length harus antara 1 dan 100, diterima: {length}")

        job = Job(name, length, priority, self.arrival_counter)
        self.arrival_counter += 1
        self.ready_queue.insert(job)

    def run_one_slice(self):
        self.time_slice += 1

        if self.current_job is None and not self.ready_queue.is_empty():
            self.current_job = self.ready_queue.extract_min()

        if self.current_job is None:
            self.history.append("idle")
            return "idle"

        running_name = self.current_job.name
        self.history.append(running_name)
        self.current_job.remaining -= 1

        if self.current_job.remaining == 0:
            self.completed_jobs.append(self.current_job.name)
            self.current_job = None

        return running_name

    def has_pending_work(self):
        return self.current_job is not None or not self.ready_queue.is_empty()


def parse_command(text):
    text = text.strip()

    if text.lower() == "no new job this slice":
        return ("none",)

    lower = text.lower()
    if lower.startswith("add "):
        try:
            parts = text.split()

            idx_with = None
            idx_length = None
            idx_and = None
            idx_priority = None

            for i, word in enumerate(parts):
                w = word.lower()
                if w == "with" and idx_with is None:
                    idx_with = i
                elif w == "length" and idx_with is not None and idx_length is None:
                    idx_length = i
                elif w == "and" and idx_length is not None and idx_and is None:
                    idx_and = i
                elif w == "priority" and idx_and is not None and idx_priority is None:
                    idx_priority = i

            if None in (idx_with, idx_length, idx_and, idx_priority):
                raise ValueError("Format command tidak valid.")

            name = " ".join(parts[1:idx_with])
            if not name:
                raise ValueError("Nama job tidak boleh kosong.")

            length = int(parts[idx_length + 1])

            priority = int(parts[idx_priority + 1])

            return ("add", name, length, priority)

        except (IndexError, ValueError) as e:
            raise ValueError(
                f"Format command tidak valid: {text}\n"
                f"Gunakan: add <nama_job> with length <n> and priority <p>"
            ) from e

    raise ValueError(
        f"Command tidak dikenali: {text}\n"
        f"Gunakan:\n"
        f"  add <nama_job> with length <n> and priority <p>\n"
        f"  no new job this slice"
    )


def main():
    print(" CPU JOB SCHEDULING SIMULATOR")
    print("Priority Queue dengan Binary Min-Heap")
    print()
    print("Format command:")
    print("  1. add <nama_job> with length <n> and priority <p>")
    print("     Contoh: add Render with length 3 and priority -5")
    print("  2. no new job this slice")
    print()
    print("Keterangan:")
    print("  - Priority: -20 (tertinggi) sampai 19 (terendah)")
    print("  - Length  : 1 sampai 100 (jumlah time slice)")
    print()

    try:
        n = int(input("Masukkan jumlah command: "))
        if n < 0:
            print("Jumlah command tidak boleh negatif.")
            return
    except ValueError:
        print("Input harus berupa bilangan bulat.")
        return

    commands = []
    print()
    for i in range(1, n + 1):
        cmd = input(f"  Command {i}: ")
        commands.append(cmd)

    scheduler = CPUScheduler()

    print()
    print("HASIL SIMULASI")

    cmd_index = 0
    while cmd_index < len(commands) or scheduler.has_pending_work():
        if cmd_index < len(commands):
            cmd_text = commands[cmd_index]
            cmd_index += 1
        else:
            cmd_text = "no new job this slice"

        try:
            parsed = parse_command(cmd_text)
        except ValueError as e:
            print(f"\n  [ERROR] {e}")
            return

        if parsed[0] == "add":
            _, name, length, priority = parsed
            try:
                scheduler.add_job(name, length, priority)
            except ValueError as e:
                print(f"\n  [ERROR] {e}")
                return

        running = scheduler.run_one_slice()

        print(f"  Time slice {scheduler.time_slice}: {running}")

    print()
    print("RINGKASAN")
    print(f"  Total time slices  : {scheduler.time_slice}")
    print(f"  Jobs selesai       : {len(scheduler.completed_jobs)}")
    print(f"  Urutan selesai     : {', '.join(scheduler.completed_jobs) if scheduler.completed_jobs else '(tidak ada)'}")
    print(f"  Timeline CPU       : {' -> '.join(scheduler.history)}")

if __name__ == "__main__":
    main()