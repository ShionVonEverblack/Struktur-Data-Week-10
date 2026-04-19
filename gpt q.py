import re

class Job:
    def __init__(self, name, length, priority, arrival_order):
        self.name = name
        self.length = length
        self.priority = priority
        self.arrival_order = arrival_order
        self.remaining = length

    def __lt__(self, other):
        # Min-heap:
        # priority lebih kecil = lebih tinggi (-20 tertinggi, 19 terendah)
        # jika priority sama, yang datang lebih dulu diproses lebih dulu
        if self.priority == other.priority:
            return self.arrival_order < other.arrival_order
        return self.priority < other.priority

    def __repr__(self):
        return (
            f"Job(name='{self.name}', length={self.length}, "
            f"priority={self.priority}, remaining={self.remaining})"
        )

class HeapPriorityQueue:
    def __init__(self):
        self._data = []

    def __len__(self):
        return len(self._data)

    def is_empty(self):
        return len(self._data) == 0

    def parent(self, j):
        return (j - 1) // 2

    def left(self, j):
        return 2 * j + 1

    def right(self, j):
        return 2 * j + 2

    def has_left(self, j):
        return self.left(j) < len(self._data)

    def has_right(self, j):
        return self.right(j) < len(self._data)

    def swap(self, i, j):
        self._data[i], self._data[j] = self._data[j], self._data[i]

    def upheap(self, j):
        while j > 0:
            p = self.parent(j)
            if self._data[j] < self._data[p]:
                self.swap(j, p)
                j = p
            else:
                break

    def downheap(self, j):
        while self.has_left(j):
            left = self.left(j)
            small_child = left

            if self.has_right(j):
                right = self.right(j)
                if self._data[right] < self._data[left]:
                    small_child = right

            if self._data[small_child] < self._data[j]:
                self.swap(j, small_child)
                j = small_child
            else:
                break

    def add(self, item):
        self._data.append(item)
        self.upheap(len(self._data) - 1)

    def min(self):
        if self.is_empty():
            raise IndexError("Priority queue kosong.")
        return self._data[0]

    def remove_min(self):
        if self.is_empty():
            raise IndexError("Priority queue kosong.")

        self.swap(0, len(self._data) - 1)
        item = self._data.pop()

        if not self.is_empty():
            self.downheap(0)

        return item

    def heap_view(self):
        # tampilan internal heap, bukan urutan sorted penuh
        return [
            f"{job.name}(p={job.priority}, rem={job.remaining})"
            for job in self._data
        ]


class CPUScheduler:
    ADD_PATTERN = re.compile(
        r"^add\s+(.+?)\s+with\s+length\s+(\d+)\s+and\s+priority\s+(-?\d+)$",
        re.IGNORECASE
    )

    def __init__(self):
        self.ready_queue = HeapPriorityQueue()
        self.current_job = None
        self.arrival_counter = 0
        self.completed_jobs = []

    def parse_command(self, command):
        command = command.strip()

        if command.lower() == "no new job this slice":
            return ("none", None)

        match = self.ADD_PATTERN.match(command)
        if not match:
            raise ValueError(
                "Format command tidak valid.\n"
                "Gunakan:\n"
                "  add job_name with length n and priority p\n"
                "atau:\n"
                "  no new job this slice"
            )

        name = match.group(1).strip()
        length = int(match.group(2))
        priority = int(match.group(3))

        if not (-20 <= priority <= 19):
            raise ValueError("Priority harus di antara -20 sampai 19.")
        if not (1 <= length <= 100):
            raise ValueError("Length harus di antara 1 sampai 100.")

        return ("add", (name, length, priority))

    def process_command(self, command):
        kind, payload = self.parse_command(command)

        if kind == "add":
            name, length, priority = payload
            job = Job(name, length, priority, self.arrival_counter)
            self.arrival_counter += 1
            self.ready_queue.add(job)
            return f"Job '{name}' ditambahkan (length={length}, priority={priority})"

        return "Tidak ada job baru"

    def dispatch_if_needed(self):
        if self.current_job is None and not self.ready_queue.is_empty():
            self.current_job = self.ready_queue.remove_min()
            return f"CPU mengambil job '{self.current_job.name}'"
        return None

    def run_one_slice(self, command_text):
        command_info = self.process_command(command_text)
        dispatch_info = self.dispatch_if_needed()

        if self.current_job is None:
            running_name = "idle"
            finish_info = None
        else:
            running_name = self.current_job.name
            self.current_job.remaining -= 1

            if self.current_job.remaining == 0:
                finish_info = f"Job '{self.current_job.name}' selesai"
                self.completed_jobs.append(self.current_job.name)
                self.current_job = None
            else:
                finish_info = None

        return {
            "command": command_text,
            "command_info": command_info,
            "dispatch_info": dispatch_info,
            "running": running_name,
            "finish_info": finish_info,
            "heap_state": self.ready_queue.heap_view(),
            "current_job": None if self.current_job is None else
                f"{self.current_job.name}(rem={self.current_job.remaining})"
        }

    def simulate(self, commands):
        """
        Menjalankan simulasi:
        - tiap command = 1 time slice
        - setelah command habis, simulator lanjut otomatis
          dengan 'no new job this slice' sampai semua job selesai
        """
        logs = []
        time_slice = 1
        index = 0

        while (
            index < len(commands)
            or self.current_job is not None
            or not self.ready_queue.is_empty()
        ):
            if index < len(commands):
                cmd = commands[index]
                index += 1
            else:
                cmd = "no new job this slice"

            result = self.run_one_slice(cmd)
            result["time_slice"] = time_slice
            logs.append(result)
            time_slice += 1

        return logs


def print_report(logs, scheduler):
    print("\n" + "=" * 72)
    print("HASIL SIMULASI CPU JOB SCHEDULER")
    print("=" * 72)

    for log in logs:
        print(f"\n[Time Slice {log['time_slice']}]")
        print(f"Command      : {log['command']}")
        print(f"Info Command : {log['command_info']}")

        if log["dispatch_info"]:
            print(f"Dispatch     : {log['dispatch_info']}")

        print(f"CPU Running  : {log['running']}")

        if log["finish_info"]:
            print(f"Status       : {log['finish_info']}")

        print(f"Current Job  : {log['current_job']}")
        print(f"Heap State   : {log['heap_state']}")

    timeline = [log["running"] for log in logs]

    print("\n" + "=" * 72)
    print("RINGKASAN")
    print("=" * 72)
    print("Timeline CPU :", " -> ".join(timeline))
    print("Urutan selesai:", " -> ".join(scheduler.completed_jobs)
          if scheduler.completed_jobs else "(tidak ada)")
    print("=" * 72)


def main():
    print("CPU Job Scheduler - Binary Heap Priority Queue")
    print("Format command:")
    print("  add job_name with length n and priority p")
    print("  no new job this slice")
    print("\nContoh:")
    print("  add Render with length 3 and priority -5")
    print("  no new job this slice")

    try:
        n = int(input("\nMasukkan jumlah command awal: ").strip())
        if n < 0:
            raise ValueError("Jumlah command tidak boleh negatif.")
    except ValueError as e:
        print(f"Input tidak valid: {e}")
        return

    commands = []
    for i in range(1, n + 1):
        cmd = input(f"Command slice {i}: ").strip()
        commands.append(cmd)

    scheduler = CPUScheduler()

    try:
        logs = scheduler.simulate(commands)
        print_report(logs, scheduler)
    except ValueError as e:
        print(f"\nTerjadi error input: {e}")
    except IndexError as e:
        print(f"\nTerjadi error heap: {e}")


if __name__ == "__main__":
    main()