"""
Student Performance Analysis System
-----------------------------------
Loads student records from a CSV file, calculates performance metrics,
identifies scholarship-eligible students and generates performance reports.

OOP concepts demonstrated:
  - Classes & objects      : Student, AIUStudent, ScholarshipStudent, PerformanceAnalyzer
  - Encapsulation          : protected (_) / private (__) attributes + properties
  - Abstraction            : Student is an abstract base class with abstract describe()
  - Inheritance            : AIUStudent -> Student, ScholarshipStudent -> AIUStudent
  - Method overriding      : describe() and generate_report() overridden in ScholarshipStudent
  - Polymorphism           : mixed list of students, describe() called in a loop
  - Flexible interfaces    : calculate_average(*marks) (Python's "overloading")
  - Composition            : PerformanceAnalyzer works WITH Student objects
"""

import csv
from abc import ABC, abstractmethod

SCHOLARSHIP_THRESHOLD = 85      # minimum average for scholarship eligibility
DEFAULT_SCHOLARSHIP = 50000     # scholarship amount awarded to eligible students


# ----------------------------------------------------------------------
# Task 2: Base class (encapsulation + abstraction)
# ----------------------------------------------------------------------
class Student(ABC):
    """Abstract base class for all students."""

    def __init__(self, student_id, first_name, last_name, programme, marks):
        # Protected attributes (single underscore): for use inside the class
        # and its subclasses.
        self._student_id = student_id
        self._first_name = first_name
        self._last_name = last_name
        self._programme = programme
        # Private attribute (double underscore): name-mangled, hidden from
        # outside code. Marks can only change through set_mark().
        self.__marks = {}
        for subject, mark in marks.items():
            self.set_mark(subject, mark)

    # ---- Getters (read-only access via properties) ----
    @property
    def student_id(self):
        return self._student_id

    @property
    def first_name(self):
        return self._first_name

    @property
    def last_name(self):
        return self._last_name

    @property
    def full_name(self):
        return f"{self._first_name} {self._last_name}"

    @property
    def programme(self):
        return self._programme

    @property
    def marks(self):
        # Return a COPY so outsiders cannot modify the private dict directly.
        return dict(self.__marks)

    # ---- Controlled update with validation ----
    def set_mark(self, subject, mark):
        """Add or update a subject mark (must be a number from 0 to 100)."""
        self._validate_mark(mark)
        self.__marks[subject] = mark

    @staticmethod
    def _validate_mark(mark):
        if isinstance(mark, bool) or not isinstance(mark, (int, float)):
            raise TypeError(f"Mark must be a number, got {mark!r}")
        if not 0 <= mark <= 100:
            raise ValueError(f"Mark must be between 0 and 100, got {mark}")

    # ---- Task 6: flexible interface (equivalent of method overloading) ----
    def calculate_average(self, *marks):
        """
        Calculate an average.
          calculate_average()              -> average of this student's own marks
          calculate_average(70, 80, 90)    -> average of three marks
          calculate_average(70, 80, 90, 65, 55) -> average of ANY number of marks

        *marks collects however many positional arguments are given, so one
        method supports several call styles. Every mark is validated.
        """
        values = marks if marks else tuple(self.__marks.values())
        if not values:
            raise ValueError("No marks available to calculate an average")
        for mark in values:
            self._validate_mark(mark)
        return round(sum(values) / len(values), 2)

    @property
    def average(self):
        return self.calculate_average()

    def get_grade(self):
        """Convert the average into a letter grade."""
        avg = self.average
        if avg >= 80:
            return "A"
        if avg >= 70:
            return "B"
        if avg >= 60:
            return "C"
        if avg >= 50:
            return "D"
        return "F"

    # ---- Abstract method: every subclass MUST implement it ----
    @abstractmethod
    def describe(self):
        """Return a one-line description appropriate to the student type."""

    # ---- Task 7: individual report ----
    def generate_report(self):
        lines = [
            f"Student ID : {self.student_id}",
            f"Name       : {self.full_name}",
            f"Programme  : {self.programme}",
            "Marks      : " + ", ".join(f"{s} = {m}" for s, m in self.__marks.items()),
            f"Average    : {self.average}",
            f"Grade      : {self.get_grade()}",
        ]
        return "\n".join(lines)

    def __str__(self):
        return f"{self.student_id} {self.full_name} (avg {self.average})"


class AIUStudent(Student):
    """A regular student. Implements the abstract describe() method."""

    def describe(self):
        return f"{self.full_name} is a regular {self.programme} student with grade {self.get_grade()}."


# ----------------------------------------------------------------------
# Task 4: Inheritance and method overriding
# ----------------------------------------------------------------------
class ScholarshipStudent(AIUStudent):
    """A student who holds (or may qualify for) a scholarship."""

    def __init__(self, student_id, first_name, last_name, programme, marks,
                 scholarship_amount=DEFAULT_SCHOLARSHIP):
        # super() reuses the parent constructor instead of repeating its code.
        super().__init__(student_id, first_name, last_name, programme, marks)
        self.scholarship_amount = scholarship_amount

    def is_eligible(self):
        return self.average >= SCHOLARSHIP_THRESHOLD

    # Overridden: same name as the parent method, scholarship-specific behaviour
    def describe(self):
        status = "ELIGIBLE" if self.is_eligible() else "NOT eligible"
        return (f"{self.full_name} is a scholarship student ({status}), "
                f"award: {self.scholarship_amount:,}.")

    # Overridden: reuse the parent's report, then extend it
    def generate_report(self):
        base = super().generate_report()
        status = "Eligible" if self.is_eligible() else "Not eligible"
        return base + f"\nScholarship: {status} (amount: {self.scholarship_amount:,})"


# ----------------------------------------------------------------------
# Task 3: PerformanceAnalyzer (composition)
# ----------------------------------------------------------------------
class PerformanceAnalyzer:
    """Analyses a collection of Student objects (no data is duplicated)."""

    def __init__(self, students):
        if not students:
            raise ValueError("At least one student is required")
        self._students = students   # references to the same objects

    def highest_average(self):
        return max(self._students, key=lambda s: s.average)

    def lowest_average(self):
        return min(self._students, key=lambda s: s.average)

    def class_average(self):
        return round(sum(s.average for s in self._students) / len(self._students), 2)

    # ---- Task 7: full report with class summary ----
    def generate_report(self):
        line = "=" * 55
        parts = [line, "STUDENT PERFORMANCE REPORT", line]
        for student in self._students:
            parts.append(student.generate_report())
            parts.append("-" * 55)
        top, bottom = self.highest_average(), self.lowest_average()
        parts += [
            "CLASS PERFORMANCE SUMMARY",
            f"Highest average : {top.full_name} ({top.average})",
            f"Lowest average  : {bottom.full_name} ({bottom.average})",
            f"Class average   : {self.class_average()}",
            line,
        ]
        return "\n".join(parts)


# ----------------------------------------------------------------------
# CSV loading
# ----------------------------------------------------------------------
def load_students(filename):
    """
    Read students from a CSV file. Students whose average reaches the
    scholarship threshold become ScholarshipStudent objects; the rest are
    AIUStudent objects.
    """
    students = []
    with open(filename, newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            marks = {"Math": float(row["Math"]),
                     "English": float(row["English"]),
                     "Science": float(row["Science"])}
            args = (row["StudentID"], row["FName"], row["LName"], row["Programme"], marks)
            if sum(marks.values()) / len(marks) >= SCHOLARSHIP_THRESHOLD:
                students.append(ScholarshipStudent(*args))
            else:
                students.append(AIUStudent(*args))
    return students


# ----------------------------------------------------------------------
# Main program / demonstrations
# ----------------------------------------------------------------------
def main():
    students = load_students("students.csv")

    # Task 5: Polymorphism - one list, two types, one method name.
    print("POLYMORPHISM DEMO: describe()")
    for student in students:
        # Python picks AIUStudent.describe or ScholarshipStudent.describe
        # depending on the actual object type at run time.
        print(f"  [{type(student).__name__}] {student.describe()}")

    # Task 6: flexible interface demo
    print("\nFLEXIBLE INTERFACE DEMO: calculate_average()")
    sample = students[0]
    print("  Own marks            :", sample.calculate_average())
    print("  Three marks (70,80,90):", sample.calculate_average(70, 80, 90))
    print("  Five marks           :", sample.calculate_average(70, 80, 90, 65, 55))
    try:
        sample.calculate_average(70, 150)
    except ValueError as error:
        print("  Validation caught    :", error)

    # Task 4: ScholarshipStudent inherits and extends
    print("\nINHERITANCE DEMO")
    for student in students:
        if isinstance(student, ScholarshipStudent):
            print(f"  {student.full_name}: eligible = {student.is_eligible()}, "
                  f"grade (inherited) = {student.get_grade()}")

    # Task 7: reports
    print()
    print(PerformanceAnalyzer(students).generate_report())


if __name__ == "__main__":
    main()