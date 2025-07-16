import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime


DEFAULT_FILE = "tasks.json"

class TaskDialog(simpledialog.Dialog):
    """Dialog for adding or editing a task."""
    def __init__(self, parent, title, task=None):
        self.task_data = task or {}
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text="Task description:").grid(row=0, column=0, sticky="w")
        self.description_var = tk.StringVar(value=self.task_data.get("description", ""))
        tk.Entry(master, textvariable=self.description_var, width=40).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(master, text="Priority (1‑5):").grid(row=1, column=0, sticky="w")
        self.priority_var = tk.IntVar(value=self.task_data.get("priority", 3))
        tk.Spinbox(master, from_=1, to=5, textvariable=self.priority_var, width=5).grid(row=1, column=1, sticky="w", padx=5)

        tk.Label(master, text="Due date (YYYY‑MM‑DD) – optional:").grid(row=2, column=0, sticky="w")
        self.due_var = tk.StringVar(value=self.task_data.get("due", ""))
        tk.Entry(master, textvariable=self.due_var, width=15).grid(row=2, column=1, sticky="w", padx=5)
        return master

    def validate(self):
        desc = self.description_var.get().strip()
        if not desc:
            messagebox.showwarning("Input error", "Description cannot be empty.")
            return False
        due = self.due_var.get().strip()
        if due:
            try:
                datetime.strptime(due, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Input error", "Due date must be YYYY‑MM‑DD or blank.")
                return False
        return True

    def apply(self):
        self.result = {
            "description": self.description_var.get().strip(),
            "priority": int(self.priority_var.get()),
            "due": self.due_var.get().strip(),
            "completed": self.task_data.get("completed", False),
        }


class TodoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("To‑Do List App")
        self.geometry("600x400")
        self.resizable(False, False)

        self.tasks = []  # list of dicts
        self._build_ui()
        self._load_tasks()
        self.protocol("WM_DELETE_WINDOW", self.on_exit)

    # ---------- UI ---------- #
    def _build_ui(self):
        columns = ("Description", "Priority", "Due", "Status")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            self.tree.heading(col, text=col)
            if col == "Description":
                self.tree.column(col, width=260)
            elif col == "Priority":
                self.tree.column(col, width=60, anchor="center")
            elif col == "Due":
                self.tree.column(col, width=90, anchor="center")
            else:
                self.tree.column(col, width=70, anchor="center")
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", pady=(0, 10))
        tk.Button(btn_frame, text="Add", width=10, command=self.add_task).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Edit", width=10, command=self.edit_task).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Delete", width=10, command=self.delete_task).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Toggle Done", width=10, command=self.toggle_complete).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Save", width=10, command=self._save_tasks).pack(side="right", padx=5)

    # ---------- CRUD operations ---------- #
    def add_task(self):
        dlg = TaskDialog(self, "Add Task")
        if dlg.result:
            self.tasks.append(dlg.result)
            self._refresh_tree()

    def edit_task(self):
        item = self._selected_item()
        if item is None:
            return
        idx = self.tree.index(item)
        task = self.tasks[idx]
        dlg = TaskDialog(self, "Edit Task", task)
        if dlg.result:
            self.tasks[idx] = dlg.result
            self._refresh_tree()

    def delete_task(self):
        item = self._selected_item()
        if item is None:
            return
        idx = self.tree.index(item)
        if messagebox.askyesno("Confirm", "Delete selected task?"):
            del self.tasks[idx]
            self._refresh_tree()

    def toggle_complete(self):
        item = self._selected_item()
        if item is None:
            return
        idx = self.tree.index(item)
        self.tasks[idx]["completed"] = not self.tasks[idx].get("completed", False)
        self._refresh_tree()

    # ---------- Helper functions ---------- #
    def _selected_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("No selection", "Please select a task first.")
            return None
        return selected[0]

    def _refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for task in sorted(self.tasks, key=lambda x: (x["completed"], x["priority"])):
            status = "✔" if task.get("completed") else "✗"
            values = (task["description"], task["priority"], task["due"], status)
            self.tree.insert("", "end", values=values)

    # ---------- File I/O ---------- #
    def _load_tasks(self):
        if os.path.exists(DEFAULT_FILE):
            try:
                with open(DEFAULT_FILE, "r", encoding="utf-8") as f:
                    self.tasks = json.load(f)
                self._refresh_tree()
            except Exception as e:
                messagebox.showerror("Error", f"Could not load tasks: {e}")

    def _save_tasks(self):
        try:
            with open(DEFAULT_FILE, "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, indent=2)
            messagebox.showinfo("Saved", "Tasks saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save tasks: {e}")

    def on_exit(self):
        # Auto‑save on exit
        self._save_tasks()
        self.destroy()


if __name__ == "__main__":
    TodoApp().mainloop()
