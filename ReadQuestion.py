import tkinter as tk
from tkinter import filedialog, messagebox
import json
import re
import html

# Danh sách lưu các file đã chọn (đường dẫn)
selected_files = []

def clean_html(text):
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    return text.strip()

def process_test_question(question_obj, processed_ids):
    question_id = question_obj.get("id")
    if question_id is not None:
        if question_id in processed_ids:
            return ""
        processed_ids.add(question_id)
    
    question_text = question_obj.get("question_direction", "")
    cleaned_question = clean_html(question_text)
    
    answer_options = question_obj.get("answer_option", [])
    cleaned_answers = []
    for opt in answer_options:
        ans_text = opt.get("value", "")
        cleaned_ans = clean_html(ans_text)
        cleaned_answers.append(cleaned_ans)
        
    result = ""
    if question_id is not None:
        result += f"ID: {question_id}\n"
    result += f"Câu hỏi: {cleaned_question}\n"
    if cleaned_answers:
        for index, ans in enumerate(cleaned_answers):
            letter = chr(65 + index)  # 65 là mã ASCII của 'A'
            result += f"{letter}. {ans}\n"
    return result.strip()

def process_txt_file(file_path, processed_ids):
    results = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        try:
            data = json.loads(content)
        except Exception:
            results.append("Lỗi: Nội dung file không đúng định dạng JSON.\n")
            return results
        
        questions = []
        if isinstance(data, dict):
            if "test" in data and isinstance(data["test"], list):
                questions = data["test"]
            elif "questions" in data and isinstance(data["questions"], list):
                questions = data["questions"]
            elif "data" in data and isinstance(data["data"], list):
                for element in data["data"]:
                    if isinstance(element, dict) and "test" in element:
                        candidate = element["test"]
                        if isinstance(candidate, list):
                            questions.extend(candidate)
                        elif isinstance(candidate, dict):
                            questions.append(candidate)
        elif isinstance(data, list):
            questions = data

        for q_obj in questions:
            question_output = process_test_question(q_obj, processed_ids)
            if question_output:
                results.append(question_output)
    except Exception as e:
        results.append(f"Lỗi khi xử lý file {file_path}: {e}\n")
    return results

def select_files():
    global selected_files
    files = filedialog.askopenfilenames(
        title="Chọn file TXT chứa dữ liệu",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if files:
        selected_files = list(files)
        lbl_status.config(text=f"Đã chọn {len(selected_files)} file.")
    else:
        selected_files = []
        lbl_status.config(text="Chưa chọn file nào.")

def convert_all():
    if not selected_files:
        messagebox.showinfo("Thông báo", "Bạn chưa chọn file nào!", parent=root)
        return

    files_to_process = selected_files[:15]
    processed_ids = set()
    all_questions = []
    
    for file_path in files_to_process:
        file_questions = process_txt_file(file_path, processed_ids)
        all_questions.extend(file_questions)
    
    if not all_questions:
        messagebox.showinfo("Thông báo", "Không có câu hỏi nào được tạo ra từ các file đã chọn.", parent=root)
        return
    final_output = ""
    for idx, question_text in enumerate(all_questions, start=1):
        lines = question_text.splitlines()
        new_lines = []
        for line in lines:
            if line.startswith("Câu hỏi:"):
                content = line[len("Câu hỏi:"):].lstrip()
                new_lines.append(f"Câu hỏi {idx}: {content}")
            else:
                new_lines.append(line)
        final_output += "\n".join(new_lines) + "\n\n"
    
    output_file = filedialog.asksaveasfilename(
        title="Lưu kết quả vào file TXT",
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        parent=root
    )
    
    if not output_file:
        messagebox.showinfo("Thông báo", "Bạn chưa chọn nơi lưu file kết quả!", parent=root)
        return

    try:
        with open(output_file, "w", encoding="utf-8") as f_out:
            f_out.write(final_output)
        messagebox.showinfo("Thông báo", f"Kết quả đã được lưu vào file:\n{output_file}", parent=root)
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể lưu file: {e}", parent=root)
root = tk.Tk()
root.title("Chuyển đổi JSON sang câu hỏi- 17thedev")
root.geometry("800x600")

btn_select = tk.Button(root, text="Chọn file", command=select_files, font=("Arial", 14), padx=10, pady=5)
btn_select.pack(pady=10)

lbl_status = tk.Label(root, text="Chưa chọn file nào.", font=("Arial", 12))
lbl_status.pack(pady=5)

btn_convert = tk.Button(root, text="Convert tất cả", command=convert_all, font=("Arial", 14), padx=10, pady=5)
btn_convert.pack(pady=20)

root.mainloop()
