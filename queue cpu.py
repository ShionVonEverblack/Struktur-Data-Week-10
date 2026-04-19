"""
CPU job scheduling simulator using a manual binary min-heap.

Example input:
5
add job A with length 3 and priority 2
add job B with length 1 and priority -5
no new job this slice
add job C with length 2 and priority 0
no new job this slice

Example output:
Time slice 1: A
Time slice 2: A
Time slice 3: A
Time slice 4: B
Time slice 5: C
Time slice 6: C
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field


ADD_JOB_PATTERN = re.compile(
    r"^add job (.+) with length (-?\d+) and priority (-?\d+)$"
)


@dataclass
class Job:
    """Represent a CPU job with priority and required time slices."""

    name: str
    priority: int
    length: int
    arrival_order: int
    remaining_time: int = field(init=False)

    def __post_init__(self) -> None:
        if not -20 <= self.priority <= 19:
            raise ValueError("Priority must be between -20 and 19.")
        if not 1 <= self.length <= 100:
            raise ValueError("Length must be between 1 and 100.")
        if not self.name:
            raise ValueError("Job name cannot be empty.")
        self.remaining_time = self.length

    def __lt__(self, other: "Job") -> bool:
        """Compare jobs for min-heap ordering."""
        return (self.priority, self.arrival_order) < (
            other.priority,
            other.arrival_order,
        )


class BinaryHeapPriorityQueue:
    """Min-heap priority queue implemented without heapq."""

    def __init__(self) -> None:
        """Create an empty priority queue."""
        self._data: list[Job] = []

    def __len__(self) -> int:
        """Return the number of jobs in the queue."""
        return len(self._data)

    def is_empty(self) -> bool:
        """Return True if the queue is empty."""
        return len(self._data) == 0

    def add(self, job: Job) -> None:
        """Insert a job into the heap."""
        self._data.append(job)
        self._upheap(len(self._data) - 1)

    def peek(self) -> Job:
        """Return the minimum job without removing it."""
        if self.is_empty():
            raise IndexError("Priority queue is empty.")
        return self._data[0]

    def min(self) -> Job:
        """Alias for peek()."""
        return self.peek()

    def remove_min(self) -> Job:
        """Remove and return the minimum job from the heap."""
        if self.is_empty():
            raise IndexError("Priority queue is empty.")
        self._swap(0, len(self._data) - 1)
        job = self._data.pop()
        if not self.is_empty():
            self._downheap(0)
        return job

    def _parent(self, index: int) -> int:
        """Return the parent index of a node."""
        return (index - 1) // 2

    def _left(self, index: int) -> int:
        """Return the left child index of a node."""
        return 2 * index + 1

    def _right(self, index: int) -> int:
        """Return the right child index of a node."""
        return 2 * index + 2

    def _has_left(self, index: int) -> bool:
        return self._left(index) < len(self._data)

    def _has_right(self, index: int) -> bool:
        return self._right(index) < len(self._data)

    def _swap(self, i: int, j: int) -> None:
        """Swap two positions in the heap array."""
        self._data[i], self._data[j] = self._data[j], self._data[i]

    def _upheap(self, index: int) -> None:
        """Move a node upward until heap order is restored."""
        while index > 0:
            parent = self._parent(index)
            if self._data[index] < self._data[parent]:
                self._swap(index, parent)
                index = parent
            else:
                break

    def _downheap(self, index: int) -> None:
        """Move a node downward until heap order is restored."""
        while self._has_left(index):
            left = self._left(index)
            small_child = left

            if self._has_right(index):
                right = self._right(index)
                if self._data[right] < self._data[left]:
                    small_child = right

            if self._data[small_child] < self._data[index]:
                self._swap(index, small_child)
                index = small_child
            else:
                break


class Scheduler:
    """Manage non-preemptive CPU scheduling per time slice."""

    def __init__(self) -> None:
        """Create a scheduler with an empty ready queue."""
        self.queue = BinaryHeapPriorityQueue()
        self.current_job: Job | None = None
        self._next_arrival_order = 0

    def process_time_slice(self, command: str) -> str:
        """Process one time slice and return the running job name."""
        new_job = self._parse_command(command)
        if new_job is not None:
            self.queue.add(new_job)

        if self.current_job is None and not self.queue.is_empty():
            self.current_job = self.queue.remove_min()

        running_name = "idle" if self.current_job is None else self.current_job.name

        if self.current_job is not None:
            self.current_job.remaining_time -= 1
            if self.current_job.remaining_time == 0:
                self.current_job = None

        return running_name

    def has_pending_work(self) -> bool:
        """Return True if CPU or queue still has unfinished jobs."""
        return self.current_job is not None or not self.queue.is_empty()

    def _parse_command(self, command: str) -> Job | None:
        """Parse a command for a time slice."""
        text = command.strip()

        if text == "no new job this slice":
            return None

        match = ADD_JOB_PATTERN.fullmatch(text)
        if match is None:
            raise ValueError(f"Invalid command: {command}")

        name = match.group(1).strip()
        length = int(match.group(2))
        priority = int(match.group(3))

        job = Job(
            name=name,
            priority=priority,
            length=length,
            arrival_order=self._next_arrival_order,
        )
        self._next_arrival_order += 1
        return job


def read_commands() -> list[str]:
    """Read T commands from standard input."""
    first_line = sys.stdin.readline()
    if first_line == "":
        return []

    first_line = first_line.strip()
    if not first_line:
        raise ValueError("First line must contain T.")

    try:
        total_slices = int(first_line)
    except ValueError as error:
        raise ValueError("T must be an integer.") from error

    if total_slices < 0:
        raise ValueError("T must be non-negative.")

    commands: list[str] = []
    for index in range(1, total_slices + 1):
        command = sys.stdin.readline()
        if command == "":
            raise ValueError(f"Missing command for time slice {index}.")
        commands.append(command.strip())

    return commands


def simulate(commands: list[str]) -> list[str]:
    """Run the scheduler and return output lines."""
    scheduler = Scheduler()
    output_lines: list[str] = []
    time_slice = 1

    for command in commands:
        running_name = scheduler.process_time_slice(command)
        output_lines.append(f"Time slice {time_slice}: {running_name}")
        time_slice += 1

    while scheduler.has_pending_work():
        running_name = scheduler.process_time_slice("no new job this slice")
        output_lines.append(f"Time slice {time_slice}: {running_name}")
        time_slice += 1

    return output_lines


def main() -> None:
    """Entry point of the program."""
    try:
        commands = read_commands()
        results = simulate(commands)
        if results:
            print("\n".join(results))
    except ValueError as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()

# Kompleksitas:
# add = O(log n)
# peek/min = O(1)
# remove_min = O(log n)
# is_empty = O(1)
# len = O(1)