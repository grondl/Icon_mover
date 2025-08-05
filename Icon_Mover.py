#!/usr/bin/env python3


import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import os
import subprocess

DESKTOP_DIR = os.path.expanduser("~/Desktop")
ICON_RADIUS = 6

class IconDot:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.dragging = False

class IconLayoutWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Desktop Icon Layout")
        self.set_default_size(1000, 600)
        self.set_resizable(True)

        self.dots = []
        self.screens = []
        self.scale = 1
        self.virtual_width = 1
        self.virtual_height = 1
        self.selected_dot = None
        self.offset_x = 0
        self.offset_y = 0

        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                                     Gdk.EventMask.BUTTON_RELEASE_MASK |
                                     Gdk.EventMask.POINTER_MOTION_MASK)
        self.drawing_area.connect("draw", self.on_draw)
        self.drawing_area.connect("button-press-event", self.on_button_press)
        self.drawing_area.connect("motion-notify-event", self.on_motion)
        self.drawing_area.connect("button-release-event", self.on_button_release)

        self.add(self.drawing_area)
        self.connect("destroy", Gtk.main_quit)
        self.connect("size-allocate", self.on_resize)

        self.detect_screens()
        self.load_dots()

    def detect_screens(self):
        self.screens.clear()
        display = Gdk.Display.get_default()
        monitor_count = display.get_n_monitors()

        min_x = 0
        min_y = 0
        max_x = 1
        max_y = 1

        for i in range(monitor_count):
            monitor = display.get_monitor(i)
            geometry = monitor.get_geometry()
            scale_factor = monitor.get_scale_factor()

            x = geometry.x
            y = geometry.y
            w = geometry.width
            h = geometry.height
            self.screens.append((x, y, w, h))

            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x + w)
            max_y = max(max_y, y + h)

        self.virtual_width = max_x - min_x
        self.virtual_height = max_y - min_y

    def load_dots(self):
        self.dots.clear()
        for entry in os.listdir(DESKTOP_DIR):
            path = os.path.join(DESKTOP_DIR, entry)
            if not os.path.isfile(path):
                continue

            try:
                result = subprocess.run(["gio", "info", "-a", "metadata::caja-icon-position", path],
                                        capture_output=True, text=True)
                for line in result.stdout.splitlines():
                    if "metadata::caja-icon-position:" in line:
                        pos = line.split("::caja-icon-position:")[1].strip()
                        x_str, y_str = pos.split(",")
                        x, y = int(x_str), int(y_str)
                        self.dots.append(IconDot(path, x, y))
            except Exception as e:
                print(f"Error reading position for {path}: {e}")

    def on_resize(self, widget, allocation):
        area_width = allocation.width
        area_height = allocation.height
        self.scale = min(area_width / self.virtual_width, area_height / self.virtual_height)
        self.drawing_area.queue_draw()

    def on_draw(self, widget, cr):
        cr.set_source_rgb(1, 1, 1)
        cr.paint()

        # Draw screens
        cr.set_line_width(2)
        for x, y, w, h in self.screens:
            cr.set_source_rgb(0.7, 0.7, 0.7)
            cr.rectangle(x * self.scale, y * self.scale, w * self.scale, h * self.scale)
            cr.stroke()

        # Draw icons
        for dot in self.dots:
            cr.set_source_rgb(0, 0, 1)
            cr.arc(dot.x * self.scale, dot.y * self.scale, ICON_RADIUS, 0, 2 * 3.1416)
            cr.fill()

    def on_button_press(self, widget, event):
        for dot in self.dots:
            dx = dot.x * self.scale - event.x
            dy = dot.y * self.scale - event.y
            if dx * dx + dy * dy <= ICON_RADIUS * ICON_RADIUS:
                dot.dragging = True
                self.selected_dot = dot
                self.offset_x = dx / self.scale
                self.offset_y = dy / self.scale
                break

    def on_motion(self, widget, event):
        if self.selected_dot and self.selected_dot.dragging:
            self.selected_dot.x = int(event.x / self.scale + self.offset_x)
            self.selected_dot.y = int(event.y / self.scale + self.offset_y)
            self.drawing_area.queue_draw()

    def on_button_release(self, widget, event):
        if self.selected_dot:
            self.selected_dot.dragging = False
            x, y = self.selected_dot.x, self.selected_dot.y
            subprocess.run(["gio", "set", "-t", "string", self.selected_dot.name,
                            "metadata::caja-icon-position", f"{x},{y}"])
            self.restart_caja()
            self.selected_dot = None

    def restart_caja(self):
        subprocess.run(["caja", "-q"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.Popen(["caja"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    win = IconLayoutWindow()
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()


