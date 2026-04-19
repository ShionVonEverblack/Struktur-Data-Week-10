class Job:
    # Mewakili satu job/proses yang akan dijalankan CPU.

    def __init__(self, name, priority, length, arrival_order):
        self.name = name                      # Nama job
        self.priority = priority              # Prioritas job (angka lebih kecil = lebih tinggi)
        self.length = length                  # Total durasi job
        self.remaining_time = length          # Sisa waktu eksekusi
        self.arrival_order = arrival_order    # Urutan kedatangan untuk tie-breaker

    def __lt__(self, other):
        # Menentukan apakah job ini lebih prioritas daripada job lain.
        # Aturan:
        # 1. Priority lebih kecil = lebih prioritas
        # 2. Jika priority sama, yang datang lebih dulu = lebih prioritas
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.arrival_order < other.arrival_order

    def __repr__(self):
        # Tampilan objek saat di-print, berguna untuk debugging.
        return (
            f"Job(name={self.name}, priority={self.priority}, "
            f"remaining={self.remaining_time}, arrival={self.arrival_order})"
        )


class BinaryHeap:
    # Implementasi min-heap untuk menyimpan job-job yang menunggu.
    # Root heap (index 0) selalu berisi job paling prioritas.

    def __init__(self):
        self.data = []  # List penyimpan elemen heap

    def __len__(self):
        return len(self.data)

    def is_empty(self):
        return len(self.data) == 0

    def parent(self, i):
        return (i - 1) // 2

    def left(self, i):
        return 2 * i + 1

    def right(self, i):
        return 2 * i + 2

    def has_left(self, i):
        return self.left(i) < len(self.data)

    def has_right(self, i):
        return self.right(i) < len(self.data)

    def peek(self):
        # Melihat elemen minimum (job paling prioritas) tanpa menghapusnya.
        if self.is_empty():
            return None
        return self.data[0]

    def swap(self, i, j):
        # Menukar dua elemen di heap.
        self.data[i], self.data[j] = self.data[j], self.data[i]

    def _upheap(self, i):
        # Memperbaiki heap dari bawah ke atas setelah insert.
        while i > 0:
            p = self.parent(i)
            if self.data[i] < self.data[p]:
                self.swap(i, p)
                i = p
            else:
                break

    def insert(self, job):
        # Menambahkan job baru ke heap.
        self.data.append(job)                 # Tambahkan di akhir
        self._upheap(len(self.data) - 1)      # Perbaiki posisi job

    def _downheap(self, i):
        # Memperbaiki heap dari atas ke bawah setelah root dihapus.
        while self.has_left(i):
            small_child = self.left(i)

            # Jika anak kanan ada dan lebih kecil dari anak kiri, pilih anak kanan
            if self.has_right(i) and self.data[self.right(i)] < self.data[small_child]:
                small_child = self.right(i)

            # Jika child lebih kecil dari parent, tukar
            if self.data[small_child] < self.data[i]:
                self.swap(i, small_child)
                i = small_child
            else:
                break

    def extract_min(self):
        # Mengambil dan menghapus job paling prioritas dari heap.
        if self.is_empty():
            return None

        if len(self.data) == 1:
            return self.data.pop()

        root = self.data[0]           # Simpan root lama
        self.data[0] = self.data.pop()  # Pindahkan elemen terakhir ke root
        self._downheap(0)             # Perbaiki heap
        return root


class CPUScheduler:
    # Simulator CPU scheduling non-preemptive.
    # CPU hanya mengambil job baru jika current_job kosong.

    def __init__(self):
        self.waiting_heap = BinaryHeap()  # Heap untuk job yang menunggu
        self.current_job = None           # Job yang sedang dijalankan CPU
        self.time_slice = 0               # Slice saat ini
        self.arrival_counter = 0          # Counter urutan kedatangan job
        self.history = []                 # Riwayat job yang berjalan per slice

    def add_job(self, name, priority, length):
        # Menambahkan job baru ke waiting heap.
        self.arrival_counter += 1
        job = Job(name, priority, length, self.arrival_counter)
        self.waiting_heap.insert(job)

    def run_one_slice(self):
        # Menjalankan CPU selama satu time slice.
        # Aturan:
        # - Jika CPU kosong, ambil job paling prioritas dari heap
        # - Jika tidak ada job sama sekali, CPU idle
        # - Jika ada job aktif, kurangi remaining_time
        # - Jika job selesai, current_job dikosongkan
        self.time_slice += 1

        # Jika CPU idle, ambil job baru dari heap
        if self.current_job is None:
            self.current_job = self.waiting_heap.extract_min()

        # Jika tetap tidak ada job, berarti idle
        if self.current_job is None:
            self.history.append("idle")
            return "idle"

        # Jalankan job aktif selama 1 slice
        running_name = self.current_job.name
        self.history.append(running_name)

        self.current_job.remaining_time -= 1

        # Jika selesai, kosongkan current_job
        if self.current_job.remaining_time == 0:
            self.current_job = None

        return running_name

    def process_slice_command(self, command):
        # Memproses command untuk satu slice, lalu menjalankan CPU satu slice.
        # Format command:
        # - ("add", name, priority, length)
        # - ("none",)
        if command[0] == "add":
            _, name, priority, length = command
            self.add_job(name, priority, length)

        return self.run_one_slice()


def parse_command(line):
    # Mengubah input string menjadi command tuple.
    #
    # Format yang didukung:
    # - add A with length 3 and priority -5
    # - no new job this slice
    line = line.strip()

    if line == "no new job this slice":
        return ("none",)

    parts = line.split()

    # Validasi sederhana format input
    if len(parts) != 8:
        raise ValueError("Format input tidak valid.")

    # Format yang diharapkan:
    # add JOBNAME with length N and priority P
    name = parts[1]
    length = int(parts[4])
    priority = int(parts[7])

    return ("add", name, priority, length)


def main():
    # Program utama:
    # - membaca jumlah time slice
    # - membaca command untuk setiap slice
    # - memproses simulasi
    # - menampilkan output per slice
    scheduler = CPUScheduler()

    n = int(input("Masukkan jumlah time slice: "))
    print("Masukkan command untuk setiap time slice:")

    for i in range(n):
        line = input().strip()
        command = parse_command(line)
        result = scheduler.process_slice_command(command)
        print(f"Slice {i + 1}: {result}")

    print("\nRiwayat eksekusi:")
    for i, job_name in enumerate(scheduler.history, start=1):
        print(f"Slice {i}: {job_name}")


if __name__ == "__main__":
    main()