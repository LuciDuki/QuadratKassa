import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3

class VendingMachineGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Drink Vending Machine")
        self.root.attributes("-fullscreen", True)  # Make the window full screen

        self.db_connection = sqlite3.connect("user_data.db")
        self.create_user_table()
        self.load_users_from_db()

        self.current_user = None

        self.drinks = {
            "Cola": 1.5,
            "Water": 1.0,
            "Juice": 2.0
        }

        self.user_manager_button = tk.Button(root, text="User Manager", font=("Helvetica", 14), command=self.open_user_manager)
        self.user_manager_button.pack(side=tk.TOP, pady=10)

        self.user_buttons_frame = tk.Frame(root)
        self.user_buttons_frame.pack(pady=10)

        for username in self.users:
            user_button = tk.Button(self.user_buttons_frame, text=username, font=("Helvetica", 14), padx=20, pady=10,
                                    command=lambda u=username: self.select_user(u))
            user_button.pack(side=tk.LEFT, padx=10)

        self.user_manager_window = None

        self.user_interface_frame = tk.Frame(root)

        self.balance_label = tk.Label(self.user_interface_frame, text="Balance: $0.00", font=("Helvetica", 16))
        self.balance_label.pack(pady=10)

        self.drink_buttons_frame = tk.Frame(self.user_interface_frame)
        self.drink_buttons_frame.pack(pady=20)

        self.drink_buttons = []
        for drink in self.drinks:
            button = tk.Button(self.drink_buttons_frame, text=f"{drink} (${self.drinks[drink]:.2f})",
                               font=("Helvetica", 14), padx=20, pady=10,
                               command=lambda d=drink: self.purchase(d),
                               bg="#3498db", fg="white", activebackground="#2980b9")
            button.pack(side=tk.LEFT, padx=10)
            self.drink_buttons.append(button)

        self.button_frame = tk.Frame(self.user_interface_frame)
        self.button_frame.pack()

        self.add_money_button = tk.Button(self.button_frame, text="Add $0.50", font=("Helvetica", 14), padx=20, pady=10,
                                          command=self.add_money, bg="#27ae60", fg="white", activebackground="#219651")
        self.add_money_button.pack(side=tk.LEFT, padx=10)

        self.return_money_button = tk.Button(self.button_frame, text="Return Money", font=("Helvetica", 14), padx=20, pady=10,
                                             command=self.return_money, bg="#e74c3c", fg="white", activebackground="#c0392b")
        self.return_money_button.pack(side=tk.LEFT, padx=10)

        self.message_label = tk.Label(self.user_interface_frame, text="", font=("Helvetica", 14), wraplength=300)
        self.message_label.pack(pady=10)

        self.text_entry = tk.Entry(self.user_interface_frame, font=("Helvetica", 16))
        self.text_entry.pack(pady=10)

        self.create_keyboard()  # Create the QWERTZ software keyboard

        self.user_interface_frame.pack_forget()

    def create_user_table(self):
        with self.db_connection:
            self.db_connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    balance REAL
                )
                """
            )

    def load_users_from_db(self):
        self.users = {}
        with self.db_connection:
            cursor = self.db_connection.execute("SELECT username, balance FROM users")
            for row in cursor:
                self.users[row[0]] = {"balance": row[1], "purchases": []}
        
    def select_user(self, username):
        self.current_user = username
        self.update_interface()
    
    def login(self):
        if self.current_user:
            self.user_interface_frame.pack(pady=20)
        else:
            messagebox.showerror("Login Error", "Please select a user.")
    
    def open_user_manager(self):
        if self.user_manager_window is None or not self.user_manager_window.winfo_exists():
            self.user_manager_window = tk.Toplevel(self.root)
            self.user_manager_window.title("User Manager")
            
            self.user_listbox = tk.Listbox(self.user_manager_window, font=("Helvetica", 12), selectmode=tk.SINGLE)
            self.user_listbox.pack(pady=10)
            
            for username in self.users:
                self.user_listbox.insert(tk.END, username)
            
            self.add_user_button = tk.Button(self.user_manager_window, text="Add User", font=("Helvetica", 12), command=self.add_user)
            self.add_user_button.pack(pady=5)
            
            self.edit_user_button = tk.Button(self.user_manager_window, text="Edit User", font=("Helvetica", 12), command=self.edit_user)
            self.edit_user_button.pack(pady=5)
            
            self.delete_user_button = tk.Button(self.user_manager_window, text="Delete User", font=("Helvetica", 12), command=self.delete_user)
            self.delete_user_button.pack(pady=5)
            
        else:
            self.user_manager_window.lift()
    

    def add_user(self):
        new_username = simpledialog.askstring("Add User", "Enter a new username:")
        if new_username is not None:
            if new_username in self.users:
                messagebox.showerror("Error", "Username already exists. Please choose a different username.")
            else:
                user_balance = simpledialog.askfloat("Add User", f"Enter initial balance for '{new_username}':",
                                                     minvalue=0.0, maxvalue=99999.0)
                if user_balance is not None:
                    with self.db_connection:
                        self.db_connection.execute(
                            "INSERT INTO users (username, balance) VALUES (?, ?)",
                            (new_username, user_balance)
                        )
                    self.users[new_username] = {"balance": user_balance, "purchases": []}
                    self.update_user_buttons()  # Update the user buttons
                    self.user_listbox.insert(tk.END, new_username)

    def update_user_buttons(self):
        for button in self.user_buttons_frame.winfo_children():
            button.destroy()

        for username in self.users:
            user_button = tk.Button(self.user_buttons_frame, text=username, font=("Helvetica", 14), padx=20, pady=10,
                                    command=lambda u=username: self.select_user(u))
            user_button.pack(side=tk.LEFT, padx=10)

    def edit_user(self):
        selected_user = self.user_listbox.get(tk.ACTIVE)
        if selected_user:
            edit_window = tk.Toplevel(self.user_manager_window)
            edit_window.title("Edit User")
            
            balance_button = tk.Button(edit_window, text="Change Balance", font=("Helvetica", 12),
                                       command=lambda: self.change_balance(selected_user))
            balance_button.pack(pady=10)
            
            username_button = tk.Button(edit_window, text="Change Username", font=("Helvetica", 12),
                                        command=lambda: self.change_username(selected_user))
            username_button.pack(pady=10)
    
    def change_balance(self, selected_user):
        new_balance = simpledialog.askfloat("Edit User", f"Enter a new balance for '{selected_user}':",
                                            minvalue=0.0, maxvalue=99999.0)
        if new_balance is not None:
            with self.db_connection:
                self.db_connection.execute(
                    "UPDATE users SET balance = ? WHERE username = ?",
                    (new_balance, selected_user)
                )
            self.users[selected_user]["balance"] = new_balance
            self.update_balance_label()
    
    def change_username(self, selected_user):
        new_username = simpledialog.askstring("Edit User", f"Enter a new username for '{selected_user}':")
        if new_username is not None:
            if new_username in self.users:
                messagebox.showerror("Error", "Username already exists. Please choose a different username.")
            else:
                with self.db_connection:
                    self.db_connection.execute(
                        "UPDATE users SET username = ? WHERE username = ?",
                        (new_username, selected_user)
                    )
                self.users[new_username] = self.users[selected_user]
                del self.users[selected_user]
                self.user_listbox.delete(tk.ACTIVE)
                self.user_listbox.insert(tk.END, new_username)
                
            
    def add_money(self):
        if self.current_user:
            self.users[self.current_user]["balance"] += 0.5
            with self.db_connection:
                self.db_connection.execute(
                    "UPDATE users SET balance = ? WHERE username = ?",
                    (self.users[self.current_user]["balance"], self.current_user)
                )
            self.update_balance_label()

    def delete_user(self):
        selected_user = self.user_listbox.get(tk.ACTIVE)
        if selected_user:
            confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete user '{selected_user}'?")
            if confirm:
                with self.db_connection:
                    self.db_connection.execute("DELETE FROM users WHERE username = ?", (selected_user,))
                del self.users[selected_user]
                self.user_listbox.delete(tk.ACTIVE)
                
    def create_keyboard(self):
        keyboard_frame = tk.Frame(self.user_interface_frame)
        keyboard_frame.pack()

        qwertz_keyboard = [
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
            ["q", "w", "e", "r", "t", "z", "u", "i", "o", "p"],
            ["a", "s", "d", "f", "g", "h", "j", "k", "l", "ö"],
            ["^", "y", "x", "c", "v", "b", "n", "m", ",", "-"],
            ["Shift", "Space", "Backspace"]
        ]

        for row in qwertz_keyboard:
            key_row = tk.Frame(keyboard_frame)
            key_row.pack()
            for key in row:
                key_button = tk.Button(key_row, text=key, font=("Helvetica", 14), padx=10, pady=5,
                                       command=lambda k=key: self.handle_keyboard_press(k))
                key_button.pack(side=tk.LEFT, padx=2, pady=2)

    def handle_keyboard_press(self, key):
        if key == "Space":
            key = " "
        elif key == "Backspace":
            self.text_entry.delete(len(self.text_entry.get()) - 1, tk.END)
            return
        elif key == "Shift":
            # Implement Shift key functionality
            return

        current_text = self.text_entry.get()
        self.text_entry.delete(0, tk.END)
        self.text_entry.insert(0, current_text + key)
    
    def add_money(self):
        if self.current_user:
            self.users[self.current_user]["balance"] += 0.5
            with self.db_connection:
                self.db_connection.execute(
                    "UPDATE users SET balance = ? WHERE username = ?",
                    (self.users[self.current_user]["balance"], self.current_user)
                )
            self.update_balance_label()
    
    def return_money(self):
        if self.current_user:
            user_balance = self.users[self.current_user]["balance"]
            if user_balance > 0:
                messagebox.showinfo("Money Returned", f"Returned ${user_balance:.2f}")
                self.users[self.current_user]["balance"] = 0
                with self.db_connection:
                    self.db_connection.execute(
                        "UPDATE users SET balance = ? WHERE username = ?",
                        (0, self.current_user)
                    )
                self.update_balance_label()
            else:
                messagebox.showinfo("No Money", "No money to return.")
    
    def purchase(self, drink):
        if self.current_user:
            user_balance = self.users[self.current_user]["balance"]
            drink_price = self.drinks[drink]
            if user_balance >= drink_price:
                self.users[self.current_user]["balance"] -= drink_price
                self.users[self.current_user]["purchases"].append(drink)
                with self.db_connection:
                    self.db_connection.execute(
                        "UPDATE users SET balance = ? WHERE username = ?",
                        (self.users[self.current_user]["balance"], self.current_user)
                    )
                self.update_balance_label()
                self.message_label.config(text=f"Enjoy your {drink}!")
            else:
                self.message_label.config(text="Not enough money to purchase.")
    
    def update_balance_label(self):
        if self.current_user:
            user_balance = self.users[self.current_user]["balance"]
            self.balance_label.config(text=f"Balance: ${user_balance:.2f}")
    
    def update_interface(self):
        self.update_balance_label()
        self.user_manager_button.pack_forget()  # Hide the user manager button
        self.user_buttons_frame.pack_forget()  # Hide the user selection buttons
        self.user_interface_frame.pack(pady=20)
        self.logout_button = tk.Button(self.user_interface_frame, text="Logout", font=("Helvetica", 14), command=self.logout)
        self.logout_button.pack(pady=10)
    
    def logout(self):
        self.current_user = None
        self.logout_button.pack_forget()
        self.user_interface_frame.pack_forget()
        self.user_manager_button.pack(side=tk.TOP, pady=10)  # Show the user manager button
        self.user_buttons_frame.pack(pady=10)  # Show the user selection buttons
    
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        self.db_connection.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = VendingMachineGUI(root)
    app.run()
