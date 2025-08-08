import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import datetime
import shutil

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("INGENIERIA Y SERVICIOS COLHER - Sistema de Inventario")
        self.root.geometry("1000x700")
        self.setup_icons()
        self.create_db()
        self.current_user = None
        self.is_admin = False
        self.show_database = False
        
        # Logo
        self.logo_label = tk.Label(root, text="INGENIERIA Y SERVICIOS COLHER", 
                                  font=("Helvetica", 20, "bold"), fg="blue")
        self.logo_label.pack(pady=10)
        
        # Frame principal
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.show_login_screen()
    
    def setup_icons(self):
        # Iconos básicos (en un sistema real, cargarías imágenes)
        self.add_icon = "➕"
        self.delete_icon = "❌"
        self.view_icon = "👁️"
        self.hide_icon = "🙈"
    
    def create_db(self):
        self.conn = sqlite3.connect('inventory.db')
        self.c = self.conn.cursor()
        
        # Tabla de usuarios
        self.c.execute('''CREATE TABLE IF NOT EXISTS users
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         username TEXT UNIQUE,
                         password TEXT,
                         is_admin INTEGER DEFAULT 0)''')
        
        # Tabla de herramientas
        self.c.execute('''CREATE TABLE IF NOT EXISTS tools
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         name TEXT,
                         type TEXT,
                         quantity REAL,
                         unit TEXT,
                         status TEXT,
                         location TEXT,
                         user TEXT,
                         observation TEXT,
                         photo_path TEXT,
                         last_update TEXT)''')
        
        # Tabla de materiales
        self.c.execute('''CREATE TABLE IF NOT EXISTS materials
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         name TEXT,
                         type TEXT,
                         quantity REAL,
                         unit TEXT,
                         status TEXT,
                         location TEXT,
                         user TEXT,
                         observation TEXT,
                         photo_path TEXT,
                         last_update TEXT)''')
        
        # Crear usuario admin si no existe
        self.c.execute("SELECT * FROM users WHERE username='admin'")
        if not self.c.fetchone():
            self.c.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
                          ('admin', 'admin123', 1))
            self.conn.commit()
    
    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def show_login_screen(self):
        self.clear_frame()
        self.current_user = None
        self.is_admin = False
        
        login_frame = tk.Frame(self.main_frame)
        login_frame.pack(pady=50)
        
        tk.Label(login_frame, text="Usuario:").grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = tk.Entry(login_frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(login_frame, text="Contraseña:").grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        login_btn = tk.Button(login_frame, text="Ingresar", command=self.login)
        login_btn.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Solo muestra el botón de registro si no hay usuarios (excepto admin)
        self.c.execute("SELECT COUNT(*) FROM users WHERE username != 'admin'")
        if self.c.fetchone()[0] == 0:
            register_btn = tk.Button(login_frame, text="Registrar primer usuario", command=self.show_register_screen)
            register_btn.grid(row=3, column=0, columnspan=2, pady=5)
    
    def show_register_screen(self):
        self.clear_frame()
        
        register_frame = tk.Frame(self.main_frame)
        register_frame.pack(pady=50)
        
        tk.Label(register_frame, text="Nuevo Usuario:").grid(row=0, column=0, padx=5, pady=5)
        self.new_username_entry = tk.Entry(register_frame)
        self.new_username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(register_frame, text="Contraseña:").grid(row=1, column=0, padx=5, pady=5)
        self.new_password_entry = tk.Entry(register_frame, show="*")
        self.new_password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(register_frame, text="Confirmar Contraseña:").grid(row=2, column=0, padx=5, pady=5)
        self.confirm_password_entry = tk.Entry(register_frame, show="*")
        self.confirm_password_entry.grid(row=2, column=1, padx=5, pady=5)
        
        register_btn = tk.Button(register_frame, text="Registrar", command=self.register_user)
        register_btn.grid(row=3, column=0, columnspan=2, pady=10)
        
        back_btn = tk.Button(register_frame, text="Volver al login", command=self.show_login_screen)
        back_btn.grid(row=4, column=0, columnspan=2, pady=5)
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Usuario y contraseña son requeridos")
            return
        
        self.c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = self.c.fetchone()
        
        if user:
            self.current_user = username
            self.is_admin = user[3] == 1
            self.show_main_menu()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
    
    def register_user(self):
        username = self.new_username_entry.get()
        password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Usuario y contraseña son requeridos")
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
        
        try:
            self.c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            self.conn.commit()
            messagebox.showinfo("Éxito", "Usuario registrado correctamente")
            self.show_login_screen()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "El usuario ya existe")
    
    def show_main_menu(self):
        self.clear_frame()
        
        # Menú superior
        menu_frame = tk.Frame(self.main_frame)
        menu_frame.pack(fill=tk.X, padx=10, pady=10)
        
        user_label = tk.Label(menu_frame, text=f"Usuario: {self.current_user}", font=("Helvetica", 10))
        user_label.pack(side=tk.LEFT)
        
        if self.is_admin:
            manage_users_btn = tk.Button(menu_frame, text="Administrar Usuarios", command=self.manage_users)
            manage_users_btn.pack(side=tk.LEFT, padx=5)
        
        db_toggle_btn = tk.Button(menu_frame, text="Mostrar Base de Datos", command=self.toggle_database_view)
        db_toggle_btn.pack(side=tk.LEFT, padx=5)
        
        logout_btn = tk.Button(menu_frame, text="Cerrar Sesión", command=self.show_login_screen)
        logout_btn.pack(side=tk.RIGHT)
        
        # Botones principales
        buttons_frame = tk.Frame(self.main_frame)
        buttons_frame.pack(pady=50)
        
        tools_btn = tk.Button(buttons_frame, text="Gestión de Herramientas", 
                             command=lambda: self.show_inventory_screen("tools"), height=3, width=20)
        tools_btn.grid(row=0, column=0, padx=20, pady=10)
        
        materials_btn = tk.Button(buttons_frame, text="Gestión de Materiales", 
                                command=lambda: self.show_inventory_screen("materials"), height=3, width=20)
        materials_btn.grid(row=0, column=1, padx=20, pady=10)
        
        # Área de la base de datos (inicialmente oculta)
        self.db_frame = tk.Frame(self.main_frame)
        self.db_notebook = ttk.Notebook(self.db_frame)
        
        self.tools_tree = ttk.Treeview(self.db_notebook)
        self.setup_treeview(self.tools_tree, "tools")
        self.db_notebook.add(self.tools_tree, text="Herramientas")
        
        self.materials_tree = ttk.Treeview(self.db_notebook)
        self.setup_treeview(self.materials_tree, "materials")
        self.db_notebook.add(self.materials_tree, text="Materiales")
        
        self.users_tree = ttk.Treeview(self.db_notebook)
        self.setup_treeview(self.users_tree, "users")
        self.db_notebook.add(self.users_tree, text="Usuarios")
        
        self.db_notebook.pack(fill=tk.BOTH, expand=True)
    
    def toggle_database_view(self):
        self.show_database = not self.show_database
        
        if self.show_database:
            self.refresh_database_view()
            self.db_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        else:
            self.db_frame.pack_forget()
    
    def refresh_database_view(self):
        # Actualizar vista de herramientas
        self.tools_tree.delete(*self.tools_tree.get_children())
        self.c.execute("SELECT * FROM tools")
        for row in self.c.fetchall():
            self.tools_tree.insert("", tk.END, values=row)
        
        # Actualizar vista de materiales
        self.materials_tree.delete(*self.materials_tree.get_children())
        self.c.execute("SELECT * FROM materials")
        for row in self.c.fetchall():
            self.materials_tree.insert("", tk.END, values=row)
        
        # Actualizar vista de usuarios (solo para admin)
        self.users_tree.delete(*self.users_tree.get_children())
        if self.is_admin:
            self.c.execute("SELECT * FROM users")
            for row in self.c.fetchall():
                self.users_tree.insert("", tk.END, values=row)
    
    def setup_treeview(self, tree, table):
        if table == "tools":
            tree["columns"] = ("ID", "Nombre", "Tipo", "Cantidad", "Unidad", "Estado", "Ubicación", 
                             "Usuario", "Observación", "Foto", "Actualizado")
            tree.column("#0", width=0, stretch=tk.NO)
            for i, col in enumerate(tree["columns"]):
                tree.column(col, width=80, anchor=tk.W)
                tree.heading(col, text=col)
        
        elif table == "materials":
            tree["columns"] = ("ID", "Nombre", "Tipo", "Cantidad", "Unidad", "Estado", "Ubicación", 
                              "Usuario", "Observación", "Foto", "Actualizado")
            tree.column("#0", width=0, stretch=tk.NO)
            for i, col in enumerate(tree["columns"]):
                tree.column(col, width=80, anchor=tk.W)
                tree.heading(col, text=col)
        
        elif table == "users":
            tree["columns"] = ("ID", "Usuario", "Contraseña", "Admin")
            tree.column("#0", width=0, stretch=tk.NO)
            for i, col in enumerate(tree["columns"]):
                tree.column(col, width=100, anchor=tk.W)
                tree.heading(col, text=col)
    
    def manage_users(self):
        if not self.is_admin:
            return
        
        self.clear_frame()
        
        # Título
        tk.Label(self.main_frame, text="Administración de Usuarios", font=("Helvetica", 16)).pack(pady=10)
        
        # Treeview de usuarios
        users_tree = ttk.Treeview(self.main_frame)
        users_tree["columns"] = ("ID", "Usuario", "Es Admin")
        users_tree.column("#0", width=0, stretch=tk.NO)
        users_tree.column("ID", width=50, anchor=tk.W)
        users_tree.column("Usuario", width=150, anchor=tk.W)
        users_tree.column("Es Admin", width=80, anchor=tk.W)
        
        users_tree.heading("ID", text="ID")
        users_tree.heading("Usuario", text="Usuario")
        users_tree.heading("Es Admin", text="Es Admin")
        
        self.c.execute("SELECT id, username, is_admin FROM users WHERE username != ?", (self.current_user,))
        for row in self.c.fetchall():
            users_tree.insert("", tk.END, values=row)
        
        users_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Botones de acción
        buttons_frame = tk.Frame(self.main_frame)
        buttons_frame.pack(pady=10)
        
        add_btn = tk.Button(buttons_frame, text="Agregar Usuario", command=lambda: self.add_edit_user())
        add_btn.grid(row=0, column=0, padx=5)
        
        edit_btn = tk.Button(buttons_frame, text="Editar Usuario", 
                           command=lambda: self.add_edit_user(users_tree))
        edit_btn.grid(row=0, column=1, padx=5)
        
        delete_btn = tk.Button(buttons_frame, text="Eliminar Usuario", 
                              command=lambda: self.delete_user(users_tree))
        delete_btn.grid(row=0, column=2, padx=5)
        
        back_btn = tk.Button(buttons_frame, text="Volver al Menú", command=self.show_main_menu)
        back_btn.grid(row=0, column=3, padx=5)
    
    def add_edit_user(self, tree=None):
        selected = tree.focus() if tree else None
        user_data = tree.item(selected, "values") if selected else None
        
        popup = tk.Toplevel(self.root)
        popup.title("Agregar/Editar Usuario")
        popup.geometry("400x300")
        
        tk.Label(popup, text="Usuario:").pack(pady=(20, 5))
        username_entry = tk.Entry(popup)
        username_entry.pack(pady=5)
        
        tk.Label(popup, text="Contraseña:").pack(pady=5)
        password_entry = tk.Entry(popup, show="*")
        password_entry.pack(pady=5)
        
        is_admin_var = tk.IntVar()
        tk.Checkbutton(popup, text="Es Administrador", variable=is_admin_var).pack(pady=5)
        
        if user_data:
            username_entry.insert(0, user_data[1])
            is_admin_var.set(int(user_data[2]))
        
        def save_user():
            username = username_entry.get()
            password = password_entry.get()
            is_admin = is_admin_var.get()
            
            if not username:
                messagebox.showerror("Error", "El usuario es requerido")
                return
            
            try:
                if user_data:  # Editar
                    if password:
                        self.c.execute("UPDATE users SET username=?, password=?, is_admin=? WHERE id=?",
                                     (username, password, is_admin, user_data[0]))
                    else:
                        self.c.execute("UPDATE users SET username=?, is_admin=? WHERE id=?",
                                     (username, is_admin, user_data[0]))
                else:  # Nuevo
                    if not password:
                        messagebox.showerror("Error", "La contraseña es requerida para nuevos usuarios")
                        return
                    
                    self.c.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
                                 (username, password, is_admin))
                
                self.conn.commit()
                popup.destroy()
                self.manage_users()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "El usuario ya existe")
        
        save_btn = tk.Button(popup, text="Guardar", command=save_user)
        save_btn.pack(pady=20)
    
    def delete_user(self, tree):
        selected = tree.focus()
        if not selected:
            messagebox.showerror("Error", "Seleccione un usuario")
            return
        
        user_data = tree.item(selected, "values")
        if messagebox.askyesno("Confirmar", f"¿Eliminar al usuario {user_data[1]}?"):
            self.c.execute("DELETE FROM users WHERE id=?", (user_data[0],))
            self.conn.commit()
            self.manage_users()
    
    def show_inventory_screen(self, inventory_type):
        self.clear_frame()
        
        # Título
        title = "Herramientas" if inventory_type == "tools" else "Materiales"
        tk.Label(self.main_frame, text=f"Gestión de {title}", font=("Helvetica", 16)).pack(pady=10)
        
        # Frame de búsqueda/filtro
        search_frame = tk.Frame(self.main_frame)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT)
        search_entry = tk.Entry(search_frame)
        search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        search_btn = tk.Button(search_frame, text="Buscar", 
                             command=lambda: self.search_inventory(inventory_type, search_entry.get()))
        search_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(search_frame, text="Mostrar Todo", 
                            command=lambda: self.search_inventory(inventory_type, ""))
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Treeview de items
        self.inventory_tree = ttk.Treeview(self.main_frame)
        columns = ("ID", "Nombre", "Tipo", "Cantidad", "Unidad", "Estado", "Ubicación", 
                  "Usuario", "Observación", "Foto", "Actualizado")
        self.inventory_tree["columns"] = columns
        
        self.inventory_tree.column("#0", width=0, stretch=tk.NO)
        for col in columns:
            self.inventory_tree.column(col, width=100, anchor=tk.W)
            self.inventory_tree.heading(col, text=col)
        
        self.inventory_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Botones de acción
        buttons_frame = tk.Frame(self.main_frame)
        buttons_frame.pack(pady=10)
        
        add_btn = tk.Button(buttons_frame, text="Agregar", 
                          command=lambda: self.add_edit_inventory_item(inventory_type))
        add_btn.grid(row=0, column=0, padx=5)
        
        edit_btn = tk.Button(buttons_frame, text="Editar", 
                           command=lambda: self.add_edit_inventory_item(inventory_type, self.inventory_tree))
        edit_btn.grid(row=0, column=1, padx=5)
        
        delete_btn = tk.Button(buttons_frame, text="Eliminar", 
                             command=lambda: self.delete_inventory_item(inventory_type, self.inventory_tree))
        delete_btn.grid(row=0, column=2, padx=5)
        
        view_photo_btn = tk.Button(buttons_frame, text="Ver Foto", 
                                 command=lambda: self.view_photo(inventory_type, self.inventory_tree))
        view_photo_btn.grid(row=0, column=3, padx=5)
        
        back_btn = tk.Button(buttons_frame, text="Volver al Menú", command=self.show_main_menu)
        back_btn.grid(row=0, column=4, padx=5)
        
        # Cargar datos iniciales
        self.search_inventory(inventory_type, "")
    
    def search_inventory(self, inventory_type, search_term):
        self.inventory_tree.delete(*self.inventory_tree.get_children())
        
        query = f"SELECT * FROM {inventory_type} WHERE name LIKE ? OR type LIKE ? OR user LIKE ?"
        params = (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%")
        
        self.c.execute(query, params)
        for row in self.c.fetchall():
            self.inventory_tree.insert("", tk.END, values=row)
    
    def add_edit_inventory_item(self, inventory_type, tree=None):
        selected = tree.focus() if tree else None
        item_data = tree.item(selected, "values") if selected else None
        
        popup = tk.Toplevel(self.root)
        popup.title(f"{'Editar' if item_data else 'Agregar'} {'Herramienta' if inventory_type == 'tools' else 'Material'}")
        popup.geometry("500x600")
        
        # Campos del formulario
        fields = [
            ("Nombre:", "name"),
            ("Tipo:", "type"),
            ("Cantidad:", "quantity"),
            ("Unidad (kg/unidad):", "unit"),
            ("Estado:", "status"),
            ("Ubicación:", "location"),
            ("Usuario asignado:", "user"),
            ("Observación:", "observation")
        ]
        
        entries = {}
        for i, (label, field) in enumerate(fields):
            tk.Label(popup, text=label).grid(row=i, column=0, padx=10, pady=5, sticky=tk.E)
            entry = tk.Entry(popup)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky=tk.W+tk.E)
            entries[field] = entry
            
            if item_data:
                entry.insert(0, item_data[fields.index((label, field)) + 1])
        
        # Foto
        self.photo_path = item_data[9] if item_data else ""
        tk.Label(popup, text="Foto:").grid(row=len(fields), column=0, padx=10, pady=5, sticky=tk.E)
        
        photo_btn_frame = tk.Frame(popup)
        photo_btn_frame.grid(row=len(fields), column=1, padx=10, pady=5, sticky=tk.W)
        
        add_photo_btn = tk.Button(photo_btn_frame, text="Seleccionar Foto", 
                                command=lambda: self.select_photo(popup, photo_label))
        add_photo_btn.pack(side=tk.LEFT)
        
        clear_photo_btn = tk.Button(photo_btn_frame, text="Quitar Foto", 
                                  command=lambda: self.clear_photo(photo_label))
        clear_photo_btn.pack(side=tk.LEFT, padx=5)
        
        photo_label = tk.Label(popup)
        photo_label.grid(row=len(fields)+1, column=0, columnspan=2, pady=5)
        
        if item_data and item_data[9]:
            self.display_photo(photo_label, item_data[9])
        
        def save_item():
            data = {field: entry.get() for field, entry in entries.items()}
            
            if not data["name"]:
                messagebox.showerror("Error", "El nombre es requerido")
                return
            
            try:
                data["quantity"] = float(data["quantity"])
            except ValueError:
                messagebox.showerror("Error", "La cantidad debe ser un número")
                return
            
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            try:
                if item_data:  # Editar
                    self.c.execute(f"""UPDATE {inventory_type} SET 
                                    name=?, type=?, quantity=?, unit=?, status=?, 
                                    location=?, user=?, observation=?, photo_path=?, last_update=?
                                    WHERE id=?""",
                                 (data["name"], data["type"], data["quantity"], data["unit"], 
                                  data["status"], data["location"], data["user"], 
                                  data["observation"], self.photo_path, now, item_data[0]))
                else:  # Nuevo
                    self.c.execute(f"""INSERT INTO {inventory_type} 
                                    (name, type, quantity, unit, status, location, 
                                     user, observation, photo_path, last_update)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                 (data["name"], data["type"], data["quantity"], data["unit"], 
                                  data["status"], data["location"], data["user"], 
                                  data["observation"], self.photo_path, now))
                
                self.conn.commit()
                popup.destroy()
                self.search_inventory(inventory_type, "")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")
        
        save_btn = tk.Button(popup, text="Guardar", command=save_item)
        save_btn.grid(row=len(fields)+2, column=0, columnspan=2, pady=20)
    
    def select_photo(self, popup, photo_label):
        file_path = filedialog.askopenfilename(
            title="Seleccionar foto",
            filetypes=(("Imágenes", "*.jpg *.jpeg *.png"), ("Todos los archivos", "*.*"))
        )
        
        if file_path:
            # Crear directorio para fotos si no existe
            if not os.path.exists("inventory_photos"):
                os.makedirs("inventory_photos")
            
            # Copiar foto al directorio con nombre único
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            ext = os.path.splitext(file_path)[1]
            new_filename = f"photo_{timestamp}{ext}"
            new_path = os.path.join("inventory_photos", new_filename)
            
            shutil.copy(file_path, new_path)
            self.photo_path = new_path
            self.display_photo(photo_label, new_path)
    
    def clear_photo(self, photo_label):
        self.photo_path = ""
        photo_label.config(image="")
        photo_label.image = None
    
    def display_photo(self, label, photo_path):
        try:
            image = Image.open(photo_path)
            image.thumbnail((200, 200))
            photo = ImageTk.PhotoImage(image)
            label.config(image=photo)
            label.image = photo
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen: {str(e)}")
    
    def view_photo(self, inventory_type, tree):
        selected = tree.focus()
        if not selected:
            messagebox.showerror("Error", "Seleccione un item")
            return
        
        item_data = tree.item(selected, "values")
        if not item_data[9]:
            messagebox.showinfo("Info", "Este item no tiene foto asociada")
            return
        
        photo_window = tk.Toplevel(self.root)
        photo_window.title(f"Foto de {item_data[1]}")
        
        try:
            image = Image.open(item_data[9])
            photo = ImageTk.PhotoImage(image)
            
            label = tk.Label(photo_window, image=photo)
            label.image = photo
            label.pack()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen: {str(e)}")
            photo_window.destroy()
    
    def delete_inventory_item(self, inventory_type, tree):
        selected = tree.focus()
        if not selected:
            messagebox.showerror("Error", "Seleccione un item")
            return
        
        item_data = tree.item(selected, "values")
        if messagebox.askyesno("Confirmar", f"¿Eliminar {'la herramienta' if inventory_type == 'tools' else 'el material'} {item_data[1]}?"):
            self.c.execute(f"DELETE FROM {inventory_type} WHERE id=?", (item_data[0],))
            self.conn.commit()
            self.search_inventory(inventory_type, "")

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()