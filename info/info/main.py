import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import sqlite3
import os
import shutil


ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"


conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT,
        image_path TEXT
    )
''')
conn.commit()


root = tk.Tk()
root.title("User Registration & Search")
root.geometry("600x750")

is_dark_mode = False

def apply_theme():
    if is_dark_mode:
        bg = "#2c2c2c"
        fg = "white"
        entry_bg = "#3c3c3c"
        result_bg = "#3b3b3b"
        btn_bg = "#444444"
        btn_fg = "white"
    else:
        bg = "#ff4e50"
        fg = "white"
        entry_bg = "white"
        result_bg = "#fff0e5"
        btn_bg = "#43cea2"
        btn_fg = "white"

    root.configure(bg=bg)
    for widget in root.winfo_children():
        if isinstance(widget, tk.Label) or isinstance(widget, tk.LabelFrame):
            widget.configure(bg=bg, fg=fg)
        elif isinstance(widget, tk.Entry):
            widget.configure(bg=entry_bg, fg="black")
        elif isinstance(widget, tk.Button):
            if widget["text"] == "Search":
                widget.configure(bg="#f7971e", fg=btn_fg)
            elif widget["text"] == "Choose Image":
                widget.configure(bg="#00c9ff", fg=btn_fg)
            else:
                widget.configure(bg=btn_bg, fg=btn_fg)
    result_frame.configure(bg=result_bg)
    result_name.configure(bg=result_bg, fg="black")
    result_id.configure(bg=result_bg, fg="black")
    result_photo.configure(bg=result_bg)

def toggle_theme():
    global is_dark_mode
    is_dark_mode = not is_dark_mode
    apply_theme()


theme_btn = tk.Button(root, text="Change Theme", command=toggle_theme, font=("Arial", 10))
theme_btn.place(x=450, y=10)

tk.Label(root, text="Name:", font=("Arial", 14)).place(x=50, y=50)
entry_name = tk.Entry(root, font=("Arial", 14), width=25)
entry_name.place(x=150, y=50)

tk.Label(root, text="ID:", font=("Arial", 14)).place(x=50, y=100)
entry_id = tk.Entry(root, font=("Arial", 14), width=25)
entry_id.place(x=150, y=100)

tk.Label(root, text="Photo:", font=("Arial", 14)).place(x=50, y=150)
photo_label = tk.Label(root)
photo_label.place(x=150, y=150)

image_path = None

def choose_image():
    global image_path
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png")])
    if file_path:
        image_path = file_path
        img = Image.open(file_path).resize((100, 100))
        img = ImageTk.PhotoImage(img)
        photo_label.configure(image=img)
        photo_label.image = img

tk.Button(root, text="Choose Image", command=choose_image, font=("Arial", 12)).place(x=280, y=150)

def submit():
    name = entry_name.get()
    user_id = entry_id.get()
    global image_path
    if not (name and user_id and image_path):
        messagebox.showwarning("Missing Info", "Please fill all fields and choose an image.")
        return

    save_dir = "images"
    os.makedirs(save_dir, exist_ok=True)
    image_filename = os.path.join(save_dir, f"{user_id}.png")
    shutil.copy(image_path, image_filename)

    try:
        cursor.execute("INSERT INTO users (id, name, image_path) VALUES (?, ?, ?)", (user_id, name, image_filename))
        conn.commit()
        messagebox.showinfo("Success", "User data saved successfully.")
        entry_name.delete(0, tk.END)
        entry_id.delete(0, tk.END)
        photo_label.config(image="")
        photo_label.image = None
        image_path = None
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "User ID already exists.")

tk.Button(root, text="Submit", command=submit, font=("Arial", 14), width=10).place(x=150, y=250)


tk.Label(root, text="Search by ID or Name:", font=("Arial", 14)).place(x=50, y=370)
search_entry = tk.Entry(root, font=("Arial", 14), width=20)
search_entry.place(x=250, y=370)


result_frame = tk.LabelFrame(root, text="User Info", font=("Arial", 12, "bold"), width=500, height=200)
result_frame.place(x=50, y=420)

result_name = tk.Label(result_frame, text="Name: ", font=("Arial", 13))
result_name.place(x=20, y=20)

result_id = tk.Label(result_frame, text="ID: ", font=("Arial", 13))
result_id.place(x=20, y=50)

result_photo = tk.Label(result_frame)
result_photo.place(x=300, y=10)


def delete_user():
    uid = current_result.get("id", None)
    if not uid:
        messagebox.showwarning("No User", "Search and select a user first.")
        return

    username = simpledialog.askstring("Admin Login", "Enter admin username:")
    password = simpledialog.askstring("Admin Login", "Enter admin password:", show="*")

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        cursor.execute("DELETE FROM users WHERE id = ?", (uid,))
        conn.commit()
        if os.path.exists(current_result.get("image_path", "")):
            os.remove(current_result["image_path"])
        messagebox.showinfo("Deleted", f"User '{uid}' deleted.")
        result_name.config(text="Name: ")
        result_id.config(text="ID: ")
        result_photo.config(image="")
        result_photo.image = None
        current_result.clear()
    else:
        messagebox.showerror("Unauthorized", "Invalid admin credentials.")

delete_btn = tk.Button(root, text="Delete User", command=delete_user, font=("Arial", 12), width=12)
delete_btn.place(x=230, y=640)


current_result = {}

def search():
    query = search_entry.get().strip()
    if not query:
        messagebox.showwarning("Input Required", "Please enter an ID or Name to search.")
        return

    cursor.execute("SELECT id, name, image_path FROM users WHERE id = ? OR name = ?", (query, query))
    result = cursor.fetchone()
    if result:
        result_name.config(text="Name: " + result[1])
        result_id.config(text="ID: " + result[0])
        current_result["id"] = result[0]
        current_result["name"] = result[1]
        current_result["image_path"] = result[2]
        if os.path.exists(result[2]):
            img = Image.open(result[2]).resize((100, 100))
            img = ImageTk.PhotoImage(img)
            result_photo.config(image=img)
            result_photo.image = img
        else:
            result_photo.config(image="")
            result_photo.image = None
    else:
        messagebox.showinfo("Not Found", "User not found.")
        result_name.config(text="Name: ")
        result_id.config(text="ID: ")
        result_photo.config(image="")
        result_photo.image = None
        current_result.clear()

tk.Button(root, text="Search", command=search, font=("Arial", 12), width=10).place(x=460, y=365)


apply_theme()

root.mainloop()
