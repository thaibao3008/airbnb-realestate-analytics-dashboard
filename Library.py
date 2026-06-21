import pyodbc

class DatabaseManager:
    def __init__(self):
        # Đã thêm chữ 'r' trước chuỗi có chứa dấu \ để fix lỗi SyntaxWarning
        self.conn_str = (
            "Driver={ODBC Driver 17 for SQL Server};"
            r"Server=MICHAEL\MSSQLSERVER01;"
            "Database=LibraryDB;"
            "Trusted_Connection=yes;"
        )
    
    def execute_query(self, query, params=None):
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"\n[Lỗi Database]: {e}")
            return False

    def fetch_data(self, query, params=None):
        try:
            conn = pyodbc.connect(self.conn_str)
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception as e:
            print(f"\n[Lỗi Database]: {e}")
            return []


class BookManager:
    def __init__(self):
        self.db = DatabaseManager()

    def view_all_books(self):
        """Hiển thị danh sách sách"""
        query = "SELECT id, title, author, category, status FROM books"
        books = self.db.fetch_data(query)
        
        if not books:
            print("\nKhông có sách nào trong thư viện hoặc lỗi kết nối.")
            return

        print("\n" + "="*70)
        print("   DANH SÁCH SÁCH TRONG THƯ VIỆN")
        print("="*70)
        
        for book in books:
            trang_thai = "Có sẵn" if book[4] == 'Available' else "Đã mượn"
            print(f"ID: {book[0]:<3} | Tên: {book[1]:<30} | Tác giả: {book[2]:<20} | Trạng thái: [{trang_thai}]")
        print("="*70)

    def add_book(self, title, author, category):
        """Thêm sách theo schema mới (không dùng PublishedYear, thay bằng Category)"""
        query = "INSERT INTO books (title, author, category, status) VALUES (?, ?, ?, 'Available')"
        success = self.db.execute_query(query, (title, author, category))
        if success:
            print(f"\n[Thành công]: Đã thêm sách '{title}' vào hệ thống.")

    def borrow_or_return_book(self, book_id, action):
        """action = 0 (Mượn), action = 1 (Trả)"""
        # Cập nhật query theo tên bảng 'books' và cột 'status', 'id'
        check_query = "SELECT status FROM books WHERE id = ?"
        result = self.db.fetch_data(check_query, (book_id,))
        
        if not result:
            print(f"\n[Lỗi]: Không tìm thấy sách có ID = {book_id}")
            return
            
        current_status = result[0][0]
        if action == 0 and current_status == 'Borrowed':
            print("\n[Cảnh báo]: Sách này đã được mượn rồi!")
            return
        elif action == 1 and current_status == 'Available':
            print("\n[Cảnh báo]: Sách này đang ở trong thư viện, không cần trả!")
            return

        # Xác định trạng thái mới để UPDATE
        new_status = 'Borrowed' if action == 0 else 'Available'
        query = "UPDATE books SET status = ? WHERE id = ?"
        success = self.db.execute_query(query, (new_status, book_id))
        
        if success:
            str_action = "MƯỢN" if action == 0 else "TRẢ"
            print(f"\n[Thành công]: Đã cập nhật trạng thái {str_action} cho sách ID {book_id}.")

    def delete_book(self, book_id):
        """Xóa sách theo schema mới"""
        check_query = "SELECT title FROM books WHERE id = ?"
        result = self.db.fetch_data(check_query, (book_id,))
        
        if not result:
            print(f"\n[Lỗi]: Không tìm thấy sách có ID = {book_id} để xóa.")
            return
            
        title = result[0][0]
        confirm = input(f"Bạn có chắc chắn muốn xóa sách '{title}' (ID: {book_id}) không? (y/n): ").strip().lower()
        
        if confirm == 'y':
            query = "DELETE FROM books WHERE id = ?"
            success = self.db.execute_query(query, (book_id,))
            if success:
                print(f"\n[Thành công]: Đã xóa sách khỏi hệ thống.")
        else:
            print("\nĐã hủy thao tác xóa.")


def main():
    manager = BookManager()
    
    while True:
        print("\n--- HỆ THỐNG QUẢN LÝ SÁCH ---")
        print("1. Xem danh sách")
        print("2. Thêm sách mới")
        print("3. Mượn sách")
        print("4. Trả sách")
        print("5. Xóa sách")
        print("6. Thoát")
        
        choice = input("Nhập lựa chọn của bạn (1-6): ").strip()
        
        if choice == '1':
            manager.view_all_books()
        elif choice == '2':
            title = input("Tên sách: ").strip()
            author = input("Tác giả: ").strip()
            category = input("Thể loại (Ví dụ: Fiction, Tech...): ").strip()
            manager.add_book(title, author, category)
        elif choice == '3':
            bid = input("Nhập ID sách muốn MƯỢN: ").strip()
            if bid.isdigit():
                manager.borrow_or_return_book(int(bid), action=0)
            else:
                print("[Lỗi]: ID phải là số!")
        elif choice == '4':
            bid = input("Nhập ID sách muốn TRẢ: ").strip()
            if bid.isdigit():
                manager.borrow_or_return_book(int(bid), action=1)
            else:
                print("[Lỗi]: ID phải là số!")
        elif choice == '5':
            bid = input("Nhập ID sách muốn XÓA: ").strip()
            if bid.isdigit():
                manager.delete_book(int(bid))
            else:
                print("[Lỗi]: ID phải là số!")
        elif choice == '6':
            print("Đang thoát chương trình...")
            break
        else:
            print("Lựa chọn không hợp lệ, vui lòng thử lại.")

if __name__ == "__main__":
    main()