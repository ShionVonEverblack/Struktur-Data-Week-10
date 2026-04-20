#Merepresentasikan satu job/tugas yang akan diproses CPU
class Job:
    def __init__(self, name, length, priority, arrival_order):
        self.name = name                    #Nama job (string)
        self.length = length                #Total time slice yang dibutuhkan
        self.priority = priority            #Nilai priority (-20 s/d 19)
        self.arrival_order = arrival_order  #Urutan kedatangan (untuk tie-breaker)
        self.remaining = length             #Sisa time slice yang harus dijalankan

    #Operator perbandingan untuk menentukan urutan di heap
    #Job dengan priority lebih kecil = lebih prioritas
    #Jika priority sama, job yang datang lebih dulu didahulukan
    def __lt__(self, other):
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.arrival_order < other.arrival_order

    # Representasi string untuk debugging
    def __repr__(self):
        return (f"Job('{self.name}', priority={self.priority}, "
                f"length={self.length}, remaining={self.remaining})")

#Implementasi Min-Heap secara manual (tanpa library heapq)
#Digunakan sebagai struktur data dasar untuk priority queue
class BinaryHeap:
    def __init__(self):
        self.heap = []  #Array/list untuk menyimpan elemen heap

    #Mengembalikan jumlah elemen dalam heap
    def __len__(self):
        return len(self.heap)

    #Mengecek apakah heap kosong
    def is_empty(self):
        return len(self.heap) == 0

    #Fungsi navigasi index pada heap
    #Menghitung index parent dari node pada index i
    def _parent(self, i):
        return (i - 1) // 2

    #Menghitung index anak kiri dari node pada index i
    def _left_child(self, i):
        return 2 * i + 1

    #Menghitung index anak kanan dari node pada index i
    def _right_child(self, i):
        return 2 * i + 2

    #Mengecek apakah node pada index i punya anak kiri
    def _has_left(self, i):
        return self._left_child(i) < len(self.heap)

    #Mengecek apakah node pada index i punya anak kanan
    def _has_right(self, i):
        return self._right_child(i) < len(self.heap)

    #Operasi dasar heap
    #Menukar posisi dua elemen dalam heap
    def _swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    #Upheap: Memperbaiki heap property dari bawah ke atas
    #Dipanggil setelah insert elemen baru di akhir array
    def _upheap(self, i):
        #Selama belum sampai root dan elemen lebih kecil dari parentnya
        while i > 0:
            parent = self._parent(i)
            if self.heap[i] < self.heap[parent]:
                self._swap(i, parent)  #Tukar dengan parent
                i = parent             #Lanjut ke posisi parent
            else:
                break  #Heap property sudah terpenuhi

    #Downheap: Memperbaiki heap property dari atas ke bawah
    #Dipanggil setelah root dihapus dan diganti elemen terakhir
    def _downheap(self, i):
        #Selama masih punya anak kiri (berarti belum leaf)
        while self._has_left(i):
            left = self._left_child(i)
            smallest = left  #Asumsikan anak kiri yang terkecil

            #Jika anak kanan ada dan lebih kecil, pilih anak kanan
            if self._has_right(i):
                right = self._right_child(i)
                if self.heap[right] < self.heap[left]:
                    smallest = right

            #Jika anak terkecil lebih kecil dari node saat ini, tukar
            if self.heap[smallest] < self.heap[i]:
                self._swap(i, smallest)
                i = smallest  #Lanjut ke posisi anak
            else:
                break  #Heap property sudah terpenuhi

    #Operasi publik heap
    #Menambahkan elemen baru ke heap
    def insert(self, item):
        self.heap.append(item)            #Tambahkan di akhir array
        self._upheap(len(self.heap) - 1)  #Perbaiki posisi ke atas

    #Melihat elemen minimum (root) tanpa menghapus
    def peek_min(self):
        if self.is_empty():
            raise IndexError("Heap kosong, tidak ada elemen minimum.")
        return self.heap[0]

    #Mengambil dan menghapus elemen minimum (root) dari heap
    def extract_min(self):
        if self.is_empty():
            raise IndexError("Heap kosong, tidak bisa extract.")

        #Tukar root dengan elemen terakhir
        self._swap(0, len(self.heap) - 1)
        #Hapus elemen terakhir (yang tadinya root/minimum)
        min_item = self.heap.pop()

        #Perbaiki heap dari root ke bawah jika masih ada elemen
        if not self.is_empty():
            self._downheap(0)

        return min_item

    #Menampilkan isi heap dalam format yang mudah dibaca
    def display(self):
        if self.is_empty():
            return "[kosong]"
        items = []
        for job in self.heap:
            items.append(f"{job.name}(p={job.priority}, rem={job.remaining})")
        return ", ".join(items)


#CLASS CPU SCHEDULER
#Mengatur penjadwalan job pada CPU secara non-preemptive
class CPUScheduler:
    def __init__(self):
        self.ready_queue = BinaryHeap()  #Heap untuk job yang menunggu
        self.current_job = None          #Job yang sedang berjalan di CPU
        self.time_slice = 0              #Nomor time slice saat ini
        self.arrival_counter = 0         #Counter untuk urutan kedatangan
        self.history = []                #Riwayat nama job per time slice
        self.completed_jobs = []         #Daftar job yang sudah selesai

    #Menambahkan job baru ke ready queue
    def add_job(self, name, length, priority):
        #Validasi input
        if not (-20 <= priority <= 19):
            raise ValueError(f"Priority harus antara -20 dan 19, diterima: {priority}")
        if not (1 <= length <= 100):
            raise ValueError(f"Length harus antara 1 dan 100, diterima: {length}")

        #Buat objek Job dan masukkan ke heap
        job = Job(name, length, priority, self.arrival_counter)
        self.arrival_counter += 1
        self.ready_queue.insert(job)

    #Menjalankan satu time slice pada CPU
    def run_one_slice(self):
        self.time_slice += 1

        #Jika CPU kosong (idle), ambil job dengan priority tertinggi dari heap
        if self.current_job is None and not self.ready_queue.is_empty():
            self.current_job = self.ready_queue.extract_min()

        #Jika tetap tidak ada job, CPU idle
        if self.current_job is None:
            self.history.append("idle")
            return "idle"

        #Jalankan job aktif selama 1 time slice
        running_name = self.current_job.name
        self.history.append(running_name)
        self.current_job.remaining -= 1

        #Jika job selesai (remaining = 0), bebaskan CPU
        if self.current_job.remaining == 0:
            self.completed_jobs.append(self.current_job.name)
            self.current_job = None

        return running_name

    #Mengecek apakah masih ada pekerjaan yang belum selesai
    def has_pending_work(self):
        return self.current_job is not None or not self.ready_queue.is_empty()


#FUNGSI PARSING COMMAND
#Mengubah string input menjadi aksi yang bisa diproses scheduler
def parse_command(text):
    text = text.strip()

    #Cek apakah command "no new job this slice"
    if text.lower() == "no new job this slice":
        return ("none",)

    #Cek apakah command format "add job NAME with length N and priority P"
    #Parsing manual tanpa regex untuk kesederhanaan
    lower = text.lower()
    if lower.startswith("add "):
        #Pisahkan berdasarkan kata kunci
        try:
            #Format: add <nama> with length <n> and priority <p>
            parts = text.split()

            #Cari posisi kata kunci "with", "length", "and", "priority"
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

            #Validasi bahwa semua kata kunci ditemukan
            if None in (idx_with, idx_length, idx_and, idx_priority):
                raise ValueError("Format command tidak valid.")

            #Ekstrak nama job (antara "add" dan "with")
            name = " ".join(parts[1:idx_with])
            if not name:
                raise ValueError("Nama job tidak boleh kosong.")

            #Ekstrak length (setelah "length")
            length = int(parts[idx_length + 1])

            #Ekstrak priority (setelah "priority")
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


#FUNGSI UTAMA
def main():
    print("                 CPU JOB SCHEDULING SIMULATOR")
    print("            Priority Queue dengan Binary Min-Heap")
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

    #Membaca jumlah command dari user
    try:
        n = int(input("Masukkan jumlah command: "))
        if n < 0:
            print("Jumlah command tidak boleh negatif.")
            return
    except ValueError:
        print("Input harus berupa bilangan bulat.")
        return

    #Membaca setiap command
    commands = []
    print()
    for i in range(1, n + 1):
        cmd = input(f"  Command {i}: ")
        commands.append(cmd)

    #Membuat scheduler dan menjalankan simulasi
    scheduler = CPUScheduler()

    print()
    print("                 HASIL SIMULASI")

    #Proses semua command yang diberikan user
    cmd_index = 0
    while cmd_index < len(commands) or scheduler.has_pending_work():
        #Ambil command berikutnya, atau "no new job" jika sudah habis
        if cmd_index < len(commands):
            cmd_text = commands[cmd_index]
            cmd_index += 1
        else:
            cmd_text = "no new job this slice"

        #Parse dan proses command
        try:
            parsed = parse_command(cmd_text)
        except ValueError as e:
            print(f"\n  [ERROR] {e}")
            return

        #Jika ada job baru, tambahkan ke ready queue
        if parsed[0] == "add":
            _, name, length, priority = parsed
            try:
                scheduler.add_job(name, length, priority)
            except ValueError as e:
                print(f"\n  [ERROR] {e}")
                return

        #Jalankan satu time slice
        running = scheduler.run_one_slice()

        #Tampilkan output sesuai format yang diminta
        print(f"  Time slice {scheduler.time_slice}: {running}")

    #Tampilkan ringkasan
    print()
    print("                     RINGKASAN")
    print(f"  Total time slices  : {scheduler.time_slice}")
    print(f"  Jobs selesai       : {len(scheduler.completed_jobs)}")
    print(f"  Urutan selesai     : {', '.join(scheduler.completed_jobs) if scheduler.completed_jobs else '(tidak ada)'}")
    print(f"  Timeline CPU       : {' -> '.join(scheduler.history)}")

#Jalankan program
if __name__ == "__main__":
    main()