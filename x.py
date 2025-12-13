import os

def update_moitruong_file():
    target_file = 'moitruongcu.py'

    # Dictionary chứa các giá trị cần thay thế: "Giá trị sai (mới)" : "Giá trị đúng (cũ)"
    replacements = {
        # --- 1. Constants (Hằng số đầu file) ---
        "0x380B44": "0x37FA34",  # OFFSET_DIACHICOSOTHONGTINGAME
        "0x380AF8": "0x37F9E8",  # OFFSET_DIACHICOSOTHONGTINNHANVAT1
        "0x1BDA60": "0x1BC950",  # OFFSET_DIACHICOSOTHONGTINNHANVATX

        # --- 2. Memory Addresses (Địa chỉ bộ nhớ quan trọng) ---
        "0x372864": "0x371754",  # Base address cho HP/MP/Info
        "0x380B64": "0x37FA54",  # Mouse Hover Character
        "0x1BD4F0": "0x1BC3E0",  # Selected Target Pointer
        "0x37284C": "0x37173C",  # Selected Target ID
        "0x1BD550": "0x1BC440",  # Backup Target Pointer
        "0x1BD554": "0x1BC444",  # Backup Target ID
        "0x380B38": "0x37FA28",  # Alt Key State
        "0x380B7D": "0x37FA6D",  # Left Click State
        "0x3A642C": "0x3A531C",  # Option Window Check
        "0x1C05E0": "0x1BF4D0",  # Effect Mapping

        # --- 3. Assembly Calls (Địa chỉ hàm game) ---
        "0x95450": "0x951C0",    # Execute Command Function
        "0x47790": "0x476A0",    # Move Function
        "0xB400": "0xB3F0",      # Pick Up Function

        # --- 4. Bypass/Disable Addresses (Chặn game ghi đè) ---
        "0x1AFE3": "0x1AF43",    # Delay Attack Pose 1
        "0x1B377": "0x1B2D7",    # Delay Attack Pose 2
        "0xA20F0": "0xA1E30",    # Target Set Disable 1
        "0xA20F8": "0xA1E38",    # Target Set Disable 2
        "0xA20FE": "0xA1E3E",    # Target Set Disable 3
        "0xA2106": "0xA1E46",    # Target Set Disable 4
        "0x9542B": "0x951A5",    # Clear Target Disable 1
        "0x95435": "0x9519B",    # Clear Target Disable 2
        "0x4993C": "0x4984C",    # Long Click Disable
        "0x5416C": "0x5405C",    # Skill Mouse State Disable
    }

    if not os.path.exists(target_file):
        print(f"Lỗi: Không tìm thấy file '{target_file}' trong thư mục hiện tại.")
        return

    print(f"Đang đọc file '{target_file}'...")
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    count = 0

    for old_val, new_val in replacements.items():
        if old_val in content:
            content = content.replace(old_val, new_val)
            print(f"[OK] Đã thay thế: {old_val} -> {new_val}")
            count += 1
        else:
            print(f"[Bỏ qua] Không tìm thấy chuỗi: {old_val}")

    if content != original_content:
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\nHoàn tất! Đã cập nhật {count} địa chỉ trong file '{target_file}'.")
    else:
        print("\nKhông có thay đổi nào được thực hiện (file có thể đã được update trước đó).")

if __name__ == "__main__":
    update_moitruong_file()