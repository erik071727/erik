import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os

# ------------------ Класс приложения ------------------
class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("700x500")
        self.root.resizable(False, False)

        # Данные
        self.users = []
        self.favorites = self.load_favorites()

        # Горячие клавиши
        self.root.bind('<Return>', lambda event: self.search_users())

        # Интерфейс
        self.create_widgets()

    # ------------------ Создание GUI ------------------
    def create_widgets(self):
        # Рамка поиска
        search_frame = ttk.Frame(self.root, padding=10)
        search_frame.pack(fill=tk.X)

        ttk.Label(search_frame, text="Введите имя пользователя GitHub:").pack(anchor=tk.W)
        self.search_entry = ttk.Entry(search_frame, width=50)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10), pady=5)
        self.search_button = ttk.Button(search_frame, text="🔍 Найти", command=self.search_users)
        self.search_button.pack(side=tk.LEFT)

        # Разделитель
        ttk.Separator(self.root, orient='horizontal').pack(fill=tk.X, padx=10, pady=5)

        # Рамка списка результатов
        result_frame = ttk.LabelFrame(self.root, text="Результаты поиска", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.result_listbox = tk.Listbox(result_frame, height=10)
        self.result_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_listbox.config(yscrollcommand=scrollbar.set)

        # Кнопки действий с результатами
        btn_frame = ttk.Frame(self.root, padding=10)
        btn_frame.pack(fill=tk.X)

        ttk.Button(btn_frame, text="⭐ Добавить в избранное", command=self.add_to_favorites).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📄 Показать избранное", command=self.show_favorites).pack(side=tk.LEFT, padx=5)

        # Рамка избранного
        fav_frame = ttk.LabelFrame(self.root, text="Избранные пользователи", padding=10)
        fav_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.fav_listbox = tk.Listbox(fav_frame, height=6)
        self.fav_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        fav_scrollbar = ttk.Scrollbar(fav_frame, orient=tk.VERTICAL, command=self.fav_listbox.yview)
        fav_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.fav_listbox.config(yscrollcommand=fav_scrollbar.set)

        # Кнопки для избранного
        fav_btn_frame = ttk.Frame(self.root, padding=10)
        fav_btn_frame.pack(fill=tk.X)

        ttk.Button(fav_btn_frame, text="❌ Удалить из избранного", command=self.remove_from_favorites).pack(side=tk.LEFT, padx=5)
        ttk.Button(fav_btn_frame, text="💾 Сохранить избранное", command=self.save_favorites).pack(side=tk.LEFT, padx=5)

        # Обновить отображение избранного
        self.update_favorites_list()

    # ------------------ API: поиск пользователей ------------------
    def search_users(self):
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Ошибка ввода", "Поле поиска не может быть пустым!")
            return

        try:
            url = f"https://api.github.com/search/users?q={query}&per_page=20"
            response = requests.get(url)
            if response.status_code != 200:
                messagebox.showerror("Ошибка API", f"Ошибка {response.status_code}: {response.json().get('message', 'Неизвестная ошибка')}")
                return

            data = response.json()
            self.users = data.get('items', [])
            self.result_listbox.delete(0, tk.END)
            for user in self.users:
                self.result_listbox.insert(tk.END, f"{user['login']} (id: {user['id']})")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Сетевая ошибка", str(e))

    # ------------------ Работа с избранным (JSON) ------------------
    def load_favorites(self):
        if os.path.exists("favorites.json"):
            with open("favorites.json", "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def save_favorites(self):
        with open("favorites.json", "w", encoding="utf-8") as f:
            json.dump(self.favorites, f, indent=4, ensure_ascii=False)
        messagebox.showinfo("Сохранено", "Избранное сохранено в favorites.json")

    def add_to_favorites(self):
        selection = self.result_listbox.curselection()
        if not selection:
            messagebox.showwarning("Нет выбора", "Сначала выберите пользователя из результатов поиска.")
            return

        idx = selection[0]
        user = self.users[idx]
        fav_user = {
            "login": user['login'],
            "id": user['id'],
            "html_url": user['html_url'],
            "avatar_url": user['avatar_url']
        }

        # Проверка, не добавлен ли уже
        if any(f['id'] == fav_user['id'] for f in self.favorites):
            messagebox.showinfo("Уже в избранном", f"{user['login']} уже есть в избранном.")
            return

        self.favorites.append(fav_user)
        self.update_favorites_list()
        self.save_favorites()
        messagebox.showinfo("Добавлено", f"{user['login']} добавлен в избранное.")

    def remove_from_favorites(self):
        selection = self.fav_listbox.curselection()
        if not selection:
            messagebox.showwarning("Нет выбора", "Сначала выберите пользователя из списка избранного.")
            return

        idx = selection[0]
        removed = self.favorites.pop(idx)
        self.update_favorites_list()
        self.save_favorites()
        messagebox.showinfo("Удалено", f"{removed['login']} удалён из избранного.")

    def update_favorites_list(self):
        self.fav_listbox.delete(0, tk.END)
        for fav in self.favorites:
            self.fav_listbox.insert(tk.END, f"{fav['login']} (id: {fav['id']})")

    def show_favorites(self):
        if not self.favorites:
            messagebox.showinfo("Избранное", "Список избранных пользователей пуст.")
        else:
            fav_names = "\n".join([f"{fav['login']} — {fav['html_url']}" for fav in self.favorites])
            messagebox.showinfo("Избранное", fav_names)

# ------------------ Запуск приложения ------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()