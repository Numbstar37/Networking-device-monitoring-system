import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import platform
import ipaddress

class NetworkMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Device Monitor")
        self.root.geometry("760x500")
        self.root.minsize(650, 420)
        self.devices = []

        title = tk.Label(
            root, text="NETWORK DEVICE MONITOR",
            font=("Segoe UI", 20, "bold"), fg="#17365D"
        )
        title.pack(pady=(18, 4))

        subtitle = tk.Label(
            root, text="A simple tool to check whether network devices are reachable",
            font=("Segoe UI", 10), fg="#555555"
        )
        subtitle.pack(pady=(0, 15))

        form = ttk.Frame(root, padding=10)
        form.pack(fill="x", padx=20)

        ttk.Label(form, text="Device name:").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = ttk.Entry(form, width=22)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="IP address:").grid(row=0, column=2, padx=5, pady=5)
        self.ip_entry = ttk.Entry(form, width=18)
        self.ip_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(form, text="Add Device", command=self.add_device).grid(
            row=0, column=4, padx=8, pady=5
        )

        columns = ("name", "ip", "status")
        self.table = ttk.Treeview(root, columns=columns, show="headings", height=12)
        self.table.heading("name", text="DEVICE NAME")
        self.table.heading("ip", text="IP ADDRESS")
        self.table.heading("status", text="STATUS")
        self.table.column("name", width=240)
        self.table.column("ip", width=200)
        self.table.column("status", width=180, anchor="center")
        self.table.tag_configure("online", foreground="#168044")
        self.table.tag_configure("offline", foreground="#C0392B")
        self.table.pack(fill="both", expand=True, padx=25, pady=12)

        buttons = ttk.Frame(root, padding=8)
        buttons.pack(pady=5)

        ttk.Button(buttons, text="Check All Devices", command=self.check_all).grid(
            row=0, column=0, padx=8
        )
        ttk.Button(buttons, text="Remove Selected", command=self.remove_device).grid(
            row=0, column=1, padx=8
        )
        ttk.Button(buttons, text="Clear All", command=self.clear_all).grid(
            row=0, column=2, padx=8
        )

        self.summary = tk.Label(
            root, text="Devices: 0    Online: 0    Offline: 0",
            font=("Segoe UI", 10, "bold"), fg="#17365D"
        )
        self.summary.pack(pady=(5, 12))

        # Localhost is included as a reliable example for the first demonstration.
        self.devices.append({"name": "This Computer", "ip": "127.0.0.1", "status": "Not checked"})
        self.refresh_table()

    def add_device(self):
        name = self.name_entry.get().strip()
        ip = self.ip_entry.get().strip()

        if not name or not ip:
            messagebox.showwarning("Missing information", "Enter both a device name and an IP address.")
            return

        try:
            ipaddress.ip_address(ip)
        except ValueError:
            messagebox.showerror("Invalid IP", "Please enter a valid IPv4 or IPv6 address.")
            return

        if any(device["ip"] == ip for device in self.devices):
            messagebox.showwarning("Duplicate device", "That IP address is already being monitored.")
            return

        self.devices.append({"name": name, "ip": ip, "status": "Not checked"})
        self.name_entry.delete(0, tk.END)
        self.ip_entry.delete(0, tk.END)
        self.refresh_table()

    def ping_device(self, ip):
        system = platform.system().lower()
        if system == "windows":
            command = ["ping", "-n", "1", "-w", "1000", ip]
        else:
            command = ["ping", "-c", "1", "-W", "1", ip]

        try:
            result = subprocess.run(
                command, stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL, timeout=3
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False

    def check_all(self):
        if not self.devices:
            messagebox.showinfo("No devices", "Add a device before checking the network.")
            return

        self.root.config(cursor="watch")
        self.root.update_idletasks()

        for device in self.devices:
            device["status"] = "Online" if self.ping_device(device["ip"]) else "Offline"

        self.root.config(cursor="")
        self.refresh_table()

    def remove_device(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo("Select a device", "Select a device from the table first.")
            return

        # Treeview item IDs are the device list indexes.
        indexes = sorted((int(item) for item in selected), reverse=True)
        for index in indexes:
            if 0 <= index < len(self.devices):
                self.devices.pop(index)
        self.refresh_table()

    def clear_all(self):
        if not self.devices:
            return
        if messagebox.askyesno("Confirm", "Remove all monitored devices?"):
            self.devices.clear()
            self.refresh_table()

    def refresh_table(self):
        for item in self.table.get_children():
            self.table.delete(item)

        for index, device in enumerate(self.devices):
            tag = device["status"].lower() if device["status"] in ("Online", "Offline") else ""
            self.table.insert(
                "", "end", iid=str(index),
                values=(device["name"], device["ip"], device["status"]),
                tags=(tag,)
            )

        online = sum(d["status"] == "Online" for d in self.devices)
        offline = sum(d["status"] == "Offline" for d in self.devices)
        self.summary.config(
            text=f"Devices: {len(self.devices)}    Online: {online}    Offline: {offline}"
        )

if __name__ == "__main__":
    window = tk.Tk()
    app = NetworkMonitor(window)
    window.mainloop()
