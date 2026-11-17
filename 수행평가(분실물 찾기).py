
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import date

# 데이터베이스 생성 및 연결
conn = sqlite3.connect("lost_found.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    place TEXT NOT NULL,
    found_date TEXT NOT NULL,
    status TEXT DEFAULT '보관 중'
)
""")
conn.commit()

# 메인 창 설정
root = tk.Tk()
root.title("우리 학교 분실물 관리 프로그램")
root.geometry("750x550")

# 제목
title = tk.Label(
    root,
    text="우리 학교 분실물 찾기",
    font=("맑은 고딕", 22, "bold")
)
title.pack(pady=15)

# 입력 영역
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

tk.Label(input_frame, text="물건 이름").grid(row=0, column=0, padx=5)
name_entry = tk.Entry(input_frame, width=20)
name_entry.grid(row=0, column=1, padx=5)

tk.Label(input_frame, text="발견 장소").grid(row=0, column=2, padx=5)
place_entry = tk.Entry(input_frame, width=20)
place_entry.grid(row=0, column=3, padx=5)

# 분실물 등록 기능
def add_item():
    name = name_entry.get().strip()
    place = place_entry.get().strip()

    if not name or not place:
        messagebox.showwarning("입력 오류", "모든 정보를 입력하세요.")
        return

    cursor.execute(
        "INSERT INTO items (name, place, found_date) VALUES (?, ?, ?)",
        (name, place, date.today().isoformat())
    )
    conn.commit()

    name_entry.delete(0, tk.END)
    place_entry.delete(0, tk.END)

    show_items()
    messagebox.showinfo("등록 완료", "분실물이 등록되었습니다.")

# 분실물 조회 기능
def show_items():
    for row in tree.get_children():
        tree.delete(row)

    cursor.execute(
        "SELECT * FROM items ORDER BY id DESC"
    )

    for item in cursor.fetchall():
        tree.insert("", tk.END, values=item)

# 분실물 검색 기능
def search_item():
    keyword = search_entry.get().strip()

    for row in tree.get_children():
        tree.delete(row)

    cursor.execute(
        "SELECT * FROM items WHERE name LIKE ? ORDER BY id DESC",
        ('%' + keyword + '%',)
    )

    for item in cursor.fetchall():
        tree.insert("", tk.END, values=item)

# 반환 처리 기능
def return_item():
    selected = tree.selection()

    if not selected:
        messagebox.showwarning("선택 오류", "물건을 선택하세요.")
        return

    item_id = tree.item(selected[0])["values"][0]

    cursor.execute(
        "UPDATE items SET status = '반환 완료' WHERE id = ?",
        (item_id,)
    )
    conn.commit()

    show_items()
    messagebox.showinfo("처리 완료", "반환 처리가 완료되었습니다.")

# 분실물 삭제 기능
def delete_item():
    selected = tree.selection()

    if not selected:
        messagebox.showwarning("선택 오류", "삭제할 물건을 선택하세요.")
        return

    item_id = tree.item(selected[0])["values"][0]

    if messagebox.askyesno("삭제 확인", "정말 삭제하시겠습니까?"):
        cursor.execute(
            "DELETE FROM items WHERE id = ?",
            (item_id,)
        )
        conn.commit()
        show_items()

# 버튼 영역
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(
    button_frame, text="분실물 등록",
    command=add_item, width=15
).grid(row=0, column=0, padx=5)

tk.Button(
    button_frame, text="반환 처리",
    command=return_item, width=15
).grid(row=0, column=1, padx=5)

tk.Button(
    button_frame, text="분실물 삭제",
    command=delete_item, width=15
).grid(row=0, column=2, padx=5)

tk.Button(
    button_frame, text="전체 목록",
    command=show_items, width=15
).grid(row=0, column=3, padx=5)

# 검색 영역
search_frame = tk.Frame(root)
search_frame.pack(pady=10)

tk.Label(search_frame, text="물건 검색").pack(side=tk.LEFT)

search_entry = tk.Entry(search_frame, width=30)
search_entry.pack(side=tk.LEFT, padx=5)

tk.Button(
    search_frame, text="검색",
    command=search_item
).pack(side=tk.LEFT)

# 분실물 목록 표
columns = ("번호", "물건 이름", "발견 장소", "등록 날짜", "상태")

tree = ttk.Treeview(
    root,
    columns=columns,
    show="headings",
    height=12
)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=130, anchor="center")

tree.pack(pady=15, padx=10, fill=tk.BOTH, expand=True)

# 프로그램 실행
show_items()

def close_program():
    conn.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", close_program)
root.mainloop()
